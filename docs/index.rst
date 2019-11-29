############
ZAP
############

The Secured Financial Transaction Protocol (ZAP) is a set of smart contracts, written in `Solidity <https://solidity.readthedocs.io/en/latest>`__ for the Ethereum blockchain, that allow for the shareization of financial securities. It provides a robust, modular framework that is configurable for a wide range of jurisdictions, with consideration for real world needs based on today’s existing markets. ZAP favors handling as much permissioning logic on-chain as possible, in order to maximize transparency for all parties involved.

ZAP was developed by `ZeroLaw <https://zerolaw.tech>`__.

.. note::

    Code starting with ``$`` is meant to be run in your terminal. Code starting with ``>>>`` is meant to run inside the `Brownie <https://github.com/iamdefinitelyahuman/brownie>`__ console.

How it Works
============

ZAP is designed to maximize interoperability between different network participants. Broadly speaking, these participants may be split into four categories:

* **Orgs** are entities that create and sell shares to fund their operations.
* **Verifiers** are trusted entities that provide verification services for network participants.
* **Members** are entities that have been verified and are are able to hold or transfer security shares.
* **Custodians** hold shares on behalf of members without taking direct ownership. They may provide services such as escrow or custody, or facilitate secondary trading of tokens.

The protocol is built with two central concepts in mind: **identification** and **permission**. Each member has their identity verified by a verifier and a unique ID hash is associated to their wallet addresses. Based on this identity information, orgs and custodians apply a series of rules to determine how the member may interact with them.

Orgs, verifiers and custodians each exist on the blockchain with their own smart contracts that define the way they interact with one another. These contracts allow different entities to provide services to each other within the ecosystem.

Tokenized shares in the protocol are built upon the ERC20 token standard. Shares are transferred via the ``transfer`` and ``transferFrom`` methods, however the transfer will only succeed if it passes a series of on-chain permissioning checks. A call to ``checkTransfer`` returns true if the transfer is possible. The base configuration includes member identification, tracking member counts and limits, and restrictions on countries and accredited status. By implementing other modules a variety of additional functionality is possible so as to meet the needs of each individual org.

Components
==========

ZAP is comprised of four core components:

1. :ref:`share`

    * ERC20 compliant token contracts
    * Intended to represent a corporate shareholder registry in book entry or certificated form
    * Permissioning logic to enforce enforce legal and contractural restrictions around share transfers
    * Modular design allows for optional added functionality

2. :ref:`org-code`

    * Common owner contract for multiples classes of shares created by the same org
    * Detailed on-chain cap table with granular permissioning capabilities
    * Modular design allows for optional added functionality
    * Multi-sig, multi-authority design provides increased security and permissioned contract management

3. :ref:`kyc`

    * Whitelists that provide identity, region, and accreditation information of members based on off-chain verification
    * May be maintained by a single entity for a single share issuance, or a federation across multiple jurisdictions providing identity data for many orgs
    * Multi-sig, multi-authority design provides increased security and permissioned contract management

4. :ref:`custodian`

    * Contracts that represent an entity approved to hold shares on behalf of multiple members
    * Deep integration with OrgCode to provide accurate on-chain member counts
    * Multiple implementations allow for a wide range of functionality including escrow services, custody, and secondary trading of shares
    * Modular design allows for optional added functionality
    * Multi-sig, multi-authority design provides increased security and permissioned contract management

Source Code
===========

The ZeroLaw Augmentation Protocol is fully open sourced. You can view the code on `GitHub <https://github.com/zerolawtech/ZAP-Tech>`__.

Testing and Deployment
======================

Unit testing and deployment of this project is performed with `Brownie <https://github.com/iamdefinitelyahuman/brownie>`__.

To run the tests:

::

    $ brownie test


.. warning:: ZAP is still under active development and has not yet undergone a third party audit. Please notify us if you find any issues in the code. **We highly recommend against using these contracts on the main-net prior to an audit by a trusted third party**.

License
=======

This project is licensed under the `Apache 2.0 <https://www.apache.org/licenses/LICENSE-2.0.html>`__ license.


Contents
========

:ref:`Keyword Index <genindex>`, :ref:`Glossary <glossary>`

.. toctree::    :maxdepth: 2

    getting-started.rst
    orgshare.rst
    orgcode.rst
    kyc.rst
    custodian.rst
    multisig.rst
    modules.rst
    governance.rst
    data-standards.rst
    glossary.rst
