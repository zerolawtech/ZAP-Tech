.. _custodian:

##########
Custodians
##########

Custodian contracts are approved to hold shares on behalf of multiple members. Each custodian must be individually approved by an org before they can receive tokens.

There are two broad categories of custodians:

* **Owned** custodians are contracts that are controlled and maintained by a known legal entity. Examples of owned custodians include broker/dealers or centralized exchanges.
* **Autonomous** custodians are contracts without an owner. Once deployed there is no authority capable of exercising control over the contract. Examples of autonomous custodians include escrow services, privacy protocols and decentralized exchanges.

It may be useful to view source code for the following contracts while reading this section:

* `OwnedCustodian.sol <https://github.com/zerolawtech/ZAP-Tech/blob/master/contracts/custodians/OwnedCustodian.sol>`__: Standard owned custodian contract with ``Multisig`` and ``Modular`` functionality.
* `ICustodian.sol <https://github.com/zerolawtech/ZAP-Tech/blob/master/contracts/interfaces/ICustodian.sol>`__: The minimum contract interface required for a custodian to interact with an ``OrgCode`` contract.

.. warning:: An org should not approve a Custodian if the contract source code cannot be verified, or it is using a non-standard implementation that has not undergone a thorough audit. ZAP includes a standard owned Custodian contract that allows for customization through modules.

.. toctree::    :maxdepth: 2

    custodian-basics.rst
    owned-custodian.rst
