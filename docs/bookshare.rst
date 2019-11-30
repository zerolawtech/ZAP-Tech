.. _security-share:

#########
BookShare
#########

The ``BookShare`` contract represents a single class of fungible, non-certificated "book entry" securities.  It is based on the `ERC20 Token
Standard <https://eips.ethereum.org/EIPS/eip-20>`__, with an additional ``checkTransfer`` function available to verify if transfers will succeed.

Share contracts include :ref:`multisig` and :ref:`modules` via the associated :ref:`org-code` contract. See the respective documents for more detailed information.

It may be useful to view source code for the following contracts while reading this document:

* `BookShare.sol <https://github.com/zerolawtech/ZAP-Tech/blob/master/contracts/BookShare.sol>`__: the deployed contract, with functionality specific to ``BookShare``.
* `OrgShare.sol <https://github.com/zerolawtech/ZAP-Tech/blob/master/contracts/bases/Share.sol>`__: the base contract that both ``BookShare`` and ``CertShare`` inherit functionality from.

Deployment
==========

.. method:: OrgShare.constructor(address _org, string _name, string _symbol, uint256 _authorizedSupply)

    * ``_org``: The address of the ``OrgCode`` associated with this share.
    * ``_name``: The full name of the share.
    * ``_symbol``: The ticker symbol for the share.
    * ``_authorizedSupply``: The initial authorized share supply.

    After the contract is deployed it must be associated with the org via ``OrgCode.addShare``. It is not possible to mint shares until this is done.

    At the time of deployment the initial authorized supply is set, and the total supply is left as 0. The org may then mint shares by calling ``BookShare.mint`` directly or via a module. See :ref:`bookshare-mint-burn`.

    .. code-block:: python

        >>> share = accounts[0].deploy(BookShare, org, "Test Share", "TST", 1000000)

        Transaction sent: 0x4d2bbbc01d026de176bf5749e6e1bd22ba6eb40a225d2a71390f767b2845bacb
        BookShare.constructor confirmed - block: 4   gas used: 3346083 (41.83%)
        BookShare deployed at: 0x099c68D84815532A2C33e6382D6aD2C634E92ef6
        <BookShare Contract object '0x099c68D84815532A2C33e6382D6aD2C634E92ef6'>

Public Constants
================

The following public variables cannot be changed after contract deployment.

.. method:: OrgShare.name

    The full name of the security share.

    .. code-block:: python

        >>> share.name()
        Test Share

.. method:: OrgShare.symbol

    The ticker symbol for the share.

    .. code-block:: python

        >>> share.symbol()
        TST

.. method:: OrgShare.decimals

    The number of decimal places for the share. In the standard ZAP implementation this is set to 0.

    .. code-block:: python

        >>> share.decimals()
        0

.. method:: OrgShare.ownerID

    The bytes32 ID hash of the org associated with this share.

    .. code-block:: python

        >>> share.ownerID()
        0x8be1198d7f1848ebeddb3f807146ce7d26e63d3b6715f27697428ddb52db9b63

.. method:: OrgShare.orgCode()

    The address of the associated OrgCode contract.

    .. code-block:: python

        >>> share.orgCode()
        0x40b49Ad1B8D6A8Df6cEdB56081D51b69e6569e06

.. _bookshare-mint-burn:

Total Supply, Minting and Burning
=================================

Authorized Supply
-----------------

Along with the ERC20 standard ``totalSupply``, share contracts include an ``authorizedSupply`` that represents the maximum allowable total supply. The org may mint new tokens using ``BookShare.mint`` until the total supply is equal to the authorized supply. The initial authorized supply is set during deployment and may be increased later using ``OrgShare.modifyAuthorizedSupply``.

A :ref:`governance` module can be deployed to dictate when the org is allowed to modify the authorized supply.

