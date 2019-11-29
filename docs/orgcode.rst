.. _org-code:

#######
OrgCode
#######

``OrgCode`` contracts hold shared compliance logic for all shares created by a single org. They are the central contract that an org uses to connect and interact with verifiers, tokens and custodians.

Each org contract includes standard ZAP multis-gi functionality. See :ref:`multisig` for detailed information on this component.

This documentation only explains contract methods that are meant to be accessed directly. External methods that will revert unless called through another contract, such as a share or module, are not included.

It may be useful to also view the `OrgCode.sol <https://github.com/zerolawtech/ZAP-Tech/blob/master/contracts/OrgCode.sol>`__ source code while reading this document.

Deployment
==========

The constructor declares the owner as per standard :ref:`multisig`.

.. method:: OrgCode.constructor(address[] _owners, uint32 _threshold)

    * ``_owners``: One or more addresses to associate with the contract owner. The address deploying the contract is not implicitly included within the owner list.
    * ``_threshold``: The number of calls required for the owner to perform a multi-sig action.

    The ID of the owner is generated as a keccak of the contract address and available from the public getter ``ownerID``.

    .. code-block:: python

        >>> org = accounts[0].deploy(OrgCode, [accounts[0], accounts[1]], 1)

        Transaction sent: 0xb37d8d16b266796e64fde6a4e9813ae0673dddaeb63022d91c706612ee741972
        OrgCode.constructor confirmed - block: 1   gas used: 6473451 (80.92%)
        OrgCode deployed at: 0xa79269260195879dBA8CEFF2767B7F2B5F2a54D8
        <OrgCode Contract object '0xa79269260195879dBA8CEFF2767B7F2B5F2a54D8'>

Public Constants
================

The following public variables cannot be changed after contract deployment.

.. method:: OrgCode.ownerID()

    The bytes32 ID hash of the org.

    .. code-block:: python

        >>> org.ownerID()
        0xce1e12589ad8fb3eed11af5b9ef8788c25b574d4073d23c871e003021400c429

Shares, Verifiers, Custodians, Governance
=========================================

The ``OrgCode`` contract is a center point through which other contracts are linked. Each contract must be associated to it before it will function properly.

* :ref:`security-share` contracts must be associated before tokens can be transferred, so that the org contract can accurately track member counts.
* :ref:`kyc` contracts must be associated to provide KYC data on members before they can receive or send shares.
* :ref:`custodian` contracts must be approved in order to send or receive shares from members.
* A :ref:`governance` contract may optionally be associated. Once attached, it requires the org to receive on-chain approval before creating or minting additional shares.

Associating Contracts
---------------------

.. method:: OrgCode.addShare(address _share)

    Associates a new :ref:`security-share` contract with the org contract.

    Once added, the share can be restricted with ``OrgCode.setShareRestriction``.

    If a :ref:`governance` module has been set, it must provide approval whenever this method is called.

    Emits the ``ShareAdded`` event.

    .. code-block:: python

        >>> org.addShare(BookShare[0], {'from': accounts[0]})

        Transaction sent: 0x8e93cd6b85d1e993755e9fe31eb14ce600706eaf98d606156447d8e431db5db9
        OrgCode.addShare confirmed - block: 5   gas used: 61630 (0.77%)
        <Transaction object '0x8e93cd6b85d1e993755e9fe31eb14ce600706eaf98d606156447d8e431db5db9'>

.. method:: OrgCode.setVerifier(address _verifier, bool _restricted)

    Associates or removes a :ref:`kyc` contract.

    Before a transfer is completed, each associated verifier is called to check which IDs are associated to the transfer addresses.

    The address => ID association is stored within OrgCode. If a verifier is later removed it is impossible for another verifier to return a different ID for the address.

    When a verifier is removed, any members that were identified through it will be unable to send or receive shares until they are identified through another associated verifier. Transfer attempts will revert with the message "Registrar restricted".

    Emits the ``VerifierSet`` event.

    .. code-block:: python

        >>> org.setVerifier(IDVerifierRegistrar[0], False, {'from': accounts[0]})

        Transaction sent: 0x606326c8b2b8f1541c333ef5a5cd44592efb50530c6326e260e728095b3ec2bd
        OrgCode.setVerifier confirmed - block: 3   gas used: 61246 (0.77%)
        <Transaction object '0x606326c8b2b8f1541c333ef5a5cd44592efb50530c6326e260e728095b3ec2bd'>

