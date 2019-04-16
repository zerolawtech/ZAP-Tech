pragma solidity >=0.4.24 <0.5.0;

import "../SecurityToken.sol";
import "../bases/MultiSig.sol";

/**
	@title Module Base Contract
	@dev Inherited contract for IssuingEntity or Custodian modules
*/
contract ModuleBase {

	bytes32 public ownerID;
	address owner;

	function _onlyAuthority() internal returns (bool) {
		return MultiSig(owner).checkMultiSigExternal(
			msg.sender,
			keccak256(msg.data),
			msg.sig
		);
	}

	/**
		@notice Base constructor
		@param _owner Contract address that module will be attached to
	 */
	constructor(address _owner) public {
		owner = _owner;
		ownerID = MultiSig(owner).ownerID();
	}

	/**
		@notice Fetch address of issuer contract that module is active on
		@return Owner contract address
	*/
	function getOwner() public view returns (address) {
		return owner;
	}

}

/** @title SecurityToken Module Base Contract */
contract STModuleBase is ModuleBase {

	SecurityToken public token;
	IssuingEntity public issuer;

	/** @dev Check that call originates from issuer or token contract */
	function _onlyOwner() internal view {
		require(msg.sender == address(token) || msg.sender == address(owner));
	}

	/**
		@notice Base constructor
		@param _token SecurityToken contract address
		@param _issuer IssuingEntity contract address
	 */
	constructor(address _token, address _issuer) public ModuleBase(_issuer) {
		token = SecurityToken(_token);
		issuer = IssuingEntity(_issuer);
	}

	/**
		@notice Fetch address of token that module is active on
		@return Token address
	*/
	function getOwner() public view returns (address) {
		return address(token);
	}

}