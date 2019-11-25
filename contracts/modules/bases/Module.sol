pragma solidity 0.4.25;


import "../../bases/MultiSig.sol";
import "../../OrgCode.sol";
import "../../SecurityToken.sol";

/**
    @title ModuleBase Abstract Base Contract
    @dev Methods in this ABC are defined in contracts that inherit ModuleBase
*/
contract ModuleBaseABC {
    function getPermissions() external pure returns (bytes4[], bytes4[], uint256);
}


/**
    @title Module Base Contract
    @dev Inherited contract for Custodian modules
*/
contract ModuleBase is ModuleBaseABC {

    bytes32 public ownerID;
    address owner;

    /**
        @notice Base constructor
        @param _owner Contract address that module will be attached to
     */
    constructor(address _owner) public {
        owner = _owner;
        ownerID = MultiSig(_owner).ownerID();
    }

    /** @dev Check that call originates from approved authority, allows multisig */
    function _onlyAuthority() internal returns (bool) {
        return MultiSig(owner).checkMultiSigExternal(
            msg.sender,
            keccak256(msg.data),
            msg.sig
        );
    }

    /**
        @notice Fetch address of org contract that module is active on
        @return Owner contract address
    */
    function getOwner() public view returns (address) {
        return owner;
    }

}


/**
    @title Token Module Base Contract
    @dev Inherited contract for SecurityToken or NFToken modules
 */
contract STModuleBase is ModuleBase {

    SecurityToken public token;
    OrgCode public org;

    /**
        @notice Base constructor
        @param _token SecurityToken contract address
        @param _org OrgCode contract address
     */
    constructor(
        SecurityToken _token,
        address _org
    )
        public
        ModuleBase(_org)
    {
        token = _token;
        org = OrgCode(_org);
    }

    /** @dev Check that call originates from parent token contract */
    function _onlyToken() internal view {
        require(msg.sender == address(token));
    }

    /**
        @notice Fetch address of token that module is active on
        @return Token address
    */
    function getOwner() public view returns (address) {
        return address(token);
    }

}


contract IssuerModuleBase is ModuleBase {

    OrgCode public org;
    mapping (address => bool) parents;

    /**
        @notice Base constructor
        @param _org OrgCode contract address
     */
    constructor(address _org) public ModuleBase(_org) {
        org = OrgCode(_org);
    }

    /** @dev Check that call originates from token contract */
    function _onlyToken() internal {
        if (!parents[msg.sender]) {
            parents[msg.sender] = org.isActiveToken(msg.sender);
        }
        require (parents[msg.sender]);
    }

}
