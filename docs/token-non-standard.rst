
.. _share-non-standard:

=======================
Non Standard Behaviours
=======================

``BookShare`` and ``CertShare`` are based upon the `ERC20 Token
Standard <https://eips.ethereum.org/EIPS/eip-20>`__, however they deviate in several areas.

Org Balances
============

Shares held by the org will always be at the address of the OrgCode contract.  ``OrgShare.treasurySupply()`` returns the same result as ``OrgShare.balanceOf(OrgShare.orgCode())``.

As a result, the following non-standard behaviours exist:

* Any address associated with the org can transfer shares from the OrgCode contract using ``OrgShare.transfer``.
* Attempting to send shares to any address associated with the org will result in the tokens being sent to the OrgCode contract.

Share Transfers
===============

The following behaviours deviate from ERC20 relating to share transfers:

* Transfers of 0 shares will revert with an error string "Cannot send 0 tokens".
* If the caller and sender addresses are both associated to the same ID, ``OrgShare.transferFrom`` may be called without giving prior approval. In this way a member can easily recover shares when a private key is lost or compromised.
* The org may call ``OrgShare.transferFrom`` to move shares between any addresses without prior approval. Transfers of this type must still pass the normal checks, with the exception that the sending address may be restricted.  In this way the org can aid members with token recovery in the event of a lost or compromised private key, or force a transfer in the event of a court order.