.. method:: OrgShare.modifyAuthorizedSupply(uint256 _value)

    Sets the authorized supply. The value may never be less than the current total supply.

    This method is callable directly by the org, implementing multi-sig via ``MultiSig.checkMultiSigExternal``. It may also be called by a permitted module.

    If a :ref:`governance` module has been set on the associated ``OrgCode``, it must provide approval whenever this method is called.

    Emits the ``AuthorizedSupplyChanged`` event.

    .. code-block:: python

        >>> share.modifyAuthorizedSupply(2000000, {'from': accounts[0]})

        Transaction sent: 0x83b7a23e1bc1248445b64f275433add538f05336a4fe07007d39edbd06e1f476
        BookShare.modifyAuthorizedSupply confirmed - block: 13   gas used: 46666 (0.58%)
        <Transaction object '0x83b7a23e1bc1248445b64f275433add538f05336a4fe07007d39edbd06e1f476'>

Minting and Burning
-------------------

.. method:: BookShare.mint(address _owner, uint256 _value)

    Mints new shares at the given address.

    * ``_owner``: Account balance to mint shares to.
    * ``_value``: Number of shares to mint.

    A ``Transfer`` even will fire showing the new shares as transferring from ``0x00`` and the total supply will increase. The new total supply cannot exceed ``authorizedSupply``.

    This method is callable directly by the org, implementing multi-sig via ``MultiSig.checkMultiSigExternal``. It may also be called by a permitted module.

    Modules can hook into this method via ``STModule.totalSupplyChanged``.

    .. code-block:: python

        >>> share.mint(accounts[1], 5000, {'from': accounts[0]})

        Transaction sent: 0x77ec76224d90763641971cd61e99711c911828053612cc16eb2e5d7faa20815e
        BookShare.mint confirmed - block: 14   gas used: 229092 (2.86%)
        <Transaction object '0x77ec76224d90763641971cd61e99711c911828053612cc16eb2e5d7faa20815e'>

.. method:: BookShare.burn(address _owner, uint256 _value)

    Burns shares at the given address.

    * ``_owner``: Account balance to burn shares from.
    * ``_value``: Number of shares to burn.

    A ``Transfer`` event is emitted showing the new shares as transferring to ``0x00`` and the total supply will increase.

    This method is callable directly by the org, implementing multi-sig via ``MultiSig.checkMultiSigExternal``. It may also be called by a permitted module.

    Modules can hook into this method via ``STModule.totalSupplyChanged``.

    .. code-block:: python

        >>> share.burn(accounts[1], 1000, {'from': accounts[0]})

        Transaction sent: 0x5414b31e3e44e657ed5ee04c0c6e4c673ab2c6300f392dfd7c282b348db0bbc7
        BookShare.burn confirmed - block: 15   gas used: 48312 (0.60%)
        <Transaction object '0x5414b31e3e44e657ed5ee04c0c6e4c673ab2c6300f392dfd7c282b348db0bbc7'>

Getters
-------

.. method:: OrgShare.totalSupply

    Returns the current total supply of shares.

    .. code-block:: python

        >>> share.totalSupply()
        5000

.. method:: OrgShare.authorizedSupply

    Returns the maximum authorized total supply of shares. Whenever the authorized supply exceeds the total supply, the org may mint new tokens using ``BookShare.mint``.

    .. code-block:: python

        >>> share.authorizedSupply()
        2000000

.. method:: OrgShare.treasurySupply

    Returns the number of shares held by the org. Equivalent to calling ``OrgShare.balanceOf(org)``.

    .. code-block:: python

        >>> share.treasurySupply()
        1000
        >>> share.balanceOf(org)
        1000


.. method:: OrgShare.circulatingSupply

    Returns the total supply, less the amount held by the org.

    .. code-block:: python

        >>> share.circulatingSupply()
        4000

Balances and Transfers
======================

BookShare uses the standard ERC20 methods for share transfers, however their functionality differs slightly due to transfer permissioning requirements.

Checking Balances
-----------------

.. method:: OrgShare.balanceOf(address)

    Returns the share balance for a given address.

    .. code-block:: python

        >>> share.balanceOf(accounts[1])
        4000

