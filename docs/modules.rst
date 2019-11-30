.. _modules:

#######
Modules
#######

Modules are contracts that hook into various methods in :ref:`orgshare` and :ref:`custodian` contracts. They may be used to add custom permissioning logic or extra functionality.

Modules introduce functionality in two ways:

* **Permissions** are methods within the parent contract that the module is able to call into. This can allow actions such as adjusting member limits, transferring shares, or changing the total supply.
* **Hooks** are points within the parent contract's methods where the module will be called. They can be used to introduce extra permissioning requirements or record additional data.

In short: hooks involve calls from a parent contract into a module, permissions involve calls from a module into the parent contract.

It may be useful to view source code for the following contracts while reading this document:

* `Modular.sol <https://github.com/zerolawtech/ZAP-Tech/blob/master/contracts/bases/Modular.sol>`__: Inherited by modular contracts. Provides functionality around attaching, detaching, and calling modules.
* `Module.sol <https://github.com/zerolawtech/ZAP-Tech/blob/master/contracts/modules/bases/Module.sol>`__: Inherited by modules. Provide required functionality for modules to be able to attach or detach.
* `IModules.sol <https://github.com/zerolawtech/ZAP-Tech/blob/master/contracts/interfaces/IModules.sol>`__: Interfaces outlining standard module functionality. Includes inputs for all possible hook methods.

.. note:: In order to minimize gas costs, modules should be attached only when their functionality is required and detached as soon as they are no longer needed.

.. warning:: Depending on the hook and permission settings, modules may be capable of actions such as blocking transfers, moving member shares and altering the total supply. Only attach a module that has been properly auditted, ensure you understand exactly what it does, and be **very** wary of any module that requires permissions outside of it's documented behaviour.

Attaching and Detaching
=======================

Modules are attached or detached via the ``attachModule`` and ``detachModule`` methods. For :ref:`custodian` modules this method is available within ``OwnedCustodian``, for share modules it is called via the associated ``OrgCode`` contract.

Ownership
---------

Each module has an owner which is typically set during deployment.  If the owner is set as an ``OrgCode`` contract, it may be attached to every share associated with that org. In this way a single module can add functionality or permissioning to many tokens.

.. method:: ModuleBase.getOwner()

    Returns the address of the parent contract that the module is owned by.

Declaring Hooks and Permissions
-------------------------------

Hooks and permissions are set the first time a module is attached by calling the following method:

.. method:: ModuleBase.getPermissions()

    Returns the following:

    * ``permissions``: ``bytes4`` array of method signatures within the parent contract that the module is permitted to call.
    * ``hooks``: ``bytes4`` array of method signatures within the module that the parent contract may call into.
    * ``hookBools``: A ``uint256`` bit field. The first 128 bits set if each hook is active initially, the second half sets if each hook should be always called. See :ref:`modules_bitfields`.

Before attaching a module, be sure to check the return value of this function and compare the requested hook points and permissions to those that would be required for the documented functionality of the module. For example, a module intended to block share transfers should not require permission to mint new tokens.

.. _modules_bitfields:

Bit Fields
**********

Solidity uses 8 bits to store a boolean, however only 1 bit is required. To maximize gas efficiency when handling many booleans at once, ``ModuleBase`` uses `bit fields <https://en.wikipedia.org/wiki/Bit_field>`_.

This functionality is mostly handled within internal methods and not user-facing, with one notable exception: in ``ModuleBase.getPermissions`` the return value ``hookBools`` is a set of 2 x 128 byte bit fields given as a single ``uint256``. The first determines if each hook is active initially, the second if the hook method should always be called when it is active.

Each bit field is read **right to left**.

For example: suppose you have declared four hook points for a module. The first, third and fourth should be active initially. The third should always called when active.

Written left to right, the two bit fields will look like:

.. code-block:: python

    active = "1011"
    always = "0010"

Now we must reverse them, and left-pad with zeros to 128 bits:

