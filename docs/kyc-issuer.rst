.. _kyc-issuer:

.. todo
    methods are correct
    need to review content of each method description
    need to add in events fired
    needs examples

#########
KYCIssuer
#########

KYCIssuer contracts are registries that hold information on the identity, region, and rating of investors. Each contract is deployed by a specific issuer, and may only be associated with a single :ref:`issuing-entity` contract.

The contract owner associates addresses to ID hashes that denote the identity of the investor who owns the address. More than one address may be associated to the same hash. Anyone can call ``KYCIssuer.getID`` to see which hash is associated to an address, and then using this ID call functions to query information about the investor's region and accreditation rating.

It may be useful to also view the `KYCIssuer.sol <https://github.com/HyperLink-Technology/SFT-Protocol/tree/master/contracts/KYCIssuer.sol>`__ source code while reading this document.

Deployment
==========

The **owner** is declared during deployment. The owner is the highest contract authority, impossible to restrict and the only entity capable of creating or restricting other authorities on the contract.

.. method:: KYCIssuer.constructor(address[] _owners, uint32 _threshold)

    * ``_owners``: One or more addresses to associate with the contract owner. The address deploying the contract is not implicitly included within the owner list.
    * ``_threshold``: The number of calls required for the owner to perform a multi-sig action. Cannot exceed the length of ``_owners``.

    The ID of the owner is generated as a keccak of the contract address and available from the public getter ``ownerID``.

Working with Investors
======================

**Investors** are natural persons or legal entities who have passed KYC/AML checks and are approved to send and receive security tokens.

Each investor is assigned a unique ID and is associated with one or more addresses. They are also assigned an expiration time for their rating. This is useful in jurisdictions where accreditation status requires periodic reconfirmation.

Authorites may add, modify, or restrict investors in any country that they have been approved to operate in by the owner.  See the :ref:`data-standards` documentation for detailed information on how this information is generated and formatted.

.. method:: KYCIssuer.generateID(string _idString)

    Returns the keccak hash of the supplied string. Can be used by an authority to generate an investor ID hash from their KYC information.

.. method:: KYCIssuer.addInvestor(bytes32 _id, uint16 _country, bytes3 _region, uint8 _rating, uint40 _expires, address[] _addr)

    Adds an investor to the registrar.

    * ``_id``: Investor's bytes32 ID hash
    * ``_country``: Investor country code
    * ``_region``: Investor region code
    * ``_rating``: Investor rating code
    * ``_expires``: The epoch time that the investor rating is valid until
    * ``_addr```: One or more addresses to associate with the investor

    Similar to authorities, addresses associated with investors can be modified by calls to ``KYCIssuer.registerAddresses`` or ``KYCIssuer.restrictAddresses``.

.. method:: KYCIssuer.updateInvestor(bytes32 _id, bytes3 _region, uint8 _rating, uint40 _expires)

    Updates information on an existing investor.

    Due to the way that the investor ID is generated, it is not possible to modify the country that an investor is associated with. An investor who changes their legal country of residence will have to resubmit KYC, be assigned a new ID, and transfer their tokens to a different address.

.. method:: KYCIssuer.setInvestorRestriction(bytes32 _id, bool _permitted)

    Modifies the restricted status of an investor.  An investor who is restricted will be unable to send or receive tokens.


Adding and Restricting Addresses
================================

Each authority and investor has one or more addresses associated to them. Once an address has been assigned to an ID, this association may never be removed. If an association were removed it would then be possible to assign that same address to a different investor. This could be used to circumvent transfer restrictions on tokens, allowing for non-compliant token ownership.

In situations of a lost or compromised private key the address may instead be flagged as restricted. In this case any tokens in the restricted address can be retrieved using another associated, unrestricted address.

.. method:: KYCIssuer.registerAddresses(bytes32 _id, address[] _addr)

    Associates one or more addresses to an ID, or removes restrictions imposed upon already associated addresses.

    If the ID belongs to an authority, this method may only be called by the owner. If the ID is an investor, it may be called by any authority permitted to work in that investor's country.

.. method:: KYCIssuer.restrictAddresses(bytes32 _id, address[] _addr)

    Restricts one or more addresses associated with an ID.

    If the ID belongs to an authority, this method may only be called by the owner. If the ID is an investor, it may be called by any authority permitted to work in that investor's country.

    When restricing addresses associated to an authority, you cannot reduce the number of addresses such that the total remaining is lower than the multi-sig threshold value for that authority.
