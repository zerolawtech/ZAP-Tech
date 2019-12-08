# ZAP Protocol

## Description

The ZeroLaw org-Augmentation Protocol (ZAP) is a general-purpose tech/law stack for augmenting any business entity or organization through the use of smart contracts and shares deployed to Ethereum or any other EVM-based blockchain. It is non-rent-seeking, fully free and open source and is neither funded by nor requires the use of any protocol token. It is intended to be compatible with a range of legal compliance strategies or applicable legal regimes by providing tunable compliance parameters; it is even compatible with antilaw positions. ZAP’s compliance parameters may be tuned "all the way up", "all the way down" or anywhere in between; thus, ZAP is suitable for any entity or organization, ranging from traditional corporations to anarchic, pseudonymous collectives. ZAP merges the vision of a borderless, decentralized future with the power to comply with existing legal requirements & best practices for doing business. ZAP has been developed by ZeroLaw, an independent law/technology team working to make technology and legal agreements interoperable. Anyone may contribute to the protocol.

ZAP was developed by [ZeroLaw](https://zerolaw.tech).

## How it Works

ZAP is designed to maximize interoperability between different network participants. Broadly speaking, these participants may be split into four categories:

* **Orgs** are entities that create and sell security shares to fund their business operations.
* **Investors** are entities that have passed identity checks and are are able to hold or transfer shares created by an Org.
* **Verifiers** are trusted entities that provide identification services for network participants.
* **Custodians** hold shares on behalf of members without taking direct ownership. They may provide services such as escrow or custody, or facilitate secondary trading of shares.

The protocol is built with two central concepts in mind: **identification** and **permission**. Each member has their identity verified by a registrar and a unique ID hash is associated to their wallet addresses. Based on this identity information, orgs and custodians apply a series of rules to determine how the member may interact with them.

Orgs, identifiers and custodians each exist on the blockchain with their own smart contracts that define the way they interact with one another. These contracts allow different entities to provide services to each other within the ecosystem.

OrgShares are based upon the ERC20 token standard. Shares are transferred via the ``transfer`` and ``transferFrom`` methods, however the transfer will only succeed if it passes a series of on-chain permissioning checks. A call to ``checkTransfer`` returns true if the transfer is possible. The base configuration includes member identification, tracking member counts and limits, and restrictions on countries and accredited status. By implementing other modules a variety of additional functionality is possible so as to meet the needs of each individual org.

## Components

ZAP is comprised of four core components:

1. **OrgShares**

    * ERC20 compliant token contracts
    * Intended to represent a corporate shareholder registry in book entry or certificated form
    * Permissioning logic to enforce enforce legal and contractural restrictions around share transfers
    * Modular design allows for optional added functionality

2. **OrgCode**

    * Common owner contract for multiples classes of shares created by the same org
    * Detailed on-chain cap table with granular permissioning capabilities
    * Modular design allows for optional added functionality
    * Multi-sig, multi-authority design provides increased security and permissioned contract management

3. **IDVerifier**

    * Whitelists that provide identity, region, and accreditation information of members based on off-chain KYC/AML verification
    * May be maintained by a single entity for a single issuance, or a federation across multiple jurisdictions providing identity data for many orgs
    * Multi-sig, multi-authority design provides increased security and permissioned contract management

4. **Custodian**

    * Contracts that represent an entity approved to hold shares on behalf of multiple members
    * Deep integration with IssuingEntity to provide accurate on-chain member counts
    * Multiple implementations allow for a wide range of functionality including escrow services, custody, and secondary trading
    * Modular design allows for optional added functionality
    * Multi-sig, multi-authority design provides increased security and permissioned contract management

## Documentation

In-depth documentation is hosted at [Read the Docs](https://sft-protocol.readthedocs.io).

## Develoment Progress

ZAP is still under active development and has not yet undergone a third party audit. Please notify us if you find any issues in the code. We highly recommend against using these contracts prior to an audit by a trusted third party.

## Testing and Deployment

Unit testing and deployment of this project is performed with [Brownie](https://github.com/iamdefinitelyahuman/brownie).

To run the tests:

```bash
$ pytest tests/
```

A [dockerfile](Dockerfile) is available if you are experiencing issues.

## Getting Started

See the [Getting Started](https://sft-protocol.readthedocs.io/en/latest/getting-started.html) page for in-depth details on how to deploy the contracts so you can interact with them.

To setup an interactive brownie test environment:

```bash
$ brownie console
>>> run('deployment')
```

This runs the `main` function in [scripts/deployment.py](scripts/deployment.py) which:

* Deploys ``IDVerifierRegistrar`` from ``accounts[0]``
* Deploys ``OrgCode`` from ``accounts[0]``
* Deploys ``BookShare`` from ``accounts[0]`` with an initial authorized supply of 1,000,000
* Associates the contracts
* Approves ``accounts[1:7]`` in ``IDVerifierRegistrar``, with member ratings 1-2 and country codes 1-3
* Approves members from country codes 1-3 in ``OrgCode``

From this configuration, the contracts are ready to mint and transfer shares:

```python
>>> share = BookShare[0]
>>> share.mint(accounts[1], 1000, {'from': accounts[0]})

Transaction sent: 0x77ec76224d90763641971cd61e99711c911828053612cc16eb2e5d7faa20815e
BookShare.mint confirmed - block: 13   gas used: 229092 (2.86%)
<Transaction object '0x77ec76224d90763641971cd61e99711c911828053612cc16eb2e5d7faa20815e'>
>>>
>>> share.transfer(accounts[2], 1000, {'from': accounts[1]})

Transaction sent: 0x29d9786ca39e79714581b217c24593546672e31dbe77c64804ea2d81848f053f
BookShare.transfer confirmed - block: 14   gas used: 192451 (2.41%)
<Transaction object '0x29d9786ca39e79714581b217c24593546672e31dbe77c64804ea2d81848f053f'>
>>>
```

## License

The code in this project is licensed under the [GNU GPLv3](https://github.com/zerolawtech/ZAP-Tech/blob/master/LICENSE) license. The ZAP Whitepaper and SFT Yellowpaper are licensed under [Creative Commons - Attribution-NonCommercial-NoDerivatives 4.0 International](https://creativecommons.org/licenses/by-nc-nd/4.0/legalcode). All model legal forms, including all documents contained in the "model-legal-forms" folder, are licensed under [Attribution-ShareAlike](https://creativecommons.org/licenses/by-sa/4.0/legalcode).
