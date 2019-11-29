.. _kyc:

##########
IDVerifier
##########

Verifier contracts are whitelists that hold information on the identity, region, and rating of members. Depending on the use case there are two implementations:

* `IDVerifierOrg.sol <https://github.com/zerolawtech/ZAP-Tech/blob/master/contracts/IDVerifierOrg.sol>`__ is a streamlined whitelist contract designed for use with a single ``OrgCode``.
* `IDVerifierRegistrar.sol <https://github.com/zerolawtech/ZAP-Tech/blob/master/contracts/IDVerifierRegistrar.sol>`__ is a more robust implementation. It is maintainable by one or more entities across many jurisdictions, and designed to provide identity data to many ``OrgCode`` contracts.

Both contracts are derived from a common base `IDVerifier.sol <https://github.com/zerolawtech/ZAP-Tech/blob/master/contracts/bases/IDVerifier.sol>`__ that defines standard getter functions and events.

Contract authorities associate addresses to ID hashes that denote the identity of the member who controls the address. More than one address may be associated to the same hash. Anyone can call ``IDVerifierBase.getID`` to see which hash is associated to an address, and then using this ID call functions to query information about the member's region and accreditation rating.

Deployment
==========

Deployment varies depending on the type of verifier contract.

IDVerifierOrg
-------------

The address of the org is declared during deployment. The identity of the contract owner and authorities are determined by calls to this contract.

.. method:: IDVerifierOrg.constructor(address _org)

    * ``_org``: The address of the ``OrgCode`` contract to associate this contract with.

    .. code-block:: python

        >>> org = OrgCode[0]
        <OrgCode Contract object '0x40b49Ad1B8D6A8Df6cEdB56081D51b69e6569e06'>
        >>> kyc = accounts[0].deploy(IDVerifierOrg, org)

        Transaction sent: 0x98f595f75535df670d0c83b247bb471189938f0f57385fa1c7d3c6621748c703
        IDVerifierOrg.constructor confirmed - block: 2   gas used: 1645437 (20.57%)
        IDVerifierOrg deployed at: 0xa79269260195879dBA8CEFF2767B7F2B5F2a54D8
        <IDVerifierOrg Contract object '0xa79269260195879dBA8CEFF2767B7F2B5F2a54D8'>
        >>> kyc.orgCode()
        '0x40b49Ad1B8D6A8Df6cEdB56081D51b69e6569e06'

IDVerifierRegistrar
-------------------

The owner is declared during deployment. The owner is the highest contract authority, impossible to restrict and the only entity capable of creating or restricting other authorities on the contract.

.. method:: IDVerifierRegistrar.constructor(address[] _owners, uint32 _threshold)

    * ``_owners``: One or more addresses to associate with the contract owner. The address deploying the contract is not implicitly included within the owner list.
    * ``_threshold``: The number of calls required for the owner to perform a multi-sig action. Cannot exceed the length of ``_owners``.

    .. code-block:: python

        >>> kyc = accounts[0].deploy(IDVerifierRegistrar, [accounts[0]], 1)

        Transaction sent: 0xd10264c1445aad4e9dc84e04615936624e0b96596fec2097bebc83f9d3e69664
        IDVerifierRegistrar.constructor confirmed - block: 2   gas used: 2853810 (35.67%)
        IDVerifierRegistrar deployed at: 0x40b49Ad1B8D6A8Df6cEdB56081D51b69e6569e06
        <IDVerifierRegistrar Contract object '0x40b49Ad1B8D6A8Df6cEdB56081D51b69e6569e06'>


Contract Owners and Authorities
===============================

IDVerifierOrg
-------------

``IDVerifierOrg`` retrieves authority permissions and derives multisig functionality from the associated ``OrgCode`` contract. The owner of the org contract may call any method within the verifier. Authorities may call any method that they have been explicitely permitted to call.

See the :ref:`multisig` documentation for information on this aspect of the contract's functionality.

.. _kyc-verifier:

IDVerifierRegistrar
-------------------

The owner is declared during deployment. The owner is the highest contract authority, impossible to restrict and the only entity capable of creating or restricting other authorities on the contract.