.. code-block:: python

    >>> active = active[::-1].zfill(128)
    >>> print(active)
    00000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000001101
    >>>
    >>> always = always[::-1].zfill(128)
    >>> print(always)
    00000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000100

Finally we join the two strings, and then convert the value from binary to decimal:

.. code-block:: python

    >>> final = active + always
    >>> int(final, 2)
    4423670769972200025023869896612986748932

The following python function can be used to quickly convert two boolean lists into a uint256 to be used as ``hookBools``:

.. code-block:: python

    def generate_bitfield(active: list, always: list) -> int:
        assert len(active) == len(always)
        assert len(active) <= 128
        active = "".join("1" if i else "0" for i in active[::-1]).zfill(128)
        always = "".join("1" if i else "0" for i in always[::-1]).zfill(128)
        return int(active + always, 2)

.. note:: If all your hooks are to be active initially and always called, the simplest approach is to set ``hookBool = uint256(-1)``. Underflowing uint256 in this way results in 256 bits set to 1.

Checking Active Modules
-----------------------

The following getter is available in the parent contract, to check if a module is currently active:

.. method:: Modular.isActiveModule(address _module)

    Returns ``true`` if a module is currently active on the contract.

Permissioning
=============

**Permissions** are methods within the parent contract that the module is able to call into. This can allow actions such as adjusting member limits, transferring shares, or changing the total supply.

Once attached, modules may call into methods in the parent contract where they have been given permission.

Checking Permissions
--------------------

Any call from a module to a function within the parent contract must first pass a check by this method:

.. method:: Modular.isPermittedModule(address _module, bytes4 _sig)

    Returns ``true`` if a module is active on the contract, and permitted to call the given method signature. Returns ``false`` if not permitted.

Callable Parent Methods
-----------------------

Modules may be permitted to call the following parent methods:

.. note:: When a module calls into the parent contract, it will still trigger any of it's own hooked in methods. With poor contract design you can create infinite loops and effectively break the parent contract functionality as long as the module remains attached.

BookShare
*************

.. method:: BookShare.transferFrom(address _from, address _to, uint256 _value)

    * Permission signature: ``0x23b872dd``

    Transfers shares between two addresses. A module calling ``BookShare.transferFrom`` has the same level of authority as if the call was from the org.

    Calling this method will also call any hooked in ``STModule.checkTransfer``, ``IssuerModule.checkTransfer``, and ``STModule.transferShares`` methods.

.. method:: OrgShare.modifyAuthorizedSupply(uint256 _value)

    * Permission signature: ``0xc39f42ed``

    Modifies the authorized supply.

.. method:: BookShare.mint(address _owner, uint256 _value)

    * Permission signature: ``0x40c10f19``

    Mints new shares to the given address.

    Calling this method will also call any hooked in ``STModule.totalSupplyChanged`` and ``IssuerModule.shareTotalSupplyChanged`` methods.

.. method:: BookShare.burn(address _owner, uint256 _value)

    * Permission signature: ``0x9dc29fac``

    Burns shares at the given address.

    Calling this method will also call any hooked in ``STModule.totalSupplyChanged`` and ``IssuerModule.shareTotalSupplyChanged`` methods.

.. method:: OrgShare.detachModule(address _module)

    * Permission signature: ``0xbb2a8522``

    Detaches a module. This method can only be called directly by a permitted module. For the org to detach a BookShare level module the call must be made via the ``OrgCode`` contract.

CertShare
*********

.. method:: CertShare.transferFrom(address _from, address _to, uint256 _value)

    * Permission signature: ``0x23b872dd``

    Transfers shares between two addresses. A module calling ``CertShare.transferFrom`` has the same level of authority as if the call was from the org.

    Calling this method will also call any hooked in ``NFTModule.checkTransfer``, ``IssuerModule.checkTransfer``, and ``NFTModule.transferShares`` methods.

.. method:: OrgShare.modifyAuthorizedSupply(uint256 _value)

    * Permission signature: ``0xc39f42ed``

    Modifies the authorized supply.

