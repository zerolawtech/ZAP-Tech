pragma solidity 0.4.25;

/** @title TokenBase Interface
    @dev
        this is a minimal interface that can be used to interact with both
        SecurityToken and NFToken contracts
 */
interface ITokenBase {

    function ownerID() external view returns (bytes32);
    function org() external view returns (address);

    function decimals() external view returns (uint8);
    function name() external view returns (string);
    function symbol() external view returns(string);

    function totalSupply() external view returns (uint256);
    function authorizedSupply() external view returns (uint256);
    function circulatingSupply() external view returns (uint256);
    function treasurySupply() external view returns (uint256);

    function balanceOf(address) external view returns (uint256);
    function custodianBalanceOf(address _owner, address _custodian) external view returns (uint256);
    function allowance(address _owner, address _spender) external view returns (uint256);

    function checkTransfer(address _from, address _to, uint256 _value) external view returns (bool);
    function checkTransferCustodian(address _cust, address _from, address _to, uint256 _value) external view returns (bool);

    function approve(address _spender, uint256 _value) external returns (bool);
    function transfer(address _to, uint256 _value) external returns (bool);
    function transferFrom(address _from, address _to, uint256 _value) external returns (bool);

    function modifyAuthorizedSupply(uint256) external returns (bool);
    function attachModule(address) external returns (bool);
    function detachModule(address) external returns (bool);

}
