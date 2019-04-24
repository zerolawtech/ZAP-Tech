.. _kyc-registrar:

############
KYCRegistrar
############

KYCRegistrar contracts are registries that hold information on the identity, region, and rating of investors. This contract may be associated with multiple :ref:`issuing-entity` contracts to provide investor KYC data to them.

Registries may be maintained by a single entity, or a federation of entities where each are approved to provide identification services for their specific jurisdiction. The contract owner can authorize other entities to add investors within specified countries.

Contract authorities associate addresses to ID hashes that denote the identity of the investor who owns the address. More than one address may be associated to the same hash. Anyone can call ``KYCRegistrar.getID`` to see which hash is associated to an address, and then using this ID call functions to query information about the investor's region and accreditation rating.

KYCRegistrar contracts implement a variation of the standard :ref:`multisig` functionality used in other contracts within the protocol. This document assumes familiarity with the standard multi-sig implementation, and will only highlight the differences.

It may be useful to also view the `KYCRegistrar.sol <https://github.com/HyperLink-Technology/SFT-Protocol/tree/master/contracts/KYCRegistrar.sol>`__ source code while reading this document.

Deployment
==========

The **owner** is declared during deployment. The owner is the highest contract authority, impossible to restrict and the only entity capable of creating or restricting other authorities on the contract.

.. method:: KYCRegistrar.constructor(address[] _owners, uint32 _threshold)

    * ``_owners``: One or more addresses to associate with the contract owner. The address deploying the contract is not implicitly included within the owner list.
    * ``_threshold``: The number of calls required for the owner to perform a multi-sig action. Cannot exceed the length of ``_owners``.

    .. code-block:: python

        >>> kyc = accounts[0].deploy(KYCRegistrar, [accounts[0]], 1)

        Transaction sent: 0xd10264c1445aad4e9dc84e04615936624e0b96596fec2097bebc83f9d3e69664
        KYCRegistrar.constructor confirmed - block: 2   gas used: 2853810 (35.67%)
        KYCRegistrar deployed at: 0x40b49Ad1B8D6A8Df6cEdB56081D51b69e6569e06
        <KYCRegistrar Contract object '0x40b49Ad1B8D6A8Df6cEdB56081D51b69e6569e06'>

Working with Authorities
========================

**Authorities** are known, trusted entities that are permitted to add, modify, or restrict investors within the registrar. Authorities are assigned a unique ID and associated with one or more addresses.

Only the owner may add, modify or restrict other authorities.

Adding Authorities
------------------

.. method:: KYCRegistrar.addAuthority(address[] _addr, uint16[] _countries, uint32 _threshold)

    Creates a new authority.

    * ``_owners``: One or more addresses to associate with the authority
    * ``_countries``: Countries that the authority is approved to act in
    * ``_threshold``: The number of calls required for the authority to perform a multi-sig action. Cannot exceed the length of ``_owners``

    Authorities do not require explicit permission to call any contract functions. However, they may only add, modify or restrict investors in countries that they have been approved to operate in.

    Once an authority has been designated they may use ``KYCRegistrar.registerAddresses`` or ``KYCRegistrar.restrictAddresses`` to modify their associated addresses.

    .. code-block:: python

        >>> kyc.addAuthority([accounts[1], accounts[2]], [4, 11, 77, 784], 1, {'from': accounts[0]})

        Transaction sent: 0x6085f4c75f12c4bed01c541d9a7e1d8f7e1ffc85247b5582459cbdd99fa1b51b
        KYCRegistrar.addAuthority confirmed - block: 2   gas used: 157356 (1.97%)
        <Transaction object '0x6085f4c75f12c4bed01c541d9a7e1d8f7e1ffc85247b5582459cbdd99fa1b51b'>
        >>> id_ = kyc.getAuthorityID(accounts[1])
        0x7b809759765e66e1999ae953ef432bec3472905be1588b398563de2912cd7d01


Modifying Authorities
---------------------

.. method:: KYCRegistrar.setAuthorityCountries(bytes32 _id, uint16[] _countries, bool _permitted)

    Modifies the country permissions for an authority.

    .. code-block:: python

        >>> kyc.isApprovedAuthority(accounts[1], 4)
        True
        >>> kyc.setAuthorityCountries(id_, [4, 11], False, {'from': accounts[0]})

        Transaction sent: 0x60e9cc4c79bf08fd2929d33039f24278d63b28c91269ff79dc752f06a2c29e2a
        KYCRegistrar.setAuthorityCountries confirmed - block: 3   gas used: 46196 (0.58%)
        <Transaction object '0x60e9cc4c79bf08fd2929d33039f24278d63b28c91269ff79dc752f06a2c29e2a'>
        >>> kyc.isApprovedAuthority(accounts[1], 4)
        False