.. method:: OrgCode.addCustodian(address _custodian)

    Approves a :ref:`custodian` contract to send and receive shares associated with the org.

    Once a custodian has been added, they can be restricted with ``OrgCode.setEntityRestriction``.

    Emits the ``CustodianAdded`` event.

    .. code-block:: python

        >>> org.addCustodian(OwnedCustodian[0])

        Transaction sent: 0xbae451ce98691dc37dad6a67d8daf410a3eeebf34b59ab60eaeef7c3f3a2654c
        OrgCode.addCustodian confirmed - block: 25   gas used: 78510 (0.98%)
        <Transaction object '0xbae451ce98691dc37dad6a67d8daf410a3eeebf34b59ab60eaeef7c3f3a2654c'>

.. method:: OrgCode.setGovernance(address _governance)

    Sets the active :ref:`Governance` contract.

    Setting the address to ``0x00`` disables governance functionality.

    .. code-block:: python

        >>> org.setGovernance(GovernanceMinimal[0])

        Transaction sent: 0x8e93cd6b85d1e993755e9fe31eb14ce600706eaf98d606156447d8e431db5db9
        OrgCode.addCustodian confirmed - block: 26   gas used: 63182 (0.98%)
        <Transaction object '0x8e93cd6b85d1e993755e9fe31eb14ce600706eaf98d606156447d8e431db5db9'>

Setting Restrictions
--------------------

Transfer restrictions can be applied at varying levels.

.. method:: OrgCode.setEntityRestriction(bytes32 _id, bool _restricted)

    Retricts or permits a member or custodian from transferring shares, based on their ID.

    This can only be used to block a member that would otherwise be able to hold the shares. It cannot be used to whitelist members who are not listed in an associated verifier. When a member is restricted, the org is still able to transfer tokens from their addresses.

    Emits the ``EntityRestriction`` event.

    .. code-block:: python

        >>> BookShare[0].transfer(accounts[2], 100, {'from': accounts[1]})

        Transaction sent: 0x89bf6113bd5ccf9917d0749776fa4bed986d519d66221973def33c0190a2e6d2
        BookShare.transfer confirmed - block: 21   gas used: 192387 (2.40%)
        >>> org.setEntityRestriction(id_, True)

        Transaction sent: 0xfc4dabf2c48b4502ab4a9d3edbfc0ea792e715069ede0f8b455697df180bfc9f
        OrgCode.setEntityRestriction confirmed - block: 22   gas used: 39978 (0.50%)
        >>> BookShare[0].transfer(accounts[2], 100, {'from': accounts[1]})
        File "contract.py", line 277, in call
          raise VirtualMachineError(e)
        VirtualMachineError: VM Exception while processing transaction: revert Sender restricted: Issuer

.. method:: OrgCode.setShareRestriction(address _share, bool _restricted)

    Restricts or permits transfers of a share. When a token is restricted, only the org may perform transfers.

    Emits the ``ShareRestriction`` event.

    .. code-block:: python

        >>> org.setShareRestriction(BookShare[0], True, {'from': accounts[0]})

        Transaction sent: 0xfe60d18d0315278bdd1cfd0896a040cdadb63ada255685737908672c0cd10cee
        OrgCode.setShareRestriction confirmed - block: 13   gas used: 40369 (0.50%)
        <Transaction object '0xfe60d18d0315278bdd1cfd0896a040cdadb63ada255685737908672c0cd10cee'>

.. method:: OrgCode.setGlobalRestriction(bool _restricted)

    Restricts or permits transfers of all associated shares. Modifying the global restriction does not affect individual token restrictions - i.e. you cannot call this method to remove restrictions that were set with ``OrgCode.setShareRestriction``.

    Emits the ``GlobalRestriction`` event.

    .. code-block:: python

        >>> org.setGlobalRestriction(True, {'from': accounts[0]})

        Transaction sent: 0xc03ac4c6d36e971f980297e365f30752ac5097e391213c59fd52544829a87479
        OrgCode.setGlobalRestriction confirmed - block: 14   gas used: 53384 (0.67%)
        <Transaction object '0xc03ac4c6d36e971f980297e365f30752ac5097e391213c59fd52544829a87479'>

