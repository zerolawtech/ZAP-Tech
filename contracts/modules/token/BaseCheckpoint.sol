pragma solidity >=0.4.24 <0.5.0;

import "../../open-zeppelin/SafeMath.sol";
import "../ModuleBase.sol";
import "../../interfaces/IBaseCustodian.sol";

contract CheckpointModule is STModuleBase {

	using SafeMath for uint256;

	uint256 time;
	uint256 totalSupply;
	mapping (address => uint256) balance;
	mapping (address => bool) zeroBalance;

	mapping (address => mapping(address => uint256)) custodianBalance;
	mapping (address => mapping(address => bool)) custodianZeroBalance;

	constructor(
		address _token,
		address _issuer,
		uint256 _time
	)
		STModuleBase(_token, _issuer)
		public
	{
		require (_time >= now);
		totalSupply = token.totalSupply();
		time = _time;
	}

	function getPermissions()
		external
		pure
		returns
	(
		bytes4[] hooks,
		bytes4[] permissions
	)
	{
		bytes4[] memory _hooks = new bytes4[](3);
		bytes4[] memory _permissions = new bytes4[](1);
		_hooks[0] = 0x35a341da;
		_hooks[1] = 0x4268353d;
		_hooks[2] = 0x6eaf832c;
		_permissions[0] = 0xbb2a8522;
		return (_hooks, _permissions);
	}

	function _getBalance(address _owner) internal view returns (uint256) {
		if (balance[_owner] > 0) return balance[_owner];
		if (zeroBalance[_owner]) return 0;
		return token.balanceOf(_owner);
	}

	function _getCustodianBalance(address _custodian, address _addr) internal view returns (uint256) {
		if (custodianBalance[_custodian][_addr] > 0) return custodianBalance[_custodian][_addr];
		if (custodianZeroBalance[_custodian][_addr]) return 0;
		return token.custodianBalanceOf(_addr, _custodian);
	}

	function transferTokens(
		address[2] _addr,
		bytes32[2] _id,
		uint8[2] _rating,
		uint16[2],
		uint256 _value
	)
		external
		onlyOwner
		returns (bool)
	{
		if (now < time) return true;
		if (_rating[0] == 0 && _id[0] != ownerID) {
			_checkCustodianSent(IBaseCustodian(_addr[0]), _addr[1], _value);
		} else if (balance[_addr[0]] == 0 && !zeroBalance[_addr[0]]) {
			balance[_addr[0]] = token.balanceOf(_addr[0]).add(_value);
		}
		if (_rating[1] == 0 && _id[1] != ownerID) {
			_checkCustodianReceived(IBaseCustodian(_addr[1]), _addr[0], _value);
		} else if (balance[_addr[1]] == 0 && !zeroBalance[_addr[1]]) {
			uint256 _bal = token.balanceOf(_addr[1]).sub(_value);
			if (_bal == 0) {
				zeroBalance[_addr[1]] == true;
			} else {
				balance[_addr[1]] = _bal;
			}
		}
		return true;
	}

	function _checkCustodianSent(address _cust, address _addr, uint256 _value) internal {
		if (
			custodianBalance[_cust][_addr] == 0 &&
			!custodianZeroBalance[_cust][_addr]
		) {
			custodianBalance[_cust][_addr] = token.custodianBalanceOf(_addr, _cust).add(_value);
		}
	}

	function _checkCustodianReceived(address _cust, address _addr, uint256 _value) internal {
		if (
			custodianBalance[_cust][_addr] == 0 &&
			!custodianZeroBalance[_cust][_addr]
		) {
			uint256 _bal = token.custodianBalanceOf(_addr, _cust).sub(_value);
			if (_bal == 0) {
				custodianZeroBalance[_cust][_addr] == true;
			} else {
				custodianBalance[_cust][_addr] = _bal;
			}
		}
	}

	function transferTokensCustodian(
		address _cust,
		address[2] _addr,
		bytes32[2],
		uint8[2],
		uint16[2],
		uint256 _value
	)
		external
		returns (bool)
	{
		if (now < time) return true;
		_checkCustodianSent(_cust, _addr[0], _value);
		_checkCustodianReceived(_cust, _addr[1], _value);
		return true;
	}

	function balanceChanged(
		address _addr,
		bytes32,
		uint8,
		uint16,
		uint256 _old,
		uint256 _new
	)
		external
		onlyOwner
		returns (bool)
	{
		if (now < time) {
			totalSupply = totalSupply.add(_new).sub(_old);
			return true;
		}
		if (balance[_addr] > 0) return true;
		if (zeroBalance[_addr]) return true;
		if (_old > 0) {
			balance[_addr] = _old;
		} else {
			zeroBalance[_addr] = true;
		}
		return true;
	}

}