.. method:: KYCRegistrar.setAuthorityThreshold(bytes32 _id, uint32 _threshold)

    Modifies the multisig threshold requirement for an authority. Can be called by any authority to modify their own threshold, or by the owner to modify the threshold for anyone.

    You cannot set the threshold higher than the number of associated, unrestricted addresses for the authority.

    .. code-block:: python

        >>> kyc.setAuthorityThreshold(id_, 2, {'from': accounts[0]})

        Transaction sent: 0xe253c5acb5f0896ebdc92090c23bcec8baab0e23abe513ae6119caf51522e425
        KYCRegistrar.setAuthorityThreshold confirmed - block: 4   gas used: 39535 (0.49%)
        <Transaction object '0xe253c5acb5f0896ebdc92090c23bcec8baab0e23abe513ae6119caf51522e425'>
        >>>
        >>> kyc.setAuthorityThreshold(id_, 3, {'from': accounts[0]})
        File "contract.py", line 277, in call
          raise VirtualMachineError(e)
        VirtualMachineError: VM Exception while processing transaction: revert

.. method:: KYCRegistrar.setAuthorityRestriction(bytes32 _id, bool _permitted)

    Modifies the permitted state of an authority.

    If an authority has been compromised or found to be acting in bad faith, the owner may apply a broad restriction upon them with this method. This will also restrict every investor that was approved by the authority.

    A list of investors that were approved by the restricted authority can be obtained by looking at ``NewInvestor`` and ``UpdatedInvestor`` events. Once the KYC/AML of these investors has been re-verified, the restriction upon them may be removed by calling either ``KYCRegistrar.updateInvestor`` or ``KYCRegistrar.setInvestorAuthority`` to change which authority they are associated with.

    .. code-block:: python

        >>> kyc.isApprovedAuthority(accounts[1], 784)
        True
        >>> kyc.setAuthorityRestriction(id_, False)

        Transaction sent: 0xeb3456fae407fb9bd673075369903769326c9f8699b313feb46e92f7f199c72e
        KYCRegistrar.setAuthorityRestriction confirmed - block: 10   gas used: 40713 (28.93%)
        <Transaction object '0xeb3456fae407fb9bd673075369903769326c9f8699b313feb46e92f7f199c72e'>
        >>> kyc.isApprovedAuthority(accounts[1], 784)
        False


Getters
-------

The following getter methods are available to query information about contract authorities:

.. method:: KYCRegistrar.isApprovedAuthority(address _addr, uint16 _country)

    Checks whether an authority is approved to add or modify investors from a given country.  Returns ``false`` if the authority is not permitted.

    .. code-block:: python

        >>> kyc.isApprovedAuthority(accounts[1], 784)
        True

.. method:: KYCRegistrar.getAuthorityID(address _addr)

    Given an address, returns the ID hash of the associated authority.  If the address is not associated with an authority the call will revert.

    .. code-block:: python

        >>> kyc.getAuthorityID(accounts[1])
        0x7b809759765e66e1999ae953ef432bec3472905be1588b398563de2912cd7d01
        >>> kyc.getAuthorityID(accounts[3])
        File "contract.py", line 277, in call
          raise VirtualMachineError(e)
        VirtualMachineError: VM Exception while processing transaction: revert

Working with Investors
======================

**Investors** are natural persons or legal entities who have passed KYC/AML checks and are approved to send and receive security tokens.

Each investor is assigned a unique ID and is associated with one or more addresses. They are also assigned an expiration time for their rating. This is useful in jurisdictions where accreditation status requires periodic reconfirmation.

Authorites may add, modify, or restrict investors in any country that they have been approved to operate in by the owner.  See the :ref:`data-standards` documentation for detailed information on how this information is generated and formatted.

Adding Investors
----------------

.. method:: KYCRegistrar.generateID(string _idString)

    Returns the keccak hash of the supplied string. Can be used by an authority to generate an investor ID hash from their KYC information.

    .. code-block:: python

        >>> id_ = kyc.generateID("JOHNDOE010119701234567890")
        0xd3e7532ecb2c15babc9a5ac8e65f9d96b7030ab7e5dc9fffaa00ac15c0937be4