Getters
-------

.. method:: OrgCode.isActiveShare(address _share)

    Returns a boolean indicating if the given address is a share contract that is associated with the ``OrgCode`` not currently restricted.

    .. code-block:: python

        >>> org.isActiveShare(BookShare[0])
        True
        >>> org.isActiveShare(accounts[2])
        False

.. method:: OrgCode.governance()

    Returns the address of the associated ``Governance`` contract. If none is set, returns ``0x00``.

    .. code-block:: python

        >>> org.governance()
        "0x14b0Ed2a7C4cC60DD8F676AE44D0831d3c9b2a9E"

Members
=========

Members must be identified by a :ref:`kyc` before they can send or receive shares. This identity data is then used to apply further checks against member limits and accreditation requirements.

Getters
-------

The ``OrgCode`` contract contains several public getter methods for querying information relating to members.

.. method:: OrgCode.isRegisteredMember(address _addr)

    Check if an address belongs to a registered member and return a bool. Returns ``false`` if the address is not registered.

    .. code-block:: python

        >>> org.isRegisteredMember(accoounts[2])
        True
        >>> org.isRegisteredMember(accoounts[9])
        False

.. method:: OrgCode.getID(address _addr)

    Returns the member ID associated with an address. If the address is not saved in the contract, this call will query associated verifiers. If the ID cannot be found the call will revert.

    .. code-block:: python

        >>> org.getID(accounts[1])
        0x8be1198d7f1848ebeddb3f807146ce7d26e63d3b6715f27697428ddb52db9b63
        >>> org.getID(accounts[9])
        File "contract.py", line 277, in call
          raise VirtualMachineError(e)
        VirtualMachineError: VM Exception while processing transaction: revert Address not registered

.. method:: OrgCode.getMemberVerifier(bytes32 _id)

    Returns the verifier address associated with a member ID. If the member ID is not saved in the ``OrgCode`` contract storage, this call will return ``0x00``.

    Note that a member's ID is only saved in the contract after a successful share transfer. Even if the member's ID is known via an associated verifier, if they have never received tokens the call to ``getMemberVerifier`` will return an empty value.

    .. code-block:: python

        >>> id_ = org.getID(accounts[1])
        0x8be1198d7f1848ebeddb3f807146ce7d26e63d3b6715f27697428ddb52db9b63
        >>> org.getMemberVerifier(id_)
        0xa79269260195879dBA8CEFF2767B7F2B5F2a54D8

Member Limits
===============

Issuers can define member limits globally, by country, by member rating, or by a combination thereof. These limits are shared across all shares associated to the org.

Member counts and limits are stored in uint32[8] arrays. The first entry in each array is the sum of all the remaining entries. The remaining entries correspond to the count or limit for each member rating. In most (if not all) countries there will be less than 7 types of member accreditation ratings, and so the upper range of these arrays will be empty. Setting a member limit to 0 means no limit is imposed.

The org must explicitely approve each country from which members are allowed to purchase shares.

It is possible for an org to set a limit that is lower than the current member count. When a limit is met or exceeded existing members are still able to receive shares, but new members are blocked.

Setters
-------

.. method:: OrgCode.setCountry(uint16 _country, bool _permitted, uint8 _minRating, uint32[8] _limits)

    Approve or restrict a country, and/or modify it's minimum member rating and member limits.

    * ``_country``: The code of the country to modify
    * ``_permitted``: Permission bool
    * ``_minRating``: The minimum rating required for a member in this country to hold shares. Cannot be zero.
    * ``_limits``: A uint32[8] array of member limits for this country.

    Emits the ``CountryModified`` event.

    .. code-block:: python

        >>> org.setCountry(784, True, 1, [100, 0, 0, 0, 0, 0, 0, 0], {'from': accounts[0]})

        Transaction sent: 0x96f9a7e12e898fbd2fb6c7593a7ae82c4eea087c508929e616f86e98ae9b0db6
        OrgCode.setCountry confirmed - block: 26   gas used: 116709 (1.46%)
        <Transaction object '0x96f9a7e12e898fbd2fb6c7593a7ae82c4eea087c508929e616f86e98ae9b0db6'>

