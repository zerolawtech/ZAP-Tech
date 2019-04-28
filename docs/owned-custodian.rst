.. _owned-custodian:

##############
OwnedCustodian
##############


``OwnedCustodian`` is a standard custodian implementation that is controlled and maintained by a known legal entity. Use cases for this contract may include broker/dealers or centralized exchanges.

Owned Custodian contracts include the standard SFT protocol :ref:`multisig` and :ref:`modules` functionality. See the respective documents for detailed information on these components.

It may be useful to view the `OwnedCustodian.sol <https://github.com/HyperLink-Technology/SFT-Protocol/tree/master/contracts/custodians/OwnedCustodian.sol>`__ source code for the following contracts while reading this document.

Deployment
==========

The constructor declares the owner as per standard :ref:`multisig`.

.. method:: OwnedCustodian.constructor(address[] _owners, uint32 _threshold)

    * ``_owners``: One or more addresses to associate with the contract owner. The address deploying the contract is not implicitly included within the owner list.
    * ``_threshold``: The number of calls required for the owner to perform a multi-sig action.

    The ID of the owner is generated as a keccak of the contract address and available from the public getter ``OwnedCustodian.ownerID``.

    Once deployed, the custodian must be approved by an ``IssuingEntity`` before it can receive tokens associated with that contract.

    .. code-block:: python

        >>> cust = accounts[0].deploy(OwnedCustodian, [accounts[0]], 1)

        Transaction sent: 0x11540767a467504e3ddd03c8c2423840a69bd82a6f28db33ea869570b87486f0
        OwnedCustodian.constructor confirmed - block: 13   gas used: 3326386 (41.58%)
        OwnedCustodian deployed at: 0x3BcC6Ad6CFbB1997eb9DA056946FC38a6b5E270D
        <OwnedCustodian Contract object '0x3BcC6Ad6CFbB1997eb9DA056946FC38a6b5E270D'>

Public Constants
================

.. method:: OwnedCustodian.ownerID

    The bytes32 ID hash of the contract owner.

    .. code-block:: python

        >>> cust.ownerID()
        0x8be1198d7f1848ebeddb3f807146ce7d26e63d3b6715f27697428ddb52db9b63


Balances and Transfers
======================

Checking Balances
=================

Custodied investor balances are tracked within the token contract. They can be queried using ``TokenBase.custodianBalanceOf`` or ``OwnedCustodian.balanceOf``.

.. method:: OwnedCustodian.balanceOf(address _token, address _owner)

    Returns the custodied token balance for a given investor address.

    .. code-block:: python

        >>> cust.balanceOf(token, accounts[1])
        5000
        >>> token.custodianBalanceOf(accounts[1], cust)
        5000

Checking Transfer Permissions
============================-

.. method:: OwnedCustodian.checkCustodianTransfer(address _token, address _from, address _to, uint256 _value)

    Checks if an internal transfer is permitted.

    * ``_token``: Token address
    * ``_from``: Sender address
    * ``_to``: Receiver address
    * ``_value``: Amount to transfer

    Returns ``true`` if the transfer is permitted. If it is not, the call will revert with the reason given in the error string.

    Permissioning checks for custodial transfers are identical to those of normal transfers.

Transferring Tokens
===================

.. method:: OwnedCustodian.transferInternal(address _token, address _from, address _to, uint256 _value)

    * ``_token``: SecurityToken address
    * ``_from``: Sender address
    * ``_to``: Receiver address
    * ``_value``: Amount to transfer

.. method:: OwnedCustodian.transfer(address _token, address _to, uint256 _value)

    Transfers tokens out of the Custodian contract.

    * ``_token``: Token address
    * ``_to``:  Receipient address
    * ``_value``: Amount to transfer

.. _custodian-modules:

Modules
=======

See the :ref:`modules` documentation for information module funtionality and development.

.. note:: For Custodians that require bespoke functionality it is preferrable to attach modules than to modify the core contract. Inaccurate balance reporting could enable a range of exploits, and so Issuers should be very wary of permitting any Custodian that uses a non-standard contract.

.. method:: OwnedCustodian.attachModule(address _module)

    Attaches a module to the custodian. Only callable by the owner or an approved authority.

.. method:: OwnedCustodian.detachModule(address _module)

    Detaches a module. A module may call to detach itself, but not other modules.

.. method:: OwnedCustodian.isActiveModule(address _module)

     Returns ``true`` if a module is currently active on the contract, ``false`` if not.

.. method:: Modular.isPermittedModule(address _module, bytes4 _sig)

    Returns ``true`` if a module is active on the contract, and permitted to call the given method signature. Returns ``false`` if not permitted.


Events
======

