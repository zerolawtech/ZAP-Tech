pragma solidity 0.4.25;

import "../bases/Modular.sol";
import "../bases/MultiSig.sol";

import "../interfaces/IOrgShare.sol";

/** @title Owned Custodian Contract */
contract OwnedCustodian is Modular, MultiSig {

    event ReceivedShares(
        address indexed share,
        address indexed from,
        uint256 amount
    );
    event SentShares(
        address indexed share,
        address indexed to,
        uint256 amount
    );
    event TransferOwnership(
        address indexed share,
        address indexed from,
        address indexed to,
        uint256 value
    );

    /**
        @notice Custodian constructor
        @param _owners Array of addresses to associate with owner
        @param _threshold multisig threshold for owning authority
     */
    constructor(
        address[] _owners,
        uint32 _threshold
    )
        MultiSig(_owners, _threshold)
        public
    {

    }

    /**
        @notice Fetch an member's current share balance held by the custodian
        @param _share address of the OrgShare contract
        @param _owner member address
        @return integer
     */
    function balanceOf(
        IOrgShareBase _share,
        address _owner
    )
        external
        view
        returns (uint256)
    {
        return _share.custodianBalanceOf(address(this), _owner);
    }


    /**
        @notice View function to check if an internal transfer is possible
        @param _share Address of the share to transfer
        @param _from Sender address
        @param _to Recipient address
        @param _value Amount of shares to transfer
        @return bool success
     */
    function checkCustodianTransfer(
        IOrgShareBase _share,
        address _from,
        address _to,
        uint256 _value
    )
        external
        view
        returns (bool)
    {
        return _share.checkTransferCustodian(address(this), _from, _to, _value);
    }

    /**
        @notice Transfers shares out of the custodian contract
        @dev callable by custodian authorities and modules
        @param _share Address of the share to transfer
        @param _to Address of the recipient
        @param _value Amount to transfer
        @return bool success
     */
    function transfer(
        IOrgShareBase _share,
        address _to,
        uint256 _value
    )
        external
        returns (bool)
    {
        if (
            /* msg.sig = 0xbeabacc8 */
            !isPermittedModule(msg.sender, msg.sig) &&
            !_checkMultiSig()
        ) {
            return false;
        }
        require(_share.transfer(_to, _value));
        /* bytes4 signature for custodian module sentShares() */
        require(_callModules(
            0xa110724f,
            0x00,
            abi.encode(_share, _to, _value)
        ));
        emit SentShares(_share, _to, _value);
        return true;
    }

    /**
        @notice Add a new share owner
        @dev called by OrgCode when shares are transferred to a custodian
        @param _from Member address
        @param _value Amount transferred
        @return bool success
     */
    function receiveTransfer(
        address _from,
        uint256 _value
    )
        external
        returns (bool)
    {

        /* bytes4 signature for custodian module receivedShares() */
        require(_callModules(
            0xa000ff88,
            0x00,
            abi.encode(msg.sender, _from, _value)
        ));
        emit ReceivedShares(msg.sender, _from, _value);
        return true;
    }

    /**
        @notice Transfer share ownership within the custodian
        @dev Callable by custodian authorities and modules
        @param _share Address of the share to transfer
        @param _from Sender address
        @param _to Recipient address
        @param _value Amount of shares to transfer
        @return bool success
     */
    function transferInternal(
        IOrgShareBase _share,
        address _from,
        address _to,
        uint256 _value
    )
        external
        returns (bool)
    {
        if (
            /* msg.sig = 0x2f98a4c3 */
            !isPermittedModule(msg.sender, msg.sig) &&
            !_checkMultiSig()
        ) {
            return false;
        }
        _share.transferCustodian([_from, _to], _value);
        /* bytes4 signature for custodian module internalTransfer() */
        require(_callModules(
            0x44a29e2a,
            0x00,
            abi.encode(_share, _from, _to, _value)
        ));
        emit TransferOwnership(_share, _from, _to, _value);
        return true;
    }

    /**
        @notice Attach a module
        @dev
            Modules have a lot of permission and flexibility in what they
            can do. Only attach a module that has been properly auditted and
            where you understand exactly what it is doing.
            https://sft-protocol.readthedocs.io/en/latest/modules.html
        @param _module Address of the module contract
        @return bool success
     */
    function attachModule(
        IBaseModule _module
    )
        external
        returns (bool)
    {
        if (!_checkMultiSig()) return false;
        require(_module.getOwner() == address(this)); // dev: wrong owner
        _attachModule(_module);
        return true;
    }

    /**
        @notice Detach a module
        @dev This function may also be called by the module itself.
        @param _module Address of the module contract
        @return bool success
     */
    function detachModule(
        address _module
    )
        external
        returns (bool)
    {
        if (_module != msg.sender) {
            if (!_checkMultiSig()) return false;
        } else {
            /* msg.sig = 0xbb2a8522 */
            require(isPermittedModule(msg.sender, msg.sig));
        }
        _detachModule(_module);
        return true;
    }

}