.. method:: OrgCode.setCountries(uint16[] _country, uint8[] _minRating, uint32[] _limit)

    Approve many countries at once.

    * ``_countries``: An array of country codes to modify
    * ``_minRating``: Array of minimum member ratings for each country.
    * ``_limits``: Array of total member limits for each country.

    Each array must be the same length. The function will iterate through them at the same time: ``_countries[0]`` will require rating ``_minRating[0]`` and have a total member limit of ``_limits[0]``.

    This method is useful when approving many countries that do not require specific limits based on member ratings. When you require specific limits for each rating or to explicitly restrict an entire country, use ``OrgCode.setCountry``.

    Emits the ``CountryModified`` event once for each country that is modified.

    .. code-block:: python

        >>> org.setCountries([784],[1],[0], {'from': accounts[0]})

        Transaction sent: 0x7299b96013acb4661f4b7f05016c0de6726d2337032740aa29f5407cdabde0c3
        OrgCode.setCountries confirmed - block: 6   gas used: 72379 (0.90%)
        <Transaction object '0x7299b96013acb4661f4b7f05016c0de6726d2337032740aa29f5407cdabde0c3'>

.. method:: OrgCode.setMemberLimits(uint32[8] _limits)

    Sets total member limits, irrespective of country.

    Emits the ``MemberLimitsSet`` event.

    .. code-block:: python

        >>> org.setMemberLimits([2000, 500, 2000, 0, 0, 0, 0, 0], {'from': accounts[0]})

        Transaction sent: 0xbeda494b5fb741ae659b866b9f5eca26b9add249ae75dc651a7944281e2ae4eb
        OrgCode.setMemberLimits confirmed - block: 27   gas used: 94926 (1.19%)
        <Transaction object '0xbeda494b5fb741ae659b866b9f5eca26b9add249ae75dc651a7944281e2ae4eb'>

Getters
-------

.. method:: OrgCode.getMemberCounts()

    Returns the sum total member counts and limits for all countries and issuances related to this contract.

    .. code-block:: python

        >>> org.getMemberCounts().dict()
        {
            '_counts': ((1, 0, 1, 0, 0, 0, 0, 0),
            '_limits': (2000, 500, 2000, 0, 0, 0, 0, 0))
        }

.. method:: OrgCode.getCountry(uint16 _country)

    Returns the minimum rating, member counts and member limits for a given country. Countries that have not been set will return all zero values. The easiest way to verify if a country has been set is to check if ``_minRating > 0``.

    .. code-block:: python

        >>> org.getCountry(784).dict()
        {
            '_count': (0, 0, 0, 0, 0, 0, 0, 0),
            '_limit': (100, 0, 0, 0, 0, 0, 0, 0),
            '_minRating': 1
        }


Document Verification
=====================

.. method:: OrgCode.getDocumentHash(string _documentID)

    Returns a recorded document hash. If no hash is recorded, it will return ``0x00``.

    See `Document Verification`_.

    .. code-block:: python

        >>> org.getDocumentHash("Shareholder Agreement")
        "0xbeda494b5fb741ae659b866b9f5eca26b9add249ae75dc651a7944281e2ae4eb"
        >>> org..getDocumentHash("Unknown Document")
        0x0000000000000000000000000000000000000000000000000000000000000000

.. method:: OrgCode.setDocumentHash(string _documentID, bytes32 _hash)

    Creates an on-chain record of the hash of a legal document.

    Once a hash is recorded, the org can distrubute the document electronically and members can verify the authenticity by generating the hash themselves and comparing it to the blockchain record.

    Emits the ``NewDocumentHash`` event.

    .. code-block:: python

        >>> org.setDocumentHash("Shareholder Agreement", "0xbeda494b5fb741ae659b866b9f5eca26b9add249ae75dc651a7944281e2ae4eb", {'from': accounts[0]})

        Transaction sent: 0x7299b96013acb4661f4b7f05016c0de6726d2337032740aa29f5407cdabde0c3
        OrgCode.setDocumentHash confirmed - block: 6   gas used: 72379 (0.90%)
        <Transaction object '0x7299b96013acb4661f4b7f05016c0de6726d2337032740aa29f5407cdabde0c3'>