Authorities are known, trusted entities that are permitted to add, modify, or restrict members within the verifier. Authorities are assigned a unique ID and associated with one or more addresses. They do not require explicit permission to call any contract functions. However, they may only add, modify or restrict members in countries that they have been approved to operate in.

``IDVerifierRegistrar`` implements a variation of the standard :ref:`multisig` functionality used in other contracts within the protocol. This section assumes familiarity with the standard multi-sig implementation, and will only highlight the differences.

Adding Authorities
******************

.. method:: IDVerifierRegistrar.addAuthority(address[] _addr, uint16[] _countries, uint32 _threshold)

    Creates a new authority.

    * ``_owners``: One or more addresses to associate with the authority
    * ``_countries``: Countries that the authority is approved to act in
    * ``_threshold``: The number of calls required for the authority to perform a multi-sig action. Cannot exceed the length of ``_owners``

    Once an authority has been designated they may use ``IDVerifierRegistrar.registerAddresses`` or ``IDVerifierRegistrar.restrictAddresses`` to modify their associated addresses.

    Emits the ``NewAuthority`` event.

    .. code-block:: python

        >>> kyc.addAuthority([accounts[1], accounts[2]], [4, 11, 77, 784], 1, {'from': accounts[0]})

        Transaction sent: 0x6085f4c75f12c4bed01c541d9a7e1d8f7e1ffc85247b5582459cbdd99fa1b51b
        IDVerifierRegistrar.addAuthority confirmed - block: 2   gas used: 157356 (1.97%)
        <Transaction object '0x6085f4c75f12c4bed01c541d9a7e1d8f7e1ffc85247b5582459cbdd99fa1b51b'>
        >>> id_ = kyc.getAuthorityID(accounts[1])
        0x7b809759765e66e1999ae953ef432bec3472905be1588b398563de2912cd7d01


Modifying Authorities
*********************

.. method:: IDVerifierRegistrar.setAuthorityCountries(bytes32 _id, uint16[] _countries, bool _permitted)

    Modifies the country permissions for an authority.

    .. code-block:: python

        >>> kyc.isApprovedAuthority(accounts[1], 4)
        True
        >>> kyc.setAuthorityCountries(id_, [4, 11], False, {'from': accounts[0]})

        Transaction sent: 0x60e9cc4c79bf08fd2929d33039f24278d63b28c91269ff79dc752f06a2c29e2a
        IDVerifierRegistrar.setAuthorityCountries confirmed - block: 3   gas used: 46196 (0.58%)
        <Transaction object '0x60e9cc4c79bf08fd2929d33039f24278d63b28c91269ff79dc752f06a2c29e2a'>
        >>> kyc.isApprovedAuthority(accounts[1], 4)
        False

.. method:: IDVerifierRegistrar.setAuthorityThreshold(bytes32 _id, uint32 _threshold)

    Modifies the multisig threshold requirement for an authority. Can be called by any authority to modify their own threshold, or by the owner to modify the threshold for anyone.

    You cannot set the threshold higher than the number of associated, unrestricted addresses for the authority.

    .. code-block:: python

        >>> kyc.setAuthorityThreshold(id_, 2, {'from': accounts[0]})

        Transaction sent: 0xe253c5acb5f0896ebdc92090c23bcec8baab0e23abe513ae6119caf51522e425
        IDVerifierRegistrar.setAuthorityThreshold confirmed - block: 4   gas used: 39535 (0.49%)
        <Transaction object '0xe253c5acb5f0896ebdc92090c23bcec8baab0e23abe513ae6119caf51522e425'>
        >>>
        >>> kyc.setAuthorityThreshold(id_, 3, {'from': accounts[0]})
        File "contract.py", line 277, in call
          raise VirtualMachineError(e)
        VirtualMachineError: VM Exception while processing transaction: revert