.. method:: KYCRegistrar.addInvestor(bytes32 _id, uint16 _country, bytes3 _region, uint8 _rating, uint40 _expires, address[] _addr)

    Adds an investor to the registrar.

    * ``_id``: Investor's bytes32 ID hash
    * ``_country``: Investor country code
    * ``_region``: Investor region code
    * ``_rating``: Investor rating code
    * ``_expires``: The epoch time that the investor rating is valid until
    * ``_addr```: One or more addresses to associate with the investor

    Similar to authorities, addresses associated with investors can be modified by calls to ``KYCRegistrar.registerAddresses`` or ``KYCRegistrar.restrictAddresses``.

    .. code-block:: python

        >>> kyc.addInvestor(id_, 784, "0x465500", 1, 9999999999, (accounts[3],), {'from': accounts[0]})

        Transaction sent: 0x47581e5b276298427f6a520353622b96cdecb29dff7269f03d7c957435398ebd
        KYCRegistrar.addInvestor confirmed - block: 3   gas used: 120707 (1.51%)
        <Transaction object '0x47581e5b276298427f6a520353622b96cdecb29dff7269f03d7c957435398ebd'>

Modifying Investors
-------------------

.. method:: KYCRegistrar.updateInvestor(bytes32 _id, bytes3 _region, uint8 _rating, uint40 _expires)

    Updates information on an existing investor.

    Due to the way that the investor ID is generated, it is not possible to modify the country that an investor is associated with. An investor who changes their legal country of residence will have to resubmit KYC, be assigned a new ID, and transfer their tokens to a different address.

    .. code-block:: python

        >>> kyc.updateInvestor(id_, "0x465500", 2, 1600000000, {'from': accounts[0]})

        Transaction sent: 0xacfb17b530d2b565ea6016ab9b50051edb85e92e5ec6d2d85b1ac1708f897949
        KYCRegistrar.updateInvestor confirmed - block: 4   gas used: 50443 (0.63%)
        <Transaction object '0xacfb17b530d2b565ea6016ab9b50051edb85e92e5ec6d2d85b1ac1708f897949'>

.. method:: KYCRegistrar.setInvestorRestriction(bytes32 _id, bool _permitted)

    Modifies the restricted status of an investor.  An investor who is restricted will be unable to send or receive tokens.

    .. code-block:: python

        >>> kyc.setInvestorRestriction(id_, False, {'from': accounts[0]})

        Transaction sent: 0x175982346d2f00a25f00a69701cda6fa311d60ade94d801267f51eefa86dc49e
        KYCRegistrar.setInvestorRestriction confirmed - block: 5   gas used: 41825 (0.52%)
        <Transaction object '0x175982346d2f00a25f00a69701cda6fa311d60ade94d801267f51eefa86dc49e'>

.. method:: KYCRegistrar.setInvestorAuthority(bytes32[] _id, bytes32 _authID)

    Modifies the authority that is associated with one or more investors.

    This method is only callable by the owner. It can be used after an authority is restricted, to remove the implied restriction upon investors that were added by that authority.

    .. code-block:: python

        >>> auth_id = kyc.getAuthorityID(accounts[1])
        0x7b809759765e66e1999ae953ef432bec3472905be1588b398563de2912cd7d01
        >>> kyc.setInvestorAuthority([id_], auth_id, {'from': accounts[0]})

        Transaction sent: 0x175982346d2f00a25f00a69701cda6fa311d60ade94d801267f51eefa86dc49e
        KYCRegistrar.setInvestorRestriction confirmed - block: 5   gas used: 41825 (0.52%)
        <Transaction object '0x175982346d2f00a25f00a69701cda6fa311d60ade94d801267f51eefa86dc49e'>

Adding and Restricting Addresses
================================

Each authority and investor has one or more addresses associated to them. Once an address has been assigned to an ID, this association may never be removed. If an association were removed it would then be possible to assign that same address to a different investor. This could be used to circumvent transfer restrictions on tokens, allowing for non-compliant token ownership.

In situations of a lost or compromised private key the address may instead be flagged as restricted. In this case any tokens in the restricted address can be retrieved using another associated, unrestricted address.

.. method:: KYCRegistrar.registerAddresses(bytes32 _id, address[] _addr)

    Associates one or more addresses to an ID, or removes restrictions imposed upon already associated addresses.

    If the ID belongs to an authority, this method may only be called by the owner. If the ID is an investor, it may be called by any authority permitted to work in that investor's country.

    .. code-block:: python

        >>> kyc.registerAddresses(id_, [accounts[4], accounts[5]], {'from': accounts[0]})

        Transaction sent: 0xf508d5c72a1f707d88a0af4dbfc1007ecf2a7f04aa53bfcba2862e46fe3e647d
        KYCRegistrar.registerAddresses confirmed - block: 7   gas used: 60329 (0.75%)
        <Transaction object '0xf508d5c72a1f707d88a0af4dbfc1007ecf2a7f04aa53bfcba2862e46fe3e647d'>

.. method:: KYCRegistrar.restrictAddresses(bytes32 _id, address[] _addr)

    Restricts one or more addresses associated with an ID.

    If the ID belongs to an authority, this method may only be called by the owner. If the ID is an investor, it may be called by any authority permitted to work in that investor's country.

    When restricing addresses associated to an authority, you cannot reduce the number of addresses such that the total remaining is lower than the multi-sig threshold value for that authority.

    .. code-block:: python

        >>> kyc.restrictAddresses(id_, [accounts[4]], {'from': accounts[0]})

        Transaction sent: 0xfeb1b2316b3c35b2e08d84b3922030b97e671eec799d0fb0eaf748f69ab0866b
        KYCRegistrar.restrictAddresses confirmed - block: 8   gas used: 60533 (0.76%)
        <Transaction object '0xfeb1b2316b3c35b2e08d84b3922030b97e671eec799d0fb0eaf748f69ab0866b'>

Events
======

The following events are specific to KYCRegistrar:

.. method:: KYCRegistrar.NewAuthority(bytes32 indexed id)

    Emitted when a new authority is added via ``KYCRegistrar.addAuthority``.

.. method:: KYCRegistrar.AuthorityRestriction(bytes32 indexed id, bool permitted)

    Emitted when an authority is restricted or permitted via ``KYCRegistrar.setAuthorityRestriction``.
