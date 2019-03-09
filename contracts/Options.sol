pragma solidity >=0.4.24 <0.5.0;

import "./modules/ModuleBase.sol";

contract Options is STModuleBase {

	mapping (bytes32 => Option[]) optionData;
	mapping (bytes32 => uint256) options;

	struct Option {
		uint96 amount;
		uint96 exercisePrice;
		uint32 creationDate;
		uint32 vestDate;
	}

	uint256 expiryDate;
	uint256 terminationGracePeriod;
	uint256 totalOptions;

	function getPermissions()
		external
		pure
		returns
	(
		bytes4[] permissions,
		bytes4[] hooks,
		bool[] hooksActive,
		bool[] hooksAlways
	)
	{

	}

	string public constant name = "Options";

	constructor(address _token, address _issuer) public STModuleBase(_token, _issuer) { }

	function issueOptions(
		bytes32 _id,
		uint96[] _amount,
		uint96[] _exercisePrice,
		uint32[] _vestDate
	)
		external
		returns (bool)
	{
		require(_amount.length == _exercisePrice.length);
		require(_amount.length == _vestDate.length);
		uint256 _total;
		for (uint256 i; i < _amount.length; i++) {
			optionData[_id].push(Option(_amount[i], _exercisePrice[i], uint32(now), _vestDate[i]));
			_total += _amount[i];
		}
		options[_id] += _total;
		totalOptions += _total;
	}

	function totalSupplyChanged(
		address _addr,
		bytes32 _id,
		uint8 _rating,
		uint16 _country,
		uint256 _old,
		uint256 _new
	)
		external
		returns (bool)
	{

	}

	function modifyAuthorizedSupply(
		address _token,
		uint256 _oldSupply,
		uint256 _newSupply
	)
		external
		returns (bool)
	{

	}



}