.. _org-code-modules:

Modules
=======

Modules for share contracts are attached and detached through the associated ``OrgCode``. This contract itself is not directly modular, however any module that declares it as the owner may be attached to all the associated token contracts.

See the :ref:`modules` documentation for more information on module functionality and development.

.. _org-code-modules-attach-detach:

Attaching and Detaching
-----------------------

.. method:: OrgCode.attachModule(address _target, address _module)

    Attaches a module.

    * ``_target``: The address of the contract to associate the module to.
    * ``_module``: The address of the module contract.

    .. code-block:: python

        >>> module = DividendModule.deploy(accounts[0], BookShare[0], org, 1600000000)

        Transaction sent: 0x1b1e7a09e7731fcb724a6586e3cf71c07221db009e89445c33e07cc8e18e74d1
        DividendModule.constructor confirmed - block: 13   gas used: 1756759 (21.96%)
        DividendModule deployed at: 0x3BcC6Ad6CFbB1997eb9DA056946FC38a6b5E270D
        <DividendModule Contract object '0x3BcC6Ad6CFbB1997eb9DA056946FC38a6b5E270D'>
        >>>
        >>> org.attachModule(BookShare[0], module, {'from': accounts[0]})

        Transaction sent: 0x7123091c968dbe0c279aa6850c668534aef327972a08d65b67779108cbaa9b45
        OrgCode.attachModule confirmed - block: 14   gas used: 212332 (2.65%)
        <Transaction object '0x7123091c968dbe0c279aa6850c668534aef327972a08d65b67779108cbaa9b45'>

.. method:: OrgCode.detachModule(address _target, address _module)

    Detaches a module.

    .. code-block:: python

        >>> org.detachModule(BookShare[0], module, {'from': accounts[0]})

        Transaction sent: 0xe1539492053b91ffb05dec6da6f73a02f0b3e44fcec707acf911d37922b65699
        OrgCode.detachModule confirmed - block: 15   gas used: 28323 (0.35%)
        <Transaction object '0xe1539492053b91ffb05dec6da6f73a02f0b3e44fcec707acf911d37922b65699'>

Events
======

The ``OrgCode`` contract includes the following events.

.. method:: OrgCode.ShareAdded(address indexed share)

    Emitted after a new share contract has been associated via ``OrgCode.addShare``.

.. method:: OrgCode.VerifierSet(address indexed verifier, bool restricted)

    Emitted by ``OrgCode.setVerifier`` when a new KYC verifier contract is added, or an existing verifier is restricted or permitted.

.. method:: OrgCode.CustodianAdded(address indexed custodian)

    Emitted when a new custodian contract is approved via ``OrgCode.addCustodian``.

.. method:: OrgCode.EntityRestriction(bytes32 indexed id, bool restricted)

    Emitted whenever a member or custodian has a restriction set or removed with ``OrgCode.setEntityRestriction``.

.. method:: OrgCode.ShareRestriction(address indexed share, bool restricted)

    Emitted when a share restriction is set or removed via ``OrgCode.setShareRestriction``.

.. method:: OrgCode.GlobalRestriction(bool restricted)

    Emitted when a global restriction is set with ``OrgCode.setGlobalRestriction``.

.. method:: OrgCode.MemberLimitsSet(uint32[8] limits)

    Emitted when global member limits are modified via ``OrgCode.setMemberLimits``.

.. method:: OrgCode.CountryModified(uint16 indexed country, bool permitted, uint8 minrating, uint32[8] limits)

    Emitted whenever country specific limits are set via ``OrgCode.setCountry`` or ``OrgCode.SetCountries``.

.. method:: OrgCode.NewDocumentHash(string indexed document, bytes32 documentHash)

    Emitted when a new document hash is saved with ``OrgCode.setDocumentHash``.
