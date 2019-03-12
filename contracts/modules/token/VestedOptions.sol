pragma solidity >=0.4.24 <0.5.0;

import "../ModuleBase.sol";

contract VestedOptions is STModuleBase {

	string public constant name = "Options";

	uint256 public totalOptions;
	uint256 public ethPeg;
	uint32 public expiryDate;
	uint32 public terminationGracePeriod;
	address public receiver;

	mapping (bytes32 => Option[]) optionData;
	mapping (bytes32 => uint256) public options;

	struct Option {
		uint96 amount;
		uint96 exercisePrice;
		uint32 creationDate;
		uint32 vestDate;
	}

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

	constructor(
		address _token,
		address _issuer,
		uint32 _expiry,
		uint32 _gracePeriod,
		address _receiver
	)
		public
		STModuleBase(_token, _issuer)
	{
		expiryDate = _expiry;
		terminationGracePeriod = _gracePeriod;
		receiver = _receiver;
	}

	function issueOptions(
		bytes32 _id,
		uint96[] _amount,
		uint96[] _exercisePrice,
		uint32[] _vestDate
	)
		external
		returns (bool)
	{
		if (!_onlyAuthority()) return false;
		require(_amount.length == _exercisePrice.length);
		require(_amount.length == _vestDate.length);
		uint256 _total;
		for (uint256 i; i < _amount.length; i++) {
			optionData[_id].push(Option(_amount[i], _exercisePrice[i], uint32(now), _vestDate[i]));
			_total += _amount[i];
		}
		options[_id] += _total;
		totalOptions += _total;
		return true;
	}

	function accellerateVestingDate(
		bytes32 _id,
		uint256[] _idx,
		uint32 _vestDate
	)
		external
		returns (bool)
	{
		if (!_onlyAuthority()) return false;
		for (uint256 i; i < _idx.length; i++) {
			require(optionData[_id][_idx[i]].vestDate >= _vestDate, "Cannot extend vesting date");
			optionData[_id][_idx[i]].vestDate = _vestDate;
		}
		return true;
	}

	function exerciseOptions(
		uint256[] _idx
	)
		external
		payable
		returns (bool)
	{
		bytes32 _id = issuer.getID(msg.sender);
		uint256 _amount;
		uint256 _exerciseTotal;
		for (uint256 i; i < _idx.length; i++) {
			Option storage o = optionData[_id][_idx[i]];
			require(o.vestDate <= now, "Options have not vested");
			require(o.creationDate + expiryDate > now, "Options have expired");
			_amount += o.amount;
			_exerciseTotal += o.exercisePrice * o.amount;
			delete optionData[_id][_idx[i]];
		}
		require(msg.value == _exerciseTotal * ethPeg, "Incorrect payment amount");
		receiver.transfer(address(this).balance);
		totalOptions -= _amount;
		options[_id] -= _amount;
		require(token.mint(msg.sender, _amount));
		return true;
	}

	function cancelExpiredOptions(
		bytes32 _id
	)
		external
		returns (bool)
	{
		Option[] storage o = optionData[_id];
		uint256 _amount;
		for (uint256 i; i < o.length; i++) {
			if (o[i].creationDate + expiryDate > now) continue;
			_amount += o[i].amount;
			delete o[i];
		}
		totalOptions -= _amount;
		options[_id] -= _amount;
		return true;
	}

	function terminateOptions(
		bytes32 _id
	)
		external
		returns (bool)
	{
		if (!_onlyAuthority()) return false;
		Option[] storage o = optionData[_id];
		uint256 _amount;
		for (uint256 i; i < o.length; i++) {
			if (o[i].vestDate > now) {
				_amount += o[i].amount;
				delete o[i];
			} else {
				o[i].creationDate = uint32(now) - expiryDate + terminationGracePeriod;
			}
		}
		totalOptions -= _amount;
		options[_id] -= _amount;
		return true;
	}

	function totalSupplyChanged(
		address,
		bytes32,
		uint8,
		uint16,
		uint256 _old,
		uint256 _new
	)
		external
		view
		returns (bool)
	{
		if (_old > _new) {
			require(token.authorizedSupply() - token.totalSupply() >= totalOptions);
		}
		return true;
		
	}

	function modifyAuthorizedSupply(
		address,
		uint256 _oldSupply,
		uint256 _newSupply
	)
		external
		view
		returns (bool)
	{
		if (_oldSupply > _newSupply) {
			require(_newSupply - token.totalSupply() >= totalOptions);
		}
		return true;
	}

}
