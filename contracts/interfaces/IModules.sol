pragma solidity >=0.4.24 <0.5.0;

/**
	Common interface for all modules - these are the minimum required methods
	that must be included to attach the contract
*/
interface IBaseModule {
	function getPermissions()
		external
		pure
		returns
	(
		bytes4[] permissions,
		bytes4[] hooks,
		uint256 hookBools
	);
	function getOwner() external view returns (address);
	function name() external view returns (string);
}

/** SecurityToken module interface */
interface ISTModule {
	
	function token() external returns (address);
	
	/* 0x70aaf928 */
	function checkTransfer(
		address[2] _addr,
		bytes32 _authID,
		bytes32[2] _id,
		uint8[2] _rating,
		uint16[2] _country,
		uint256 _value
	)
		external
		view
		returns (bool);

	/* 0x35a341da */
	function transferTokens(
		address[2] _addr,
		bytes32[2] _id,
		uint8[2] _rating,
		uint16[2] _country,
		uint256 _value
	)
		external
		returns (bool);

	/* 0x8b5f1240 */
	function transferTokensCustodian(
		address _custodian,
		address[2] _addr,
		bytes32[2] _id,
		uint8[2] _rating,
		uint16[2] _country,
		uint256 _value
	)
		external
		returns (bool);

	/* 0xb1a1a455 */
	function modifyAuthorizedSupply(
		address _token,
		uint256 _oldSupply,
		uint256 _newSupply
	)
		external
		returns (bool);

	/* 0x741b5078 */
	function totalSupplyChanged(
		address _addr,
		bytes32 _id,
		uint8 _rating,
		uint16 _country,
		uint256 _old,
		uint256 _new
	)
		external
		returns (bool);
}

/** NFToken module interface */
interface INFTModule {

	function token() external returns (address);

	/* 0x70aaf928 */
	function checkTransfer(
		address[2] _addr,
		bytes32 _authID,
		bytes32[2] _id,
		uint8[2] _rating,
		uint16[2] _country,
		uint256 _value
	)
		external
		view
		returns (bool);

	/* 0x2d79c6d7 */
	function checkTransferRange(
		address[2] _addr,
		bytes32 _authID,
		bytes32[2] _id,
		uint8[2] _rating,
		uint16[2] _country,
		uint48[2] _range
	)
		external
		view
		returns (bool);

	/* 0xead529f5 */
	function transferTokenRange(
		address[2] _addr,
		bytes32[2] _id,
		uint8[2] _rating,
		uint16[2] _country,
		uint48[2] _range
	)
		external
		returns (bool);

	/* 0x8b5f1240 */
	function transferTokensCustodian(
		address _custodian,
		address[2] _addr,
		bytes32[2] _id,
		uint8[2] _rating,
		uint16[2] _country,
		uint256 _value
	)
		external
		returns (bool);

	/* 0xb1a1a455 */
	function modifyAuthorizedSupply(
		address _token,
		uint256 _oldSupply,
		uint256 _newSupply
	)
		external
		returns (bool);

	/* 0x741b5078 */
	function totalSupplyChanged(
		address _addr,
		bytes32 _id,
		uint8 _rating,
		uint16 _country,
		uint256 _old,
		uint256 _new
	)
		external
		returns (bool);
}

/** IssuingEntity module interface */
interface IIssuerModule {

	/* 0x9a5150fc */
	function checkTransfer(
		address _token,
		bytes32 _authID,
		bytes32[2] _id,
		uint8[2] _rating,
		uint16[2] _country
	)
		external
		view
		returns (bool);

	/* 0xb446f3ca */
	function tokenTotalSupplyChanged(
		address _token,
		bytes32 _id,
		uint8 _rating,
		uint16 _country,
		uint256 _old,
		uint256 _new
	)
		external
		returns (bool);
}

/** Custodian module interface */
interface ICustodianModule {

	/**
		@notice Custodian sent tokens
		@dev
			Called after a successful token transfer from the custodian.
			Use 0xb4684410 as the hook value for this method.
		@param _token Token address
		@param _to Recipient address
		@param _value Amount of tokens transfered
		@return bool success
	 */
	function sentTokens(
		address _token,
		address _to,
		uint256 _value
	)
		external
		returns (bool);

	/**
		@notice Custodian received tokens
		@dev
			Called after a successful token transfer to the custodian.
			Use 0xb15bcbc4 as the hook value for this method.
		@param _token Token address
		@param _from Sender address
		@param _value Amount of tokens transfered
		@return bool success
	 */
	function receivedTokens(
		address _token,
		address _from,
		uint256 _value
	)
		external
		returns (bool);

	/* 0x44a29e2a */
	function internalTransfer(
		address _token,
		address _from,
		address _to,
		uint256 _value
	)
		external
		returns (bool);
}