.. method:: OrgShare.custodianBalanceOf(address _owner, address _cust)

    Returns the custodied share balance for a given address.

    .. code-block:: python

        >>> share.custodianBalanceOf(accounts[1], cust)
        0

.. method:: OrgShare.allowance(address _owner, address _spender)

    Returns the amount of shares that ``_spender`` may transfer from ``_owner``'s balance using ``BookShare.transferFrom``.

    .. code-block:: python

        >>> share.allowance(accounts[1], accounts[2])
        1000

Checking Transfer Permissions
-----------------------------

.. method:: OrgShare.checkTransfer(address _from, address _to, uint256 _value)

    Checks if a share transfer is permitted.

    * ``_from``: Address of the sender
    * ``_to``: Address of the recipient
    * ``_value``: Amount of shares to be transferred

    Returns ``true`` if the transfer is permitted. If the transfer is not permitted, the call will revert with the reason given in the error string.

    For a transfer to succeed it must first pass a series of checks:

    * Shares cannot be locked.
    * Sender must have a sufficient balance.
    * Sender and receiver must be verified in a verifier associated to the org.
    * Sender and receiver must not be restricted by the verifier or the org.
    * Transfer must not result in any org-imposed member limits being exceeded.
    * Transfer must be permitted by all active modules.

    Transfers between two addresses that are associated to the same ID do not undergo the same level of restrictions, as there is no change of ownership occuring.

    Modules can hook into this method via ``STModule.checkTransfer``.

    .. code-block:: python

        >>> share.checkTransfer(accounts[1], accounts[2], 100)
        True
        >>> share.checkTransfer(accounts[1], accounts[2], 10000)
        File "contract.py", line 282, in call
          raise VirtualMachineError(e)
        VirtualMachineError: VM Exception while processing transaction: revert Insufficient Balance
        >>> share.checkTransfer(accounts[1], accounts[9], 100)
        File "contract.py", line 282, in call
          raise VirtualMachineError(e)
        VirtualMachineError: VM Exception while processing transaction: revert Address not registered


.. method:: OrgShare.checkTransferCustodian(address _cust, address _from, address _to, uint256 _value)

    Checks if a custodian internal transfer of shares is permitted. See the :ref:`custodian` documentation for more information on custodial internal transfers.

    * ``_cust``: Address of the custodian
    * ``_from``: Address of the sender
    * ``_to``: Address of the recipient
    * ``_value``: Amount of shares to be transferred

    Returns ``true`` if the transfer is permitted. If the transfer is not permitted, the call will revert with the reason given in the error string.

    Permissioning checks for custodial transfers are identical to those of normal transfers.

    Modules can hook into this method via ``STModule.checkTransfer``. A custodial transfer can be differentiated from a regular transfer because the caller ID is be that of the custodian.

    .. code-block:: python

        >>> share.custodianBalanceOf(accounts[1], cust)
        2000
        >>> share.checkTransferCustodian(cust, accounts[1], accounts[2], 1000)
        True
        >>> share.checkTransferCustodian(cust, accounts[1], accounts[2], 5000)
        File "contract.py", line 282, in call
          raise VirtualMachineError(e)
        VirtualMachineError: VM Exception while processing transaction: revert Insufficient Custodial Balance

Transferring Shares
-------------------

.. method:: BookShare.transfer(address _to, uint256 _value)

    Transfers ``_value`` shares from ``msg.sender`` to ``_to``. If the transfer cannot be completed, the call will revert with the reason given in the error string.

    Some logic in this method deviates from the ERC20 standard, see :ref:`share-non-standard` for more information.

    All transfers will emit the ``Transfer`` event. Transfers where there is a change of ownership will also emit``OrgCode.TransferOwnership``.

    .. code-block:: python

        >>> share.transfer(accounts[2], 1000, {'from': accounts[1]})

        Transaction sent: 0x29d9786ca39e79714581b217c24593546672e31dbe77c64804ea2d81848f053f
        BookShare.transfer confirmed - block: 14   gas used: 192451 (2.41%)
        <Transaction object '0x29d9786ca39e79714581b217c24593546672e31dbe77c64804ea2d81848f053f'>