.. method:: CertShare.mint(address _owner, uint48 _value, uint32 _time, bytes2 _tag)

    * Permission signature: ``0x15077ec8``

    Mints new shares to the given address.

    Calling this method will also call any hooked in ``NFTModule.totalSupplyChanged`` and ``IssuerModule.shareTotalSupplyChanged`` methods.

.. method:: CertShare.burn(uint48 _start, uint48 _stop)

    * Permission signature: ``0x9a0d378b``

    Burns shares at the given address.

    Calling this method will also call any hooked in ``NFTModule.totalSupplyChanged`` and ``IssuerModule.shareTotalSupplyChanged`` methods.

.. method:: CertShare.modifyRange(uint48 _pointer, uint32 _time, bytes2 _tag)

    * Permission signature: ``0x712a516a``

    Modifies the time restriction and tag for a single range.

.. method:: CertShare.modifyRanges(uint48 _start, uint48 _stop, uint32 _time, bytes2 _tag)

    * Permission signature: ``0x786500aa``

    Modifies the time restriction and tag for all shares within a given range.

.. method:: OrgShare.detachModule(address _module)

    * Permission signature: ``0xbb2a8522``

    Detaches a module. This method can only be called directly by a permitted module, for the org to detach a BookShare level module the call must be made via the ``OrgCode`` contract.

Custodian
*********

See :ref:`custodian` for more detailed information on these methods.

.. method:: OwnedCustodian.transfer(address _share, address _to, uint256 _value)

    * Permission signature: ``0xbeabacc8``

    Transfers shares from the custodian to a member.

    Calling this method will also call any hooked in ``CustodianModule.sentShares`` methods.

.. method:: OwnedCustodian.transferInternal(address _share, address _from, address _to, uint256 _value)

    * Permission signature: ``0x2f98a4c3``

    Transfers the ownership of shares between members within the Custodian contract.

    Calling this method will also call any hooked in ``CustodianModule.internalTransfer`` methods.

.. method:: OwnedCustodian.detachModule(address _module)

    * Permission signature: ``0xbb2a8522``

    Detaches a module.

.. _modules-hooks-tags:

Hooks and Tags
==============

* **Hooks** are points within the parent contract's methods where the module will be called. They can be used to introduce extra permissioning requirements or record additional data.
* **Tags** are ``bytes2`` values attached to share ranges in ``CertShare``, that allow for more granular hook attachments.

Hooks and tags are defined in the following struct:

::

    struct Hook {
        uint256[256] tagBools;
        bool permitted;
        bool active;
        bool always;
    }

* ``tagBools``: An bit field of length ``2^16``. Defines granular hook points based on specific tags.
* ``permitted``: Can only be set the first time the module is attached. If ``true``, this is an available hook point for the module.
* ``active``: Set during attachment, can be modified by the module. If ``true``, this hook is currently active and will be called during the execution of the parent module.
* ``always``: Set during attachment, can be modified by the module. If ``true``, this hook is always called regardless of the tag value.

Hooks involving shares from an ``CertShare`` contract rely upon tags to determine if the hook point should be called.  A tag is a ``bytes2`` that is assigned to a specific range of tokens.  When a hook point involves a tagged token range, the following three conditions are evaluated to see if the hook method should be called:

* Is ``Hook.always`` set to ``true``?
* Is the first byte of the tag, followed by '00', set to true within ``Hook.tagBools``?
* Is the entire tag set to true within ``Hook.tagBools``?

For example, if the tag is ``0xff32``, the hook point will be called if either ``Hook.always``, ``Hook.tagBools[0xff00]``, or ``Hook.tagBools[0xff32]`` are ``true``.

For hook points that do not involve tags, the module should set ``active`` and ``always`` to true when it wishes to be called.

Setting and Modifying
---------------------

Modules can be designed to modify their own active hook points and tag settings as they progress through different stages of functionality. Avoiding unnecessary external calls from hook points to modules that are no longer relevent helps keep gas costs down.

The following methods are used to modify hook and tag settings. These methods may only be called from the module while it is active.

