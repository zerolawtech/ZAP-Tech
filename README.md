# SFT Protocol

## Description

The SFT protocol is a set of smart contracts, written in Solidity for the Ethereum blockchain, that allow for the tokenization of financial securities. It provides a robust, modular framework that is configurable for a wide range of jurisdictions, with consideration for real world needs based on today’s existing markets.

## Documentation

In-depth documentation is hosted at [Read the Docs](https://sft-protocol.readthedocs.io).

## Develoment Progress

The SFT Protocol is still under active development and has not yet undergone a third party audit. Please notify us if you find any issues in the code. We highly recommend against using these contracts prior to an audit by a trusted third party.

## Testing and Deployment

Unit testing and deployment of this project is performed with [Brownie](https://github.com/HyperLink-Technology/brownie).

To run the tests:

```bash
$ brownie test
```

## Getting Started

See the [Getting Started](https://sft-protocol.readthedocs.io/en/latest/getting-started.html) page for in-depth details on how to deploy the contracts so you can interact with them.

To setup an interactive brownie test environment:

```bash
$ brownie console
>>> from scripts.deployment import main
>>> main()
```

This runs the `main` function in [scripts/deployment.py](scripts/deployment.py) which:

* Deploys ``KYCRegistrar`` from ``accounts[0]``
* Deploys ``IssuingEntity`` from ``accounts[0]``
* Deploys ``SecurityToken`` from ``accounts[0]`` with an initial authorized supply of 1,000,000
* Associates the contracts
* Approves ``accounts[1:7]`` in ``KYCRegistrar``, with investor ratings 1-2 and country codes 1-3
* Approves investors from country codes 1-3 in ``IssuingEntity``

From this configuration, the contracts are ready to mint and transfer tokens:

```python
>>> token = SecurityToken[0]
>>> token.mint(accounts[1], 1000, {'from': accounts[0]})

Transaction sent: 0x77ec76224d90763641971cd61e99711c911828053612cc16eb2e5d7faa20815e
SecurityToken.mint confirmed - block: 13   gas used: 229092 (2.86%)
<Transaction object '0x77ec76224d90763641971cd61e99711c911828053612cc16eb2e5d7faa20815e'>
>>>
>>> token.transfer(accounts[2], 1000, {'from': accounts[1]})

Transaction sent: 0x29d9786ca39e79714581b217c24593546672e31dbe77c64804ea2d81848f053f
SecurityToken.transfer confirmed - block: 14   gas used: 192451 (2.41%)
<Transaction object '0x29d9786ca39e79714581b217c24593546672e31dbe77c64804ea2d81848f053f'>
>>>
```

## License

This project is licensed under the [Apache 2.0](https://www.apache.org/licenses/LICENSE-2.0.html) license.