.. method:: IDVerifierRegistrar.setAuthorityRestriction(bytes32 _id, bool _restricted)

    Modifies the permitted state of an authority.

    If an authority has been compromised or found to be acting in bad faith, the owner may apply a broad restriction upon them with this method. This will also restrict every member that was approved by the authority.

    A list of members that were approved by the restricted authority can be obtained by looking at ``NewMember`` and ``UpdatedMember`` events. Once the identify of these members has been re-verified, the restriction upon them may be removed by calling either ``IDVerifierRegistrar.updateMember`` or ``IDVerifierRegistrar.setMemberAuthority`` to change which authority they are associated with.

    Emits the ``AuthorityRestriction`` event.

    .. code-block:: python

        >>> kyc.isApprovedAuthority(accounts[1], 784)
        True
        >>> kyc.setAuthorityRestriction(id_, True)

        Transaction sent: 0xeb3456fae407fb9bd673075369903769326c9f8699b313feb46e92f7f199c72e
        IDVerifierRegistrar.setAuthorityRestriction confirmed - block: 10   gas used: 40713 (28.93%)
        <Transaction object '0xeb3456fae407fb9bd673075369903769326c9f8699b313feb46e92f7f199c72e'>
        >>> kyc.isApprovedAuthority(accounts[1], 784)
        False


Getters
*******

The following getter methods are available to query information about contract authorities:

.. method:: IDVerifierRegistrar.isApprovedAuthority(address _addr, uint16 _country)

    Checks whether an authority is approved to add or modify members from a given country.  Returns ``false`` if the authority is not permitted.

    .. code-block:: python

        >>> kyc.isApprovedAuthority(accounts[1], 784)
        True

.. method:: IDVerifierRegistrar.getAuthorityID(address _addr)

    Given an address, returns the ID hash of the associated authority.  If the address is not associated with an authority the call will revert.

    .. code-block:: python

        >>> kyc.getAuthorityID(accounts[1])
        0x7b809759765e66e1999ae953ef432bec3472905be1588b398563de2912cd7d01
        >>> kyc.getAuthorityID(accounts[3])
        File "contract.py", line 277, in call
          raise VirtualMachineError(e)
        VirtualMachineError: VM Exception while processing transaction: revert

Working with Members
======================

Members are natural persons or legal entities who have passed verification checks and are approved to send and receive security shares.

Each member is assigned a unique ID and is associated with one or more addresses. They are also assigned an expiration time for their rating. This is useful in jurisdictions where accreditation status requires periodic reconfirmation.

See the :ref:`data-standards` documentation for detailed information on how to generate and format member information for use with verifier contracts.

Adding Members
----------------

.. method:: IDVerifierBase.generateID(string _idString)

    Returns the keccak hash of the supplied string. Can be used by an authority to generate a member ID hash from their identify information.

    .. code-block:: python

        >>> id_ = kyc.generateID("JOHNDOE010119701234567890")
        0xd3e7532ecb2c15babc9a5ac8e65f9d96b7030ab7e5dc9fffaa00ac15c0937be4

