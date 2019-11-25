pragma solidity 0.4.25;

/** @title Minimal Custodian Interface
    @dev
        these are the minimum required methods that MUST be included for
        the module to attach to OrgCode
 */
interface IBaseCustodian {

    function ownerID() external view returns (bytes32);
    
    function receiveTransfer(
        address _from,
        uint256 _value
    )
        external
        returns (bool);
}
