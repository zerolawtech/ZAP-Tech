pragma solidity 0.4.25;

/** @title Governance Module Interface
    @dev
        these are the minimum required methods that MUST be included for
        the module to attach to OrgCode
 */
interface IGovernance {

    function orgCode() external view returns (address);

    function modifyAuthorizedSupply(address, uint256) external returns (bool);
    function addOrgShare(address _share) external returns (bool);

}
