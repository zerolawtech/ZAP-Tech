pragma solidity >=0.4.24 <0.5.0;

/** @title Minimal Custodian Interface */
interface IBaseCustodian {

	function ownerID() external view returns (bytes32);
	
	function receiveTransfer(
		address _from,
		uint256 _value
	)
		external
		returns (bool);
}
