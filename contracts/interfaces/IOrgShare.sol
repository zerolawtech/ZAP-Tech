pragma solidity 0.4.25;

/** @title OrgShareBase Interface
    @dev
        this is a minimal interface that can be used to interact with both
        BookShare and CertShare contracts
 */
contract IOrgShareBase {
    event Approval (address indexed shareOwner, address indexed spender, uint256 value);
    event AuthorizedSupplyChanged (uint256 oldAuthorized, uint256 newAuthorized);
    event ModuleAttached (address module, bytes4[] hooks, bytes4[] permissions);
    event ModuleDetached (address module);
    event ModuleHookSet (address module, bytes4 hook, bool active, bool always);
    event Transfer (address indexed from, address indexed to, uint256 value);

    function approve (address _spender, uint256 _value) external returns (bool);
    function attachModule (address _module) external returns (bool);
    function clearHookTags (bytes4 _sig, bytes1[] _tagBase) external returns (bool);
    function detachModule (address _module) external returns (bool);
    function modifyAuthorizedSupply (uint256 _value) external returns (bool);
    function setHook (bytes4 _sig, bool _active, bool _always) external returns (bool);
    function setHookTags (bytes4 _sig, bool _value, bytes1 _tagBase, bytes1[] _tags) external returns (bool);
    function transfer (address, uint256) external returns (bool);
    function transferCustodian (address[2], uint256) external returns (bool);
    function transferFrom (address, address, uint256) external returns (bool);
    function allowance (address _owner, address _spender) external view returns (uint256);
    function authorizedSupply () external view returns (uint256);
    function balanceOf (address) external view returns (uint256);
    function checkTransfer (address _from, address _to, uint256 _value) external view returns (bool);
    function checkTransferCustodian (address _cust, address _from, address _to, uint256 _value) external view returns (bool);
    function circulatingSupply () external view returns (uint256);
    function custodianBalanceOf (address _owner, address _cust) external view returns (uint256);
    function decimals () external view returns (uint8);
    function isActiveModule (address _module) external view returns (bool);
    function isPermittedModule (address _module, bytes4 _sig) external view returns (bool);
    function name () external view returns (string);
    function org () external view returns (address);
    function ownerID () external view returns (bytes32);
    function symbol () external view returns (string);
    function totalSupply () external view returns (uint256);
    function treasurySupply () external view returns (uint256);
}

/** @title BookShare Interface
    @dev
        this is a minimal interface that can be used to interact BookShare contracts
 */
contract IBookShare is IOrgShareBase {
    function mint(address _owner, uint256 _value) external returns (bool);
    function burn(address _owner, uint256 _value) external returns (bool);
}

/** @title CertShare Interface
    @dev
        this is a minimal interface that can be used to interact CertShare contracts
 */
contract ICertShare is IOrgShareBase {
    function burn(uint48 _start, uint48 _stop) external returns (bool);
    function mint(address _owner, uint48 _value, uint32 _time, bytes2 _tag) external returns (bool);
    function modifyRange(uint48 _pointer, uint32 _time, bytes2 _tag) public returns (bool);
    function modifyRanges(uint48 _start, uint48 _stop, uint32 _time, bytes2 _tag) public returns (bool);
    function transferRange(address _to, uint48 _start, uint48 _stop) external returns (bool);
    function custodianRangesOf(address _owner, address _custodian) external view returns (uint48[2][]);
    function getRange(uint256 _idx) external view returns (address _owner, uint48 _start, uint48 _stop, uint32 _time, bytes2 _tag, address _custodian);
    function rangesOf(address _owner) external view returns (uint48[2][]);
}
