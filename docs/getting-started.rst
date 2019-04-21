.. _getting-started:

###############
Getting Started
###############

This is a quick explanation of the minimum steps required to deploy and use each contract of the protocol.

To setup a simple test environment using brownie:


::

    $ brownie console
    >>> run('deployment')


This runs the ``main`` function in `scripts/deployment.py <https://github.com/HyperLink-Technology/SFT-Protocol/tree/master/scripts/deployment.py>`__ which:

* Deploys ``KYCRegistrar`` from ``accounts[0]``
* Deploys ``IssuingEntity`` from ``accounts[0]``
* Deploys ``SecurityToken`` from ``accounts[0]`` with an initial authorized supply of 1,000,000 tokens
* Associates the contracts
* Approves ``accounts[1:7]`` in ``KYCRegistrar``, with investor ratings 1-2 and country codes 1-3
* Approves investors from country codes 1-3 in ``IssuingEntity``

From this configuration, the contracts are ready to mint and transfer tokens:

::

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

KYC Registrar
=============

There are two types of investor registry contracts:

* `KYCRegistrar.sol <https://github.com/HyperLink-Technology/SFT-Protocol/tree/master/contracts/KYCRegistrar.sol>`__ can be maintained by one or more authorities and used as a shared whitelist by many issuers
* `KYCIssuer.sol <https://github.com/HyperLink-Technology/SFT-Protocol/tree/master/contracts/KYCIssuer.sol>`__ is a more bare-bones registry, unique to a single issuer

Owner addresses are able to add investors to the registrar whitelist using ``KYCRegistrar.addInvestor``.

See the :ref:`kyc-registrar` page for a detailed explanation of how to use this contract.

Issuing Tokens
==============

Issuing tokens and being able to transfer them requires the following steps:

1. Deploy `IssuingEntity.sol <https://github.com/HyperLink-Technology/SFT-Protocol/tree/master/contracts/IssuingEntity.sol>`__.
2. Call ``IssuingEntity.setRegistrar`` to add one or more investor registries. You may maintain your own registry and/or use those belonging to trusted third parties.
3. Deploy `SecurityToken.sol <https://github.com/HyperLink-Technology/SFT-Protocol/tree/master/contracts/SecurityToken.sol>`__. Enter the address of the issuer contract from step one in the constructor. The authorized supply is set at deployment, the initial total supply will be zero.
4. Call ``IssuingEntity.addToken`` to attach the token to the issuer.
5. Call ``IssuingEntity.setCountries`` to approve investors from specific countries to hold the tokens.
6. Call ``SecurityToken.mint`` to create new tokens, up to the authorized supply.

At this point, the issuer will be able to transfer tokens to any address that has been whitelisted by one of the approved investor registries *if the investor meets the country and rating requirements*.

Note that the issuer's balance is assigned to the IssuingEntity contract. The issuer can transfer these tokens with a normal call to ``SecurityToken.transfer`` from any approved address. Sending tokens to any address associated with the issuer will increase the balance on the IssuingEntity contract.

See the :ref:`issuing-entity` and :ref:`security-token` pages for detailed explanations of how to use these contracts.

Transferring Tokens
===================

SecurityToken.sol is based on the `ERC20 Token Standard <https://theethereum.wiki/w/index.php/ERC20_Token_Standard>`__. Token transfers may be performed in the same ways as any token using this standard. However, in order to send or receive tokens you must:

* Be approved in one of the KYC registries associated to the token issuer
* Meet the approved country and rating requirements as set by the issuer
* Pass any additional checks set by the issuer

You can check if a transfer will succeed without performing a transaction by calling the ``SecurityToken.checkTransfer`` method within the token contract.

Restrictions imposed on investor limits, approved countries and minimum ratings are only checked when receiving tokens. Unless an address has been explicitly blocked, it will always be able to send an existing balance. For example, an investor may purchase tokens that are only available to accredited investors, and then later their accreditation status expires. The investor may still transfer the tokens they already have, but may not receive any more tokens.

Transferring a balance between two addresses associated with the same investor ID does not have the same restrictions imposed, as there is no change of ownership. An investor with multiple addresses may call ``SecurityToken.transferFrom`` to move tokens from any of their addresses without first using the ``SecurityToken.approve`` method. The issuer can also use ``SecurityToken.transferFrom`` to move any investor's tokens, without prior approval.

See the :ref:`security-token` page for a detailed explanation of how to use this contract.

Custodians
==========

There are many types of custodians possible. Included in the core SFT contracts is `OwnedCustodian.sol <https://github.com/HyperLink-Technology/SFT-Protocol/tree/master/contracts/custodians/OwnedCustodian.sol>`__, which is a basic implementation with a real-world owner.

Once a custodian contract is deployed you must attach it to an IssuingEntity with ``IssuingEntity.addCustodian``. At this point, transfers work in the following ways:

* Investors send tokens into the custodian contract just like they would any other address, using ``SecurityToken.transfer`` or ``SecurityToken.transferFrom``.
* Internal transfers within the custodian are done via ``OwnedCustodian.transferInternal``.
* Transfers out of the custodian contract are initiated with ``OwnedCustodian.transfer``.

You can see an investor's custodied balance using ``SecurityToken.custodianBalanceOf``.

See the :ref:`custodian` page for a detailed explanation of how to use this contract.