.. method:: OrgShare.approve(address _spender, uint256 _value)

    Approves ``_spender`` to transfer up to ``_value`` shares belonging to ``msg.sender``.

    If ``_spender`` is already approved for >0 shares, the caller must first set approval to 0 before setting a new value. This prevents the attack vector documented `here <https://docs.google.com/document/d/1YLPtQxZu1UAvO9cZ1O2RPXBbT0mooh4DYKjA_jp-RLM/edit>`__.

    No transfer permission logic is applied when making this call. Approval may be given to any address, but a transfer can only be initiated by an address that is known by one of the associated verifiers. The same transfer checks also apply for both the sender and receiver, as if the transfer was done directly.

    Emits the ``Approval`` event.

    .. code-block:: python

        >>> share.approve(accounts[2], 1000, {'from': accounts[1]})

        Transaction sent: 0xa8793d57cfbf6e6ed0507c62e09c31c34feaae503b69aa6e6f4d39fad36fd7c5
        BookShare.approve confirmed - block: 20   gas used: 45948 (0.57%)
        <Transaction object '0xa8793d57cfbf6e6ed0507c62e09c31c34feaae503b69aa6e6f4d39fad36fd7c5'>

.. method:: BookShare.transferFrom(address _from, address _to, uint256 _value)

    Transfers ``_value`` shares from ``_from`` to ``_to``.

    Prior approval must have been given via ``OrgShare.approve``, except in certain cases documented under :ref:`share-non-standard`.

    All transfers will emit the ``Transfer`` event. Transfers where there is a change of ownership will also emit``OrgCode.TransferOwnership``.

    Modules can hook into this method via ``STModule.transferShares``.

    .. code-block:: python

        >>> share.transferFrom(accounts[1], accounts[3], 1000, {'from': accounts[2]})

        Transaction sent: 0x84cdd0c85d3e39f1ba4f5cbd0c4cb196c0f343c90c0819157acd14f6041fe945
        BookShare.transferFrom confirmed - block: 21   gas used: 234557 (2.93%)
        <Transaction object '0x84cdd0c85d3e39f1ba4f5cbd0c4cb196c0f343c90c0819157acd14f6041fe945'>

Modules
=======

Modules are attached and detached to share contracts via the associated ``OrgCode``. See :ref:`org-code-modules-attach-detach`.

.. method:: OrgShare.isActiveModule(address _module)

    Returns ``true`` if a module is currently active on the share.  Modules that are active on the associated ``OrgCode`` are also considered active on tokens. If the module is not active, returns ``false``.

    .. code-block:: python

        >>> share.isActiveModule(token_module)
        True
        >>> share.isActiveModule(other_module)
        False

.. method:: OrgShare.isPermittedModule(address _module, bytes4 _sig)

    Returns ``true`` if a module is permitted to access a specific method. If the module is not active or not permitted to call the method, returns ``false``.

    .. code-block:: python

        >>> share.isPermittedModule(token_module, "0x40c10f19")
        True
        >>> share.isPermittedModule(token_module, "0xc39f42ed")
        False

Events
======

The ``BookShare`` contract includes the following events.

.. method:: OrgShare.Transfer(address indexed from, address indexed to, uint256 shares)

    Emitted when a share transfer is completed via ``BookShare.transfer`` or ``BookShare.transferFrom``.

    Also emitted by ``BookShare.mint`` and ``BookShare.burn``. For minting the address of the sender will be ``0x00``, for burning it will be the address of the receiver.

.. method:: OrgShare.Approval(address indexed shareOwner, address indexed spender, uint256 tokens)

    Emitted when an approved transfer amount is set via ``BookShare.approve``.

.. method:: OrgShare.AuthorizedSupplyChanged(uint256 oldAuthorized, uint256 newAuthorized)

    Emitted when the authorized supply is changed via ``OrgShare.modifyAuthorizedSupply``.
