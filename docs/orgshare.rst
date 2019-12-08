.. _orgshare:

########
OrgShare
########

Each token contract represents a single class of securities from an org. Share contracts are based on the `ERC20 Token
Standard <https://eips.ethereum.org/EIPS/eip-20>`__. Depending on the use case, there are two token implementations:

* `BookShare.sol <https://github.com/zerolawtech/ZAP-Tech/blob/master/contracts/BookShare.sol>`__ is used for the issuance of non-certificated (book entry) securities. These tokens are fungible.
* `CertShare.sol <https://github.com/zerolawtech/ZAP-Tech/blob/master/contracts/CertShare.sol>`__ is used for the issuance of certificated securities. These tokens are non-fungible.

Both contracts are derived from a common base `OrgShare.sol <https://github.com/zerolawtech/ZAP-Tech/blob/master/contracts/bases/OrgShare.sol>`__.

Share contracts include :ref:`multisig` and :ref:`modules` via the associated :ref:`org-code` contract. See the respective documents for more detailed information.

This documentation only explains contract methods that are meant to be accessed directly. External methods that will revert unless called through another contract, such as ``OrgCode`` or modules, are not included.

Because of significant differences in the contracts, ``BookShare`` and ``CertShare`` are documented seperately.

.. toctree::    :maxdepth: 2

    bookshare.rst
    certshare.rst
    token-non-standard.rst
