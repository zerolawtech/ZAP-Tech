pragma solidity >=0.4.24 <0.5.0;

import "./open-zeppelin/SafeMath.sol";
import "./IssuingEntity.sol";
import "./components/Modular.sol";

/**
	@title Security Token
	@dev
		Expands upon the ERC20 token standard
		https://theethereum.wiki/w/index.php/ERC20_Token_Standard
 */
contract TokenBase is Modular {

	using SafeMath for uint256;

	bytes32 public ownerID;
	IssuingEntity public issuer;

	/* Assets cannot be fractionalized */
	uint8 public constant decimals = 0;
	string public name;
	string public symbol;
	uint256 public totalSupply;
	uint256 public authorizedSupply;

	mapping (address => mapping (address => uint256)) allowed;

	event Transfer(address indexed from, address indexed to, uint tokens);
	event Approval(
		address indexed tokenOwner,
		address indexed spender,
		uint tokens
	);
	event AuthorizedSupplyChanged(uint256 oldAuthorized, uint256 newAuthorized);
	event TotalSupplyChanged(
		address indexed owner,
		uint256 oldBalance,
		uint256 newBalance
	);

	/**
		@notice Security token constructor
		@dev Initially the total supply is credited to the issuer
		@param _issuer Address of the issuer's IssuingEntity contract
		@param _name Name of the token
		@param _symbol Unique ticker symbol
		@param _authorizedSupply Initial authorized token supply
	 */
	constructor(
		address _issuer,
		string _name,
		string _symbol,
		uint256 _authorizedSupply
	)
		public
	{
		issuer = IssuingEntity(_issuer);
		ownerID = issuer.ownerID();
		name = _name;
		symbol = _symbol;
		authorizedSupply = _authorizedSupply;
	}

	/**
		@notice Fetch circulating supply
		@dev Circulating supply = total supply - amount retained by issuer
		@return integer
	 */
	function circulatingSupply() external view returns (uint256) {
		return totalSupply.sub(balanceOf(address(issuer)));
	}

	/**
		@notice Fetch the amount retained by issuer
		@return integer
	 */
	function treasurySupply() external view returns (uint256) {
		return balanceOf(address(issuer));
	}

	function balanceOf(address) public view returns (uint256);

	/**
		@notice Fetch the allowance
		@param _owner Owner of the tokens
		@param _spender Spender of the tokens
		@return integer
	 */
	function allowance(
		address _owner,
		address _spender
	 )
		external
		view
		returns (uint256)
	{
		return allowed[_owner][_spender];
	}

	/**
		@notice ERC-20 approve standard
		@dev
			Approval may be given to addresses that are not registered,
			but the address will not be able to call transferFrom()
		@param _spender Address being approved to transfer tokens
		@param _value Amount approved for transfer
		@return bool success
	 */
	function approve(address _spender, uint256 _value) external returns (bool) {
		require(_spender != address(this));
		require(_value == 0 || allowed[msg.sender][_spender] == 0);
		allowed[msg.sender][_spender] = _value;
		emit Approval(msg.sender, _spender, _value);
		return true;
	}

	/**
		@notice Modify authorized Supply
		@dev Callable by issuer or via module
		@param _value New authorized supply value
		@return bool
	 */
	function modifyAuthorizedSupply(uint256 _value) external returns (bool) {
		/* msg.sig = 0xc39f42ed */
		if (!_checkPermitted()) return false;
		require(_value >= totalSupply);
		/* bytes4 signature for token module modifyAuthorizedSupply() */
		_callModules(
			0xb1a1a455,
			0x00,
			abi.encode(address(this), totalSupply, _value)
		);
		emit AuthorizedSupplyChanged(totalSupply, _value);
		authorizedSupply = _value;
		return true;
	}

	/**
		@notice Internal shared logic for minting and burning
		@param _owner Owner of the tokens
		@param _old Previous balance
		@return bool success
	 */
	function _modifyTotalSupply(
		address _owner,
		uint256 _old
	)
		internal
		returns (bool)
	{
		uint256 _new = balanceOf(_owner);
		(
			bytes32 _id,
			uint8 _rating,
			uint16 _country
		) = issuer.modifyTokenTotalSupply(_owner, _old, _new);
		/* bytes4 signature for token module totalSupplyChanged() */
		_callModules(
			0x741b5078,
			0x00,
			abi.encode(_owner, _id, _rating, _country, _old, _new)
		);
		emit TotalSupplyChanged(_owner, _old, _new);
		return true;
	}

	/**
		@notice Attach a security token module
		@dev Can only be called indirectly from IssuingEntity.attachModule()
		@param _module Address of the module contract
		@return bool success
	 */
	function attachModule(address _module) external returns (bool) {
		require(msg.sender == address(issuer));
		_attachModule(_module);
		return true;
	}

	/**
		@notice Attach a security token module
		@dev
			Called indirectly from IssuingEntity.attachModule() or by the
			module that is attached.
		@param _module Address of the module contract
		@return bool success
	 */
	function detachModule(address _module) external returns (bool) {
		if (_module != msg.sender) {
			require(msg.sender == address(issuer));
		} else {
			/* msg.sig = 0xbb2a8522 */
			require(isPermittedModule(msg.sender, msg.sig));
		}
		_detachModule(_module);
		return true;
	}

	/**
		@notice Check if a module is active on this token
		@dev
			IssuingEntity modules are considered active on all tokens
			associated with that issuer.
		@param _module Deployed module address
	 */
	function isActiveModule(address _module) public view returns (bool) {
		if (moduleData[_module].active) return true;
		return issuer.isActiveModule(_module);
	}

	/**
		@notice Check if a module is permitted to access a specific function
		@dev
			This returns false instead of throwing because an issuer level 
			module must be checked twice
		@param _module Module address
		@param _sig Function signature
		@return bool permission
	 */
	function isPermittedModule(
		address _module,
		bytes4 _sig
	)
		public
		view
		returns (bool)
	{
		if (
			moduleData[_module].active && 
			moduleData[_module].permissions[_sig]
		) {
			return true;
		}
		return issuer.isPermittedModule(_module, _sig);
	}

	/**
		@notice Checks that a call comes from a permitted module or the issuer
		@dev If the caller is the issuer, requires multisig approval
		@return bool multisig approved
	 */
	function _checkPermitted() internal returns (bool) {
		if (isPermittedModule(msg.sender, msg.sig)) return true;
		require(issuer.isApprovedAuthority(msg.sender, msg.sig));
		return issuer.checkMultiSigExternal(msg.sig, keccak256(msg.data));
	}

}
