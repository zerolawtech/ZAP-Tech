.. _kyc-base:

.. todo
    examples
    events

###
KYC
###

KYC registry contracts are whitelists that hold information on the identity, region, and rating of investors. Depending on the use case there are two implementations:

* :ref:`kyc-issuer` is a streamlined whitelist contract designed for use with a single ``IssuingEntity``.
* :ref:`kyc-registrar` is a more robust implementation. It is maintainable by one or more entities across many jurisdictions, and designed to supply KYC data to many ``IssuingEntity`` contracts.

In both contracts, the owner associates addresses to ID hashes that denote the identity of the investor who controls the address. More than one address may be associated to the same hash. Anyone can call ``KYCBase.getID`` to see which hash is associated to an address, and then using this ID call functions to query information about the investor's region and accreditation rating.

Both contracts are derived from a common base contract `KYC.sol <https://github.com/HyperLink-Technology/SFT-Protocol/tree/master/contracts/bases/KYC.sol>`__ that defines standard getter functions and events. These are outlined below.

.. toctree::
    :maxdepth: 2
    :hidden:

    kyc-issuer.rst
    kyc-registrar.rst

Getting Investor Info
=====================

There are a variey of getter methods available for issuers and custodians to query information about investors. In some cases these calls will revert if no investor data is found.

Calls that Return False
-----------------------

The following calls will not revert, instead returning ``false`` or an empty result:

.. method:: KYCBase.isRegistered(bytes32 _id)

    Returns a boolean to indicate if an ID is known to the registrar contract. No permissioning checks are applied.

.. method:: KYCBase.getID(address _addr)

    Given an address, returns the investor or authority ID associated to it. If there is no association it will return an empty bytes32.

.. method:: KYCBase.isPermitted(address _addr)

    Given an address, returns a boolean to indicate if this address is permitted to transfer based on the following conditions:

    * Is the registring authority restricted?
    * Is the investor ID restricted?
    * Is the address restricted?
    * Has the investor's rating expired?

.. method:: KYCBase.isPermittedID(bytes32 _id)

    Returns a transfer permission boolean similar to ``KYCBase.isPermitted``, without a check on a specific address.

Calls that Revert
-----------------

The remaining calls **will revert under some conditions**:

.. method:: KYCBase.getInvestor(address _addr)

    Returns the investor ID, permission status (based on the input address), rating, and country code for an investor.

    Reverts if the address is not registered.

    .. note:: This function is designed to maximize gas efficiency when calling for information prior to performing a token transfer.

.. method:: KYCBase.getInvestors(address _from, address _to)

    The two investor version of ``KYCBase.getInvestor``. Also used to maximize gas efficiency.

.. method:: KYCBase.getRating(bytes32 _id)

    Returns the investor rating number for a given ID.

    Reverts if the ID is not registered.

.. method:: KYCBase.getRegion(bytes32 _id)

    Returns the investor region code for a given ID.

    Reverts if the ID is not registered.

.. method:: KYCBase.getCountry(bytes32 _id)

    Returns the investor country code for a given ID.

    Reverts if the ID is not registered.

.. method:: KYCBase.getExpires(bytes32 _id)

    Returns the investor rating expiration date (in epoch time) for a given ID.

    Reverts if the ID is not registered or the rating has expired.

Events
======

Both KYC implementations include the following events:

.. method:: KYCBase.NewInvestor(bytes32 indexed id, uint16 indexed country, bytes3 region, uint8 rating, uint40 expires, bytes32 indexed authority)

.. method:: KYCBase.UpdatedInvestor(bytes32 indexed id, bytes3 region, uint8 rating, uint40 expires, bytes32 indexed authority)

.. method:: KYCBase.InvestorRestriction(bytes32 indexed id, bool restricted, bytes32 indexed authority)

.. method:: KYCBase.RegisteredAddresses(bytes32 indexed id, address[] addr, bytes32 indexed authority)

.. method:: KYCBase.RestrictedAddresses(bytes32 indexed id, address[] addr, bytes32 indexed authority)
