.. _kyc-base:

###
KYC
###

KYC registry contracts are whitelists that hold information on the identity, region, and rating of investors. Depending on the use case there are two implementations:

* :ref:`kyc-issuer` is a streamlined whitelist contract designed for use with a single ``IssuingEntity``.
* :ref:`kyc-registrar` is a more robust implementation. It is maintainable by one or more entities across many jurisdictions, and designed to supply KYC data to many ``IssuingEntity`` contracts.

In both contracts, the owner associates addresses to ID hashes that denote the identity of the investor who controls the address. More than one address may be associated to the same hash. Anyone can call ``KYCBase.getID`` to see which hash is associated to an address, and then using this ID call functions to query information about the investor's region and accreditation rating.

.. toctree::
    :maxdepth: 2

    kyc-issuer.rst
    kyc-registrar.rst
    kyc-getters-events.rst
