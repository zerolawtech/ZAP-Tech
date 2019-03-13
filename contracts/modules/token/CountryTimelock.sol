pragma solidity ^0.4.24;

import "../ModuleBase.sol";

/** @title Country based transfer timelock module */
contract CountryLockModule is STModuleBase {

	string public name = "CountryTimeLock";
	mapping (uint16 => uint256) public countryLock;

	/**
		@notice supply permissions and hook points when attaching module
		@dev
			hooks: 0x70aaf928 - checkTransfer
			hookBools - all true
	 */
	function getPermissions()
		external
		pure
		returns (
			bytes4[] _permissions,
			bytes4[] _hooks,
			uint256 _hookBools
		)
	{
		_hooks = new bytes4[](1);
		_hooks[0] = 0x70aaf928;
		return (_hooks, _permissions, uint256(-1));
	}

	/**
		@notice constructor
		@param _token token address
		@param _issuer issuer address
	 */
	constructor(
		address _token,
		address _issuer
	)
		STModuleBase(_token, _issuer)
		public
	{
		return;
	}

	/**
		@notice Set time lock for a country
		@dev Only callable by permitted authority
		@param _country Country code
		@param _epochTime Absolute epoch time to lock transfers until
		@return bool success
	 */
	function modifyCountryLock(
		uint16 _country,
		uint256 _epochTime
	)
		external
		returns (bool)
	{
		if (!_onlyAuthority()) return false;
		countryLock[_country] = _epochTime;
		return true;
	}

	/**
		@notice SecurityToken.checkTransfer hook point method
		@dev Checks that now > time lock
	 */
	function checkTransfer(
		address[2],
		bytes32,
		bytes32[2],
		uint8[2],
		uint16[2] _country,
		uint256
	)
		external
		view
		returns (bool)
	{
		require (countryLock[_country[0]] < now);
		require (countryLock[_country[1]] < now);
	}

}
