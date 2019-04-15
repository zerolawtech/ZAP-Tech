pragma solidity >=0.4.24 <0.5.0;

import "../../open-zeppelin/SafeMath.sol";
import "./BaseCheckpoint.sol";

contract DividendModule is CheckpointModule {

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
		CheckpointModule(_token, _issuer, _time)
		public
	{

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

	function claimDividend(address _beneficiary) public {
		require (address(this).balance > 0);
		if (_beneficiary == 0) {
			_beneficiary = msg.sender;
		}
		require (issuer.getID(_beneficiary) != ownerID);
		require (!claimed[_beneficiary]);
		uint256 _value = (
			_getBalance(_beneficiary).mul(dividendAmount).div(totalSupply)
		);
		claimed[_beneficiary] = true;
		_beneficiary.transfer(_value);
		emit DividendClaimed(_beneficiary, _value);
	}

	function claimMany(address[] _beneficiaries) public {
		for (uint256 i = 0; i < _beneficiaries.length; i++) {
			claimDividend(_beneficiaries[i]);
		}
	}

	function claimCustodianDividend(
		address _custodian,
		address _beneficiary
	)
		public
	{
		require (address(this).balance > 0);
		if (_beneficiary == 0) {
			_beneficiary = msg.sender;
		}
		require (issuer.getID(_beneficiary) != ownerID);
		require (!claimedCustodian[_custodian][_beneficiary]);
		uint256 _value = _getCustodianBalance(
			_custodian,
			_beneficiary
		).mul(dividendAmount).div(totalSupply);
		claimedCustodian[_custodian][_beneficiary] = true;
		msg.sender.transfer(_value);
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