.. method:: Modular.setHook(bytes4 _sig, bool _active, bool _always)

    Enables or disables a hook point for an active module.

    * ``_sig``: Signature of the hooked method.
    * ``_active``: Boolean for if hooked method is active.
    * ``_always``: Boolean for if hooked method should always be called when active.

.. method:: Modular.setHookTags(bytes4 _sig, bool _value, bytes1 _tagBase, bytes1[] _tags)

    Enables or disables specific tags for a hook point.

    * ``_sig``: Signature of the hooked method.
    * ``_value``: Boolean value to set each tag to.
    * ``_tagBase``: The first byte of the tag to set.
    * ``_tags``: Array of 2nd bytes for the tag.

    For example: if ``_tagBase = 0xff`` and ``_tags = [0x11, 0x22]``, you will modify tags ``0xff00``, ``0xff11``, and ``0xff22``.

.. method:: Modular.clearHookTags(bytes4 _sig, bytes1[] _tagBase)

    Disables many tags for a given hook point.

    * ``_sig``: Signature of the hooked method.
    * ``_tagBase``: Array of first bytes for tags to disable.

    For example: if ``_tagBase = [0xee, 0xff]`` it will clear tags ``0xee00``, ``0xee01`` ... ``0xeeff``, and ``0xff00``, ``0xff01`` ... ``0xffff``.

Hookable Module Methods
-----------------------

The following methods may be included in modules and given as hook points via ``getPermissions``.

Inputs and outputs of all hook points are also defined in `IModules.sol <https://github.com/zerolawtech/ZAP-Tech/blob/master/contracts/interfaces/IModules.sol>`__. This can be a useful starting point when writing your own modules.

BookShare
*************

.. method:: STModule.checkTransfer(address[2] _addr, bytes32 _authID, bytes32[2] _id, uint8[2] _rating, uint16[2] _country, uint256 _value)

    * Hook signature: ``0x70aaf928``

    Called by ``BookShare.checkTransfer`` to verify if a transfer is permitted.

    * ``_addr``: Sender and receiver addresses.
    * ``_authID``: ID of the authority who wishes to perform the transfer. It may differ from the sender ID if the check is being performed prior to a ``transferFrom`` call.
    * ``_id``: Sender and receiver IDs.
    * ``_rating``: Sender and receiver member ratings.
    * ``_country``: Sender and receiver countriy codes.
    * ``_value``: Amount to be transferred.

.. method:: STModule.transferShares(address[2] _addr, bytes32[2] _id, uint8[2] _rating, uint16[2] _country, uint256 _value)

    * Hook signature: ``0x0675a5e0``

    Called after a share transfer has completed successfully with ``BookShare.transfer`` or ``BookShare.transferFrom``.

    * ``_addr``: Sender and receiver addresses.
    * ``_id``: Sender and receiver IDs.
    * ``_rating``: Sender and receiver member ratings.
    * ``_country``: Sender and receiver country codes.
    * ``_value``: Amount that was transferred.

.. method:: STModule.transferSharesCustodian(address _custodian, bytes32[2] _id, uint8[2] _rating, uint16[2] _country, uint256 _value)

    * Hook signature: ``0xdc9d1da1``

    Called after an internal custodian share transfer has completed with ``Custodian.transferInternal``.

    * ``_custodian``: Address of the custodian contract.
    * ``_id``: Sender and receiver IDs.
    * ``_rating``: Sender and receiver member ratings.
    * ``_country``: Sender and receiver country codes.
    * ``_value``: Amount that was transferred.

.. method:: STModule.totalSupplyChanged(address _addr, bytes32 _id, uint8 _rating, uint16 _country, uint256 _old, uint256 _new)

    * Hook signature: ``0x741b5078``

    Called after the total supply has been modified by ``BookShare.mint`` or ``BookShare.burn``.

    * ``_addr``: Address where balance has changed.
    * ``_id``: ID that the address is associated to.
    * ``_rating``: Member rating.
    * ``_country``: Member country code.
    * ``_old``: Previous share balance at the address.
    * ``_new``: New share balance at the address.

