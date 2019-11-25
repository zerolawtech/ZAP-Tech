pragma solidity 0.4.25;

import "../../bases/MultiSig.sol";

import "../../interfaces/IOrgCode.sol";
import "../../interfaces/IOrgShare.sol";

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
    @title OrgShare Module Base Contract
    @dev Inherited contract for BookShare and CertShare modules
 */
contract OrgShareModuleBase is ModuleBase {

    IOrgShareBase token;
    IOrgCode public org;

    /**
        @notice Base constructor
        @param _token OrgShare contract address
        @param _org OrgCode contract address
     */
    constructor(
        IOrgShareBase _token,
        IOrgCode _org
    )
        public
        ModuleBase(_org)
    {
        org = _org;
        token = _token;
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

/**
    @title BookShare Module Base Contract
    @dev Inherited contract for BookShare modules
 */
contract BookShareModuleBase is OrgShareModuleBase {

    IBookShare public token;

    /**
        @notice Base constructor
        @param _token BookShare contract address
        @param _org OrgCode contract address
     */
    constructor(
        IBookShare _token,
        IOrgCode _org
    )
        public
        OrgShareModuleBase(_token, _org)
    {
        token = _token;
    }

}


/**
    @title CertShare Module Base Contract
    @dev Inherited contract for CertShare modules
 */
contract CertShareModuleBase is OrgShareModuleBase {

    ICertShare public token;

    /**
        @notice Base constructor
        @param _token CertShare contract address
        @param _org OrgCode contract address
     */
    constructor(
        ICertShare _token,
        IOrgCode _org
    )
        public
        OrgShareModuleBase(_token, _org)
    {
        token = _token;
    }

}

contract IssuerModuleBase is ModuleBase {

    IOrgCode public org;
    mapping (address => bool) parents;

    /**
        @notice Base constructor
        @param _org IOrgCode contract address
     */
    constructor(address _org) public ModuleBase(_org) {
        org = IOrgCode(_org);
    }

    /** @dev Check that call originates from token contract */
    function _onlyToken() internal {
        if (!parents[msg.sender]) {
            parents[msg.sender] = org.isActiveToken(msg.sender);
        }
        require (parents[msg.sender]);
    }

}
