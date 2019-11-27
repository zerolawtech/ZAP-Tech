pragma solidity 0.4.25;

/**
    @notice Common interface for all modules
    @dev
        These are the minimum required methods that MUST be included to
        attach the module to the parent contract
*/
interface IBaseModule {

    /**
        @notice Defines the permissions for a module when it is attached
        @dev https://sft-protocol.readthedocs.io/en/latest/modules.html#ModuleBase.getPermissions
        @return permissions array, hooks array, hook attachments bitfield
     */
    function getPermissions()
        external
        pure
        returns (
            bytes4[] permissions,
            bytes4[] hooks,
            uint256 hookBools
        );
    function getOwner() external view returns (address);
}

/**
    @notice BookShare module interface
    @dev These are all the possible hook point methods for share modules
*/
contract IBookShareModule is IBaseModule {

    function share() external returns (address);

    /**
        @notice Check if a transfer is possible
        @dev
            Called before a share transfer to check if it is permitted
            Hook signature: 0x70aaf928
        @param _addr sender and receiver addresses
        @param _authID id hash of caller
        @param _id sender and receiver id hashes
        @param _rating sender and receiver member ratings
        @param _country sender and receiver country codes
        @param _value amount of shares to be transfered
        @return bool success
     */
    function checkTransfer(
        address[2] _addr,
        bytes32 _authID,
        bytes32[2] _id,
        uint8[2] _rating,
        uint16[2] _country,
        uint256 _value
    )
        external
        view
        returns (bool);

    /**
        @notice Share transfer
        @dev
            Called a share transfer has completed
            Hook signature: 0x0675a5e0
        @param _addr sender and receiver addresses
        @param _id sender and receiver id hashes
        @param _rating sender and receiver member ratings
        @param _country sender and receiver country codes
        @param _value amount of shares to be transfered
        @return bool success
     */
    function transferShares(
        address[2] _addr,
        bytes32[2] _id,
        uint8[2] _rating,
        uint16[2] _country,
        uint256 _value
    )
        external
        returns (bool);

    /**
        @notice Share custodial internal transfer
        @dev
            Called a custodian internal share transfer has completed
            Hook signature: 0xdc9d1da1
        @param _custodian custodian address
        @param _addr sender and receiver addresses
        @param _id sender and receiver id hashes
        @param _rating sender and receiver member ratings
        @param _country sender and receiver country codes
        @param _value amount of shares to be transfered
        @return bool success
     */
    function transferSharesCustodian(
        address _custodian,
        address[2] _addr,
        bytes32[2] _id,
        uint8[2] _rating,
        uint16[2] _country,
        uint256 _value
    )
        external
        returns (bool);

    /**
        @notice Total supply changed
        @dev
            Called after the total supply has been changed via minting or burning
            Hook signature: 0x741b5078
        @param _addr Address where balance has changed
        @param _id ID that the address is associated to
        @param _rating Member rating
        @param _country Member country code
        @param _old Previous share balance at the address
        @param _new New share balance at the address
        @return bool success
     */
    function totalSupplyChanged(
        address _addr,
        bytes32 _id,
        uint8 _rating,
        uint16 _country,
        uint256 _old,
        uint256 _new
    )
        external
        returns (bool);
}

/**
    @notice CertShare module interface
    @dev
        These are all the possible hook point methods for CertShare modules
        All BookShare module hook points are also available
*/
contract ICertShareModule is IBookShareModule {

    /**
        @notice Check if a transfer is possible
        @dev
            Called before a share transfer to check if it is permitted
            Hook signature: 0x70aaf928
        @param _addr sender and receiver addresses
        @param _authID id hash of caller
        @param _id sender and receiver id hashes
        @param _rating sender and receiver member ratings
        @param _country sender and receiver country codes
        @param _range start and stop index of transferred range
        @return bool success
     */
    function checkTransferRange(
        address[2] _addr,
        bytes32 _authID,
        bytes32[2] _id,
        uint8[2] _rating,
        uint16[2] _country,
        uint48[2] _range
    )
        external
        view
        returns (bool);

    /**
        @notice Share range transfer
        @dev
            Called a range of shares has been transferred
            Hook signature: 0x244d5002 (taggable)
        @param _addr sender and receiver addresses
        @param _id sender and receiver id hashes
        @param _rating sender and receiver member ratings
        @param _country sender and receiver country codes
        @param _range start and stop index of transferred range
        @return bool success
     */
    function transferShareRange(
        address[2] _addr,
        bytes32[2] _id,
        uint8[2] _rating,
        uint16[2] _country,
        uint48[2] _range
    )
        external
        returns (bool);

}

/**
    @notice Custodian module interface
    @dev These are all the possible hook point methods for custodian modules
*/
contract ICustodianModule is IBaseModule {

    /**
        @notice Custodian sent shares
        @dev
            Called after a successful share transfer from the custodian.
            Hook signature: 0xa110724f
        @param _share Share address
        @param _to Recipient address
        @param _value Amount of shares transfered
        @return bool success
     */
    function sentShares(
        address _share,
        address _to,
        uint256 _value
    )
        external
        returns (bool);

    /**
        @notice Custodian received shares
        @dev
            Called after a successful share transfer to the custodian.
            Hook signature: 0xa000ff88
        @param _share Share address
        @param _from Sender address
        @param _value Amount of shares transfered
        @return bool success
     */
    function receivedShares(
        address _share,
        address _from,
        uint256 _value
    )
        external
        returns (bool);

    /**
        @notice Custodian internal share transfer
        @dev
            Called after a successful internal share transfer by the custodian
            Hook signature: 0x44a29e2a
        @param _share Share address
        @param _from Sender address
        @param _value Amount of shares transfered
        @return bool success
     */
    function internalTransfer(
        address _share,
        address _from,
        address _to,
        uint256 _value
    )
        external
        returns (bool);
}
