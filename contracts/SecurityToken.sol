pragma solidity >=0.4.24 <0.5.0;

import "./TokenBase.sol";

/**
	@title Security Token
	@dev
		Expands upon the ERC20 token standard
		https://theethereum.wiki/w/index.php/ERC20_Token_Standard
 */
contract SecurityToken is TokenBase {

	using SafeMath for uint256;

	mapping (address => uint256) balances;

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
		TokenBase(
			_issuer,
			_name,
			_symbol,
			_authorizedSupply
		)
	{	}

	/**
		@notice Fetch the current balance at an address
		@param _owner Address of balance to query
		@return integer
	 */
	function balanceOf(address _owner) public view returns (uint256) {
		return balances[_owner];
	}

	/**
		@notice View function to check if a transfer is permitted
		@dev If a transfer is not allowed, the function will throw
		@param _from Address of sender
		@param _to Address of recipient
		@param _value Amount being transferred
		@return bool success
	 */
	function checkTransfer(
		address _from,
		address _to, 
		uint256 _value
	)
		external
		view
		returns (bool)
	{
		_checkToSend(_from, [_from, _to], _value);
		return true;
	}

	/**
		@notice Check if custodian internal transfer is permitted
		@dev If a transfer is not allowed, the function will throw
		@dev Do not call directly, use Custodian.checkTransferInternal
		@param _id Array of sender/receiver investor IDs
		@param _stillOwner bool is sender still a beneficial owner?
		@return bool success
	 */
	function checkTransferCustodian(
		bytes32[2] _id,
		bool _stillOwner
	)
		external
		view
		returns (bool)
	{
		(
			bytes32 _custID,
			uint8[2] memory _rating,
			uint16[2] memory _country
		) = issuer.checkTransferCustodian(
			msg.sender,
			address(this),
			_id,
			_stillOwner
		);
		_checkTransfer(
			[address(0), address(0)],
			_custID,
			_id,
			_rating,
			_country,
			0
		);
		return true;
	}

	/**
		@notice internal check of transfer permission before performing it
		@param _auth Address calling to initiate the transfer
		@param _addr Address of sender / recipient
		@param _value Amount being transferred
		@return ID of caller
		@return ID array of investors
		@return address array of investors 
		@return uint8 array of investor ratings
		@return uint16 array of investor countries
	 */
	function _checkToSend(
		address _auth,
		address[2] _addr,
		uint256 _value
	)
		internal
		returns (
			bytes32 _authID,
			bytes32[2] _id,
			address[2],
			uint8[2] _rating,
			uint16[2] _country
		)
	{
		require(_value > 0, "Cannot send 0 tokens");
		(_authID, _id, _rating, _country) = issuer.checkTransfer(
			_auth,
			_addr[0],
			_addr[1],
			_value == balances[_addr[0]],
			_value
		);
		_addr = _checkTransfer(
			_addr,
			_authID,
			_id,
			_rating,
			_country,
			_value
		);
		return(_authID, _id, _addr, _rating, _country);
	}

	/**
		@notice internal check of transfer permission
		@dev common logic for checkTransfer() and _checkToSend()
		@param _addr address array of investors 
		@param _authID ID of caller
		@param _id ID array of investor IDs
		@param _rating array of investor ratings
		@param _country array of investor countries
		@param _value Amount being transferred
		@return array of investor addresses
	 */
	function _checkTransfer(
		address[2] _addr,
		bytes32 _authID,
		bytes32[2] _id,
		uint8[2] _rating,
		uint16[2] _country,
		uint256 _value
	)
		internal
		view
		returns (address[2])
	{
		/* Issuer tokens are held at the IssuingEntity contract address */
		if (_id[0] == ownerID) {
			_addr[0] = address(issuer);
		}
		if (_id[1] == ownerID) {
			_addr[1] = address(issuer);
		}
		require(balances[_addr[0]] >= _value, "Insufficient Balance");
		/* bytes4 signature for token module checkTransfer() */
		_callModules(0x70aaf928, 0x00, abi.encode(
			_addr,
			_authID,
			_id,
			_rating,
			_country,
			_value
		));
		return _addr;
	}

	/**
		@notice ERC-20 transfer standard
		@dev calls to _checkToSend() to verify permission before transferring
		@param _to Recipient
		@param _value Amount being transferred
		@return bool success
	 */
	function transfer(address _to, uint256 _value) external returns (bool) {
		(
			bytes32 _authID,
			bytes32[2] memory _id,
			address[2] memory _addr,
			uint8[2] memory _rating,
			uint16[2] memory _country
		) = _checkToSend(msg.sender, [msg.sender, _to], _value);
		_transfer(_addr, _id, _rating, _country, _value);
		return true;
	}

	/**
		@notice ERC-20 transferFrom standard
		@dev
			* The issuer may use this function to transfer tokens belonging to
			  any address.
			* Modules may call this function to transfer tokens with the same
			  level of authority as the issuer.
			* An investor with multiple addresses may use this to transfer tokens
			  from any address he controls, without giving prior approval to that
			  address.
			* An unregistered address cannot initiate a transfer, even if it was
			  given approval.
		@param _from Sender
		@param _to Recipient
		@param _value Amount being transferred
		@return bool success
	 */
	function transferFrom(
		address _from,
		address _to,
		uint256 _value
	)
		external
		returns (bool)
	{
		/* If called by a module, the authority becomes the issuing contract. */
		/* msg.sig = 0x23b872dd */
		if (isPermittedModule(msg.sender, msg.sig)) {
			address _auth = address(issuer);
		} else {
			_auth = msg.sender;
		}
		(
			bytes32 _authID,
			bytes32[2] memory _id,
			address[2] memory _addr,
			uint8[2] memory _rating,
			uint16[2] memory _country
		) = _checkToSend(_auth, [_from, _to], _value);

		if (_id[0] != _id[1] && _authID != ownerID && _authID != _id[0]) {
			/*
				If the call was not made by the issuer or the sender and involves
				a change in ownership, subtract from the allowed mapping.
			*/
			require(allowed[_from][_auth] >= _value, "Insufficient allowance");
			allowed[_from][_auth] = allowed[_from][_auth].sub(_value);
		}
		_transfer(_addr, _id, _rating, _country, _value);
		return true;
	}

	/**
		@notice Internal transfer function
		@dev common logic for transfer() and transferFrom()
		@param _addr Array of sender/receiver addresses
		@param _id Array of sender/receiver IDs
		@param _rating Array of sender/receiver ratings
		@param _country Array of sender/receiver countries
		@param _value Amount to transfer
	 */
	function _transfer(
		address[2] _addr,
		bytes32[2] _id,
		uint8[2] _rating,
		uint16[2] _country,		
		uint256 _value
	)
		internal
	{
		balances[_addr[0]] = balances[_addr[0]].sub(_value);
		balances[_addr[1]] = balances[_addr[1]].add(_value);
		require(issuer.transferTokens(
			_id,
			_rating,
			_country,
			_value,
			[balances[_addr[0]] == 0, balances[_addr[1]] == _value]
		));
		/* bytes4 signature for token module transferTokens() */
		_callModules(
			0x35a341da,
			0x00,
			abi.encode(_addr, _id, _rating, _country, _value)
		);
		emit Transfer(_addr[0], _addr[1], _value);
	}

	/**
		@notice Check custodian internal transfer permission and set ownership
		@dev Called by Custodian.transferInternal
		@param _id Array of sender/receiver investor IDs
		@param _value Amount being transferred
		@param _stillOwner bool is sender still a beneficial owner?
		@return bool success
	 */
	function transferCustodian(
		bytes32[2] _id,
		uint256 _value,
		bool _stillOwner
	)
		external
		returns (bool)
	{
		(
			bytes32 _custID,
			uint8[2] memory _rating,
			uint16[2] memory _country
		) = issuer.checkTransferCustodian(
			msg.sender,
			address(this),
			_id,
			_stillOwner
		);
		_checkTransfer(
			[address(0), address(0)],
			_custID,
			_id,
			_rating,
			_country,
			0
		);
		require(issuer.transferCustodian(
			_custID,
			_id,
			_rating,
			_country,
			_value,
			_stillOwner
		));
		/* bytes4 signature for token module transferTokensCustodian() */
		_callModules(
			0x6eaf832c,
			0x00,
			abi.encode(msg.sender, _id, _rating, _country, _value)
		);
		return true;
	}

	/**
		@notice Mint new tokens and increase total supply
		@dev Callable by the issuer or via module
		@param _owner Owner of the tokens
		@param _value Number of tokens to mint
		@return bool
	 */
	function mint(address _owner, uint256 _value) external returns (bool) {
		/* msg.sig = 0x40c10f19 */
		if (!_checkPermitted()) return false;
		require(_value > 0);
		issuer.checkTransfer(
			address(issuer),
			address(issuer),
			_owner,
			false,
			_value
		);
		uint256 _old = balances[_owner];
		balances[_owner] = _old.add(_value);
		totalSupply = totalSupply.add(_value);
		require(totalSupply <= authorizedSupply);
		emit Transfer(0x00, _owner, _value);
		return _modifyTotalSupply(_owner, _old);
	}

	/**
		@notice Burn tokens and decrease total supply
		@dev Callable by the issuer or via module
		@param _owner Owner of the tokens
		@param _value Number of tokens to burn
		@return bool
	 */
	function burn(address _owner, uint256 _value) external returns (bool) {
		/* msg.sig = 0x9dc29fac */
		if (!_checkPermitted()) return false;
		require(_value > 0);
		uint256 _old = balances[_owner];
		balances[_owner] = _old.sub(_value);
		totalSupply = totalSupply.sub(_value);
		emit Transfer(_owner, 0x00, _value);
		return _modifyTotalSupply(_owner, _old);
	}

}
