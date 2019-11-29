.. _owned-custodian:

##############
OwnedCustodian
##############


``OwnedCustodian`` is a standard custodian implementation that is controlled and maintained by a known legal entity. Use cases for this contract may include broker/dealers or centralized exchanges.

Owned Custodian contracts include the standard ZAP :ref:`multisig` and :ref:`modules` functionality. See the respective documents for detailed information on these components.

It may be useful to view the `OwnedCustodian.sol <https://github.com/zerolawtech/ZAP-Tech/blob/master/contracts/custodians/OwnedCustodian.sol>`__ source code for the following contracts while reading this document.

Deployment
==========

The constructor declares the owner as per standard :ref:`multisig`.

.. method:: OwnedCustodian.constructor(address[] _owners, uint32 _threshold)

    * ``_owners``: One or more addresses to associate with the contract owner. The address deploying the contract is not implicitly included within the owner list.
    * ``_threshold``: The number of calls required for the owner to perform a multi-sig action.

    The ID of the owner is generated as a keccak of the contract address and available from the public getter ``OwnedCustodian.ownerID``.

    Once deployed, the custodian must be approved by an ``OrgCode`` before it can receive shares associated with that contract.

    .. code-block:: python

        >>> cust = accounts[0].deploy(OwnedCustodian, [accounts[0]], 1)

        Transaction sent: 0x11540767a467504e3ddd03c8c2423840a69bd82a6f28db33ea869570b87486f0
        OwnedCustodian.constructor confirmed - block: 13   gas used: 3326386 (41.58%)
        OwnedCustodian deployed at: 0x3BcC6Ad6CFbB1997eb9DA056946FC38a6b5E270D
        <OwnedCustodian Contract object '0x3BcC6Ad6CFbB1997eb9DA056946FC38a6b5E270D'>

Public Constants
================

The following public variables cannot be changed after contract deployment.

.. method:: OwnedCustodian.ownerID

    The bytes32 ID hash of the contract owner.

    .. code-block:: python

        >>> cust.ownerID()
        0x8be1198d7f1848ebeddb3f807146ce7d26e63d3b6715f27697428ddb52db9b63

Balances and Transfers
======================

Checking Balances
-----------------

Custodied member balances are tracked within the share contract. They can be queried using ``OrgShare.custodianBalanceOf`` or ``OwnedCustodian.balanceOf``.

.. method:: OwnedCustodian.balanceOf(address _share, address _owner)

    Returns the custodied share balance for a given member address.

    .. code-block:: python

        >>> cust.balanceOf(share, accounts[1])
        5000
        >>> share.custodianBalanceOf(accounts[1], cust)
        5000

Checking Transfer Permissions
-----------------------------

.. method:: OwnedCustodian.checkCustodianTransfer(address _share, address _from, address _to, uint256 _value)

    Checks if an internal transfer is permitted.

    * ``_share``: Share address
    * ``_from``: Sender address
    * ``_to``: Receiver address
    * ``_value``: Amount to transfer

    Returns ``true`` if the transfer is permitted. If it is not, the call will revert with the reason given in the error string.

    Permissioning checks for custodial transfers are identical to those of normal transfers.

    .. code-block:: python

        >>> cust.balanceOf(share, accounts[1])
        2000
        >>> cust.checkCustodianTransfer(share, accounts[1], accounts[2], 1000)
        True
        >>> cust.checkCustodianTransfer(share, accounts[1], accounts[2], 5000)
        File "contract.py", line 282, in call
          raise VirtualMachineError(e)
        VirtualMachineError: VM Exception while processing transaction: revert Insufficient Custodial Balance

Transferring Shares
-------------------

