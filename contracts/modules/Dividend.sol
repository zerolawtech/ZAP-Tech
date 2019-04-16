pragma solidity >=0.4.24 <0.5.0;

import "../open-zeppelin/SafeMath.sol";
import "./bases/Checkpoint.sol";

contract DividendModule is CheckpointModuleBase {

	using SafeMath for uint256;

	string public name = "Dividend";
	uint256 public dividendTime;
	uint256 public dividendAmount;
	uint256 public claimExpiration;

	mapping (address => bool) claimed;
	mapping (address => mapping (address => bool)) claimedCustodian;

	event DividendIssued(uint256 time, uint256 amount);
	event DividendClaimed(address beneficiary, uint256 amount);
	event DividendExpired(uint256 unclaimedAmount);
	event CustodianDividendClaimed(
		address indexed custodian,
		address beneficiary,
		uint256 amount
	);

	constructor(
		address _token,
		address _issuer,
		uint256 _time
	)
		CheckpointModuleBase(_token, _issuer, _time)
		public
	{
		return;
	}

	function issueDividend(uint256 _claimPeriod) external payable returns (bool) {
		if (!_onlyAuthority()) return false;
		require (dividendTime < now);
		require (claimExpiration == 0);
		require (msg.value > 0);
		claimExpiration = now.add(_claimPeriod);
		dividendAmount = msg.value;
		totalSupply = totalSupply.sub(_getBalance(token.issuer()));
		emit DividendIssued(dividendTime, msg.value);
		return true;
	}

	function claimDividend(address _beneficiary) external returns (bool) {
		require (address(this).balance > 0);
		_claim(_beneficiary == 0 ? msg.sender : _beneficiary);
		return true;
	}

	function claimMany(address[] _beneficiaries) external returns (bool) {
		require (address(this).balance > 0);
		for (uint256 i; i < _beneficiaries.length; i++) {
			_claim(_beneficiaries[i]);
		}
		return true;
	}

	function _claim(address _beneficiary) internal {
		require(issuer.isRegisteredInvestor(_beneficiary));
		require (!claimed[_beneficiary]);
		uint256 _value = _getBalance(
			_beneficiary
		).mul(dividendAmount).div(totalSupply);
		claimed[_beneficiary] = true;
		_beneficiary.transfer(_value);
		emit DividendClaimed(_beneficiary, _value);
	}

	function claimCustodianDividend(
		address _beneficiary,
		address _custodian
	)
		external
		returns (bool)
	{
		require (address(this).balance > 0);
		_claimCustodian(_beneficiary, _custodian);
		return true;
	}

	function claimManyCustodian(
		address[] _beneficiaries,
		address _custodian
	)
		external
		returns (bool)
	{
		require (address(this).balance > 0);
		for (uint256 i; i < _beneficiaries.length; i++) {
			_claimCustodian(_beneficiaries[i], _custodian);
		}
		return true;
	}

	function _claimCustodian(address _beneficiary, address _custodian) internal {
		require(issuer.isRegisteredInvestor(_beneficiary));
		require (!claimedCustodian[_beneficiary][_custodian]);
		uint256 _value = _getCustodianBalance(
			_beneficiary,
			_custodian
		).mul(dividendAmount).div(totalSupply);
		claimedCustodian[_beneficiary][_custodian] = true;
		_beneficiary.transfer(_value);
		emit CustodianDividendClaimed(
			_custodian,
			_beneficiary,
			_value
		);
	}

	function closeDividend() external returns (bool) {
		if (!_onlyAuthority()) return false;
		require (claimExpiration > 0);
		require (now > claimExpiration || address(this).balance == 0);
		emit DividendExpired(address(this).balance);
		msg.sender.transfer(address(this).balance);
		require (token.detachModule(address(this)));
		return true;
	}

}