CertShare
*********

``CertShare`` contracts also include all the hook points for ``BookShare``.

Hook points that are unique to ``CertShare`` also perform a check against the tag of the related range before calling to a module.

.. method:: NFTModule.checkTransferRange(address[2] _addr, bytes32 _authID, bytes32[2] _id, uint8[2] _rating, uint16[2] _country, uint48[2] _range)

    * Hook signature: ``0x2d79c6d7``

    Called by ``CertShare.checkTransfer`` and ``CertShare.transferRange`` to verify if the transfer of a specific range is permitted.

    * ``_addr``: Sender and receiver addresses.
    * ``_authID``: ID of the authority who wishes to perform the transfer. It may differ from the sender ID if the check is being performed prior to a ``transferFrom`` call.
    * ``_id``: Sender and receiver IDs.
    * ``_rating``: Sender and receiver member ratings.
    * ``_country``: Sender and receiver countriy codes.
    * ``_range``: Start and stop index of share range.

.. method:: NFTModule.transferShareRange(address[2] _addr, bytes32[2] _id, uint8[2] _rating, uint16[2] _country, uint48[2] _range)

    * Hook signature: ``0x244d5002``

    Called after a share range has been transferred successfully with ``CertShare.transfer`, ``CertShare.transferFrom`` or ``CertShare.transferRange``.

    * ``_addr``: Sender and receiver addresses.
    * ``_id``: Sender and receiver IDs.
    * ``_rating``: Sender and receiver member ratings.
    * ``_country``: Sender and receiver countriy codes.
    * ``_range``: Start and stop index of share range.

Custodian
*********

.. method:: CustodianModule.sentShares(address _share, address _to, uint256 _value)

    * Hook signature: ``0xa110724f``

    Called after shares have been transferred out of a Custodian via ``Custodian.transfer``.

    * ``_share``: Address of token that was sent.
    * ``_to``: Address of the recipient.
    * ``_value``: Number of shares that were sent.

.. method:: CustodianModule.receivedShares(address _share, address _from, uint256 _value)

    * Hook signature: ``0xa000ff88``

    Called after a shares have been transferred into a Custodian.

    * ``_share``: Address of token that was received.
    * ``_from``: Address of the sender.
    * ``_value``: Number of shares that were received.

.. method:: CustodianModule.internalTransfer(address _share, address _from, address _to, uint256 _value)

    * Hook signature: ``0x44a29e2a``

    Called after an internal transfer of ownership within the Custodian contract via ``Custodian.transferInternal``.

    * ``_share``: Address of token that was received.
    * ``_from``: Address of the sender.
    * ``_to``: Address of the recipient.
    * ``_value``: Number of shares that were received.

Module Execution Flows
======================

The following diagrams show the sequence in which modules are called during some of the more complex methods.

.. figure:: flow1.png
    :align: center
    :alt: BookShare
    :figclass: align-center

    BookShare

.. figure:: flow2.png
    :align: center
    :alt: CertShare
    :figclass: align-center

    CertShare

Events
======

Contracts that include modular functionality have the following events:

.. method:: Modular.ModuleAttached(address module, bytes4[] hooks, bytes4[] permissions)

    Emitted whenever a module is attached with ``Modular.attachModule``.

.. method:: Modular.ModuleHookSet(address module, bytes4 hook, bool active, bool always)

    Emitted once for each hook that is set when a module is attached with ``Modular.attachModule``.

.. method:: Modular.ModuleDetached(address module)

    Emitted when a module is detached with ``Modular.detachModule``.

Use Cases
=========

The wide range of functionality that modules can hook into and access allows for many different applications. Some examples include: crowdsales, country/time based share locks, right of first refusal enforcement, voting rights, dividend payments, tender offers, and bond redemption.

We have included some sample modules on `GitHub <https://github.com/zerolawtech/ZAP-Tech/tree/master/contracts/modules>`__ as examples to help understand module development and demonstrate the range of available functionality.