.. method:: IDVerifierBase.addMember(bytes32 _id, uint16 _country, bytes3 _region, uint8 _rating, uint40 _expires, address[] _addr)

    Adds a member to the verifier.

    * ``_id``: Member's bytes32 ID hash
    * ``_country``: Member country code
    * ``_region``: Member region code
    * ``_rating``: Member rating code
    * ``_expires``: The epoch time that the member rating is valid until
    * ``_addr```: One or more addresses to associate with the member

    Similar to authorities, addresses associated with members can be modified by calls to ``IDVerifierRegistrar.registerAddresses`` or ``IDVerifierRegistrar.restrictAddresses``.

    Emits the ``NewMember`` event.

    .. code-block:: python

        >>> kyc.addMember(id_, 784, "0x465500", 1, 9999999999, (accounts[3],), {'from': accounts[0]})

        Transaction sent: 0x47581e5b276298427f6a520353622b96cdecb29dff7269f03d7c957435398ebd
        IDVerifierRegistrar.addMember confirmed - block: 3   gas used: 120707 (1.51%)
        <Transaction object '0x47581e5b276298427f6a520353622b96cdecb29dff7269f03d7c957435398ebd'>

Modifying Members
-------------------

.. method:: IDVerifierBase.updateMember(bytes32 _id, bytes3 _region, uint8 _rating, uint40 _expires)

    Updates information on an existing member.

    Due to the way that the member ID is generated, it is not possible to modify the country that a member is associated with. An member who changes their legal country of residence will have to resubmit their information, be assigned a new ID, and transfer their shares to a different address.

    Emits the ``UpdatedMember`` event.

    .. code-block:: python

        >>> kyc.updateMember(id_, "0x465500", 2, 1600000000, {'from': accounts[0]})

        Transaction sent: 0xacfb17b530d2b565ea6016ab9b50051edb85e92e5ec6d2d85b1ac1708f897949
        IDVerifierRegistrar.updateMember confirmed - block: 4   gas used: 50443 (0.63%)
        <Transaction object '0xacfb17b530d2b565ea6016ab9b50051edb85e92e5ec6d2d85b1ac1708f897949'>

.. method:: IDVerifierBase.setMemberRestriction(bytes32 _id, bool _restricted)

    Modifies the restricted status of a member.  An member who is restricted will be unable to send or receive shares.

    Emits the ``MemberRestriction`` event.

    .. code-block:: python

        >>> kyc.setMemberRestriction(id_, True, {'from': accounts[0]})

        Transaction sent: 0x175982346d2f00a25f00a69701cda6fa311d60ade94d801267f51eefa86dc49e
        IDVerifierRegistrar.setMemberRestriction confirmed - block: 5   gas used: 41825 (0.52%)
        <Transaction object '0x175982346d2f00a25f00a69701cda6fa311d60ade94d801267f51eefa86dc49e'>

IDVerifierRegistrar
*******************

The following method is only available in ``IDVerifierRegistrar``.

.. method:: IDVerifierRegistrar.setMemberAuthority(bytes32[] _id, bytes32 _authID)

    Modifies the authority that is associated with one or more members.

    This method is only callable by the owner. It can be used after an authority is restricted, to remove the implied restriction upon members that were added by that authority.

    .. code-block:: python

        >>> auth_id = kyc.getAuthorityID(accounts[1])
        0x7b809759765e66e1999ae953ef432bec3472905be1588b398563de2912cd7d01
        >>> kyc.setMemberAuthority([id_], auth_id, {'from': accounts[0]})

        Transaction sent: 0x175982346d2f00a25f00a69701cda6fa311d60ade94d801267f51eefa86dc49e
        IDVerifierRegistrar.setMemberRestriction confirmed - block: 5   gas used: 41825 (0.52%)
        <Transaction object '0x175982346d2f00a25f00a69701cda6fa311d60ade94d801267f51eefa86dc49e'>

Adding and Restricting Addresses
================================

Each authority and member has one or more addresses associated to them. Once an address has been assigned to an ID, this association may never be removed. If an association were removed it would then be possible to assign that same address to a different member. This could be used to circumvent transfer restrictions on shares, allowing for non-compliant token ownership.

In situations of a lost or compromised private key the address may instead be flagged as restricted. In this case any shares in the restricted address can be retrieved using another associated, unrestricted address.

.. method:: IDVerifierBase.registerAddresses(bytes32 _id, address[] _addr)

    Associates one or more addresses to an ID, or removes restrictions imposed upon already associated addresses.

    In ``IDVerifierRegistrar``: If the ID belongs to an authority, this method may only be called by the owner. If the ID is a member, it may be called by any authority permitted to work in that member's country.

    Emits the ``RegisteredAddresses`` event.

    .. code-block:: python

        >>> kyc.registerAddresses(id_, [accounts[4], accounts[5]], {'from': accounts[0]})

        Transaction sent: 0xf508d5c72a1f707d88a0af4dbfc1007ecf2a7f04aa53bfcba2862e46fe3e647d
        IDVerifierRegistrar.registerAddresses confirmed - block: 7   gas used: 60329 (0.75%)
        <Transaction object '0xf508d5c72a1f707d88a0af4dbfc1007ecf2a7f04aa53bfcba2862e46fe3e647d'>

.. method:: IDVerifierBase.restrictAddresses(bytes32 _id, address[] _addr)

    Restricts one or more addresses associated with an ID.

    In ``IDVerifierRegistrar``: If the ID belongs to an authority, this method may only be called by the owner. If the ID is a member, it may be called by any authority permitted to work in that member's country.

    When restricing addresses associated to an authority, you cannot reduce the number of addresses such that the total remaining is lower than the multi-sig threshold value for that authority.

    Emits the ``RestrictedAddresses`` event.

    .. code-block:: python

        >>> kyc.restrictAddresses(id_, [accounts[4]], {'from': accounts[0]})

        Transaction sent: 0xfeb1b2316b3c35b2e08d84b3922030b97e671eec799d0fb0eaf748f69ab0866b
        IDVerifierRegistrar.restrictAddresses confirmed - block: 8   gas used: 60533 (0.76%)
        <Transaction object '0xfeb1b2316b3c35b2e08d84b3922030b97e671eec799d0fb0eaf748f69ab0866b'>

Getting Member Info
=====================

There are a variey of getter methods available for orgs and custodians to query information about members. In some cases these calls will revert if no member data is found.

Calls that Return False
-----------------------

The following calls will not revert, instead returning ``false`` or an empty result:

.. method:: IDVerifierBase.getID(address _addr)

    Given an address, returns the member or authority ID associated to it. If there is no association it will return an empty bytes32.

    .. code-block:: python

        >>> kyc.getID(accounts[1])
        0x1d285a37d3afce3a200a1eeb6697e59d15e8dc0d9b5132391e3ee53c7a69f18a
        >>> kyc.getID(accounts[2])
        0x0000000000000000000000000000000000000000000000000000000000000000

.. method:: IDVerifierBase.isRegistered(bytes32 _id)

    Returns a boolean to indicate if an ID is known to the verifier contract. No permissioning checks are applied.

    .. code-block:: python

        >>> kyc.isRegistered('0x1d285a37d3afce3a200a1eeb6697e59d15e8dc0d9b5132391e3ee53c7a69f18a')
        True
        >>> kyc.isRegistered('0x81a5c449c2409c87d702e0c4a675313347faf1c39576af357dd75efe7cad4793')
        False

.. method:: IDVerifierBase.isPermitted(address _addr)

    Given an address, returns a boolean to indicate if this address is permitted to transfer based on the following conditions:

    * Is the registring authority restricted?
    * Is the member ID restricted?
    * Is the address restricted?
    * Has the member's rating expired?

    .. code-block:: python

        >>> kyc.isPermitted(accounts[1])
        True
        >>> kyc.isPermitted(accounts[2])
        False

.. method:: IDVerifierBase.isPermittedID(bytes32 _id)

    Returns a transfer permission boolean similar to ``IDVerifierBase.isPermitted``, without a check on a specific address.

    .. code-block:: python

        >>> kyc.isPermittedID('0x1d285a37d3afce3a200a1eeb6697e59d15e8dc0d9b5132391e3ee53c7a69f18a(')
        True
        >>> kyc.isPermittedID('0x81a5c449c2409c87d702e0c4a675313347faf1c39576af357dd75efe7cad4793')
        False

Calls that Revert
-----------------

The remaining calls will revert under some conditions:

.. method:: IDVerifierBase.getMember(address _addr)

    Returns the member ID, permission status (based on the input address), rating, and country code for a member.

    Reverts if the address is not registered.

    .. note:: This function is designed to maximize gas efficiency when calling for information prior to performing a share transfer.

    .. code-block:: python

        >>> kyc.getMember(a[1]).dict()
        {
            '_country': 784,
            '_id': "0x1d285a37d3afce3a200a1eeb6697e59d15e8dc0d9b5132391e3ee53c7a69f18a",
            '_permitted': True,
            '_rating': 1
        }
        >>> kyc..getMember(a[0])
        File "contract.py", line 277, in call
          raise VirtualMachineError(e)
        VirtualMachineError: VM Exception while processing transaction: revert Address not registered

.. method:: IDVerifierBase.getMembers(address _from, address _to)

    The two member version of ``IDVerifierBase.getMember``. Also used to maximize gas efficiency.

    .. code-block:: python

        >>> kyc.getMembers(accounts[1], accounts[2]).dict()
        {
            '_country': (784, 784),
            '_id': ("0x1d285a37d3afce3a200a1eeb6697e59d15e8dc0d9b5132391e3ee53c7a69f18a", "0x9becd445b3c5703a4f1abc15870dd10c56bb4b4a70c68dba05e116551ab11b44"),
            '_permitted': (True, False),
            '_rating': (1, 2)
        }
        >>> kyc.getMembers(accounts[1], accounts[3])
        File "contract.py", line 277, in call
          raise VirtualMachineError(e)
        VirtualMachineError: VM Exception while processing transaction: revert Receiver not Registered

.. method:: IDVerifierBase.getRating(bytes32 _id)

    Returns the member rating number for a given ID.

    Reverts if the ID is not registered.

    .. code-block:: python

        >>> kyc.getRating("0x1d285a37d3afce3a200a1eeb6697e59d15e8dc0d9b5132391e3ee53c7a69f18a")
        1
        >>> kyc.getRating("0x00")
        File "contract.py", line 277, in call
          raise VirtualMachineError(e)
        VirtualMachineError: VM Exception while processing transaction: revert

.. method:: IDVerifierBase.getRegion(bytes32 _id)

    Returns the member region code for a given ID.

    Reverts if the ID is not registered.

    .. code-block:: python

        >>> kyc.getRegion("0x1d285a37d3afce3a200a1eeb6697e59d15e8dc0d9b5132391e3ee53c7a69f18a")
        0x653500
        >>> kyc.getRegion("0x00")
        File "contract.py", line 277, in call
          raise VirtualMachineError(e)
        VirtualMachineError: VM Exception while processing transaction: revert

.. method:: IDVerifierBase.getCountry(bytes32 _id)

    Returns the member country code for a given ID.

    Reverts if the ID is not registered.

    .. code-block:: python

        >>> kyc.getCountry("0x1d285a37d3afce3a200a1eeb6697e59d15e8dc0d9b5132391e3ee53c7a69f18a")
        784
        >>> kyc.getCountry("0x00")
        File "contract.py", line 277, in call
          raise VirtualMachineError(e)
        VirtualMachineError: VM Exception while processing transaction: revert

.. method:: IDVerifierBase.getExpires(bytes32 _id)

    Returns the member rating expiration date (in epoch time) for a given ID.

    Reverts if the ID is not registered or the rating has expired.

    .. code-block:: python

        >>> kyc.getExpires("0x1d285a37d3afce3a200a1eeb6697e59d15e8dc0d9b5132391e3ee53c7a69f18a")
        1600000000
        >>> kyc.getExpires("0x00")
        File "contract.py", line 277, in call
          raise VirtualMachineError(e)
        VirtualMachineError: VM Exception while processing transaction: revert

Events
======

Both ``IDVerifier`` implementations include the following events.

The ``authority`` value in each event is the ID hash of the authority that called the method where the event was emitted.

.. method:: IDVerifierBase.NewMember(bytes32 indexed id, uint16 indexed country, bytes3 region, uint8 rating, uint40 expires, bytes32 indexed authority)

    Emitted when a new member is added to the registry with ``IDVerifierBase.addMember``.

.. method:: IDVerifierBase.UpdatedMember(bytes32 indexed id, bytes3 region, uint8 rating, uint40 expires, bytes32 indexed authority)

    Emitted when data about an existing member is modified with ``IDVerifierBase.updateMember``.

.. method:: IDVerifierBase.MemberRestriction(bytes32 indexed id, bool permitted, bytes32 indexed authority)

    Emitted when a restriction upon a member is set or removed with ``IDVerifierBase.setMemberRestriction``.

.. method:: IDVerifierBase.RegisteredAddresses(bytes32 indexed id, address[] addr, bytes32 indexed authority)

    Emitted by ``IDVerifierBase.registerAddresses`` when new addresses are associated with a member ID, or existing addresses have a restriction removed.

.. method:: IDVerifierBase.RestrictedAddresses(bytes32 indexed id, address[] addr, bytes32 indexed authority)

    Emitted when a restriction is set upon addresses associated with a member ID with ``IDVerifierBase.restrictAddresses``.

IDVerifierRegistrar
-------------------

The following events are specific to ``IDVerifierRegistrar``'s authorities:

.. method:: IDVerifierRegistrar.NewAuthority(bytes32 indexed id)

    Emitted when a new authority is added via ``IDVerifierRegistrar.addAuthority``.

.. method:: IDVerifierRegistrar.AuthorityRestriction(bytes32 indexed id, bool permitted)

    Emitted when an authority is restricted or permitted via ``IDVerifierRegistrar.setAuthorityRestriction``.