.. method:: OwnedCustodian.transferInternal(address _share, address _from, address _to, uint256 _value)

    * ``_share``: BookShare address
    * ``_from``: Sender address
    * ``_to``: Receiver address
    * ``_value``: Amount to transfer

    .. code-block:: python

        >>> cust.transferInternal(share, accounts[1], accounts[2], 5000, {'from': accounts[0]})

        Transaction sent: 0x1c5cf1d01d2d5f9b9d9e801d8e2a0b9b2eb50fa11fbe03864b69ccf0fe2c03fc
        OwnedCustodian.transferInternal confirmed - block: 17   gas used: 189610 (2.37%)
        <Transaction object '0x1c5cf1d01d2d5f9b9d9e801d8e2a0b9b2eb50fa11fbe03864b69ccf0fe2c03fc'>

.. method:: OwnedCustodian.transfer(address _share, address _to, uint256 _value)

    Transfers shares out of the Custodian contract.

    * ``_share``: Share address
    * ``_to``:  Receipient address
    * ``_value``: Amount to transfer

    .. code-block:: python

        >>> cust.transfer(share, accounts[2], 5000, {'from': accounts[0]})

        Transaction sent: 0x227f7c24d68d63aa567c16458e039a283481ef5fd79d8b9e48c88b033ff18f79
        OwnedCustodian.transfer confirmed - block: 18   gas used: 149638 (1.87%)
        <Transaction object '0x227f7c24d68d63aa567c16458e039a283481ef5fd79d8b9e48c88b033ff18f79'>

.. _custodian-modules:

Modules
=======

See the :ref:`modules` documentation for information module funtionality and development.

.. note:: For Custodians that require bespoke functionality it is preferrable to attach modules than to modify the core contract. Inaccurate balance reporting could enable a range of exploits, and so Issuers should be very wary of permitting any Custodian that uses a non-standard contract.

.. method:: OwnedCustodian.attachModule(address _module)

    Attaches a module to the custodian. Only callable by the owner or an approved authority.

    .. code-block:: python

        >>> cust.attachModule(module, {'from': accounts[0]})

        Transaction sent: 0x7123091c968dbe0c279aa6850c668534aef327972a08d65b67779108cbaa9b45
        OwnedCustodian.attachModule confirmed - block: 14   gas used: 212332 (2.65%)
        <Transaction object '0x7123091c968dbe0c279aa6850c668534aef327972a08d65b67779108cbaa9b45'>

.. method:: OwnedCustodian.detachModule(address _module)

    Detaches a module. A module may call to detach itself, but not other modules.

    .. code-block:: python

        >>> cust.detachModule(module, {'from': accounts[0]})

        Transaction sent: 0x7123091c968dbe0c279aa6850c668534aef327972a08d65b67779108cbaa9b45
        OwnedCustodian.detachhModule confirmed - block: 15   gas used: 43828 (2.65%)
        <Transaction object '0x7123091c968dbe0c279aa6850c668534aef327972a08d65b67779108cbaa9b45'>

.. method:: Modular.isActiveModule(address _module)

     Returns ``true`` if a module is currently active on the contract, ``false`` if not.

    .. code-block:: python

        >>> cust.isActiveModule(cust_module)
        True
        >>> cust.isActiveModule(other_module)
        False

.. method:: Modular.isPermittedModule(address _module, bytes4 _sig)

    Returns ``true`` if a module is active on the contract, and permitted to call the given method signature. Returns ``false`` if not permitted.

    .. code-block:: python

        >>> cust.isPermittedModule(cust_module, "0x40c10f19")
        True
        >>> cust.isPermittedModule(cust_module, "0xc39f42ed")
        False

Events
======

``OwnedCustodian`` includes the following events:

.. method:: OwnedCustodian.ReceivedShares(address indexed share, address indexed from, uint256 amount)

    Emitted by ``OwnedCustodian.receiveTransfer`` when shares are sent into the custodian contract.

.. method:: OwnedCustodian.SentShares(address indexed share, address indexed to, uint256 amount)

    Emitted by ``OwnedCustodian.transfer`` after shares are sent out of the custodian contract.

.. method:: OwnedCustodian.TransferOwnership(address indexed share, address indexed from, address indexed to, uint256 value)

    Emitted by ``OwnedCustodia.transferInternal`` after an internal change of beneficial ownership.