.. _custodian-basics:

###################
How Custodians Work
###################

Custody and Beneficial Ownership
================================

Custodians interact with an org's member counts differently from regular members. When a member transfers a balance into a custodian it does not increase the overall member count, instead the member is now included in the list of beneficial owners represented by the custodian. Even if the member now has a balance of 0 in their own wallet, they will be still be included in the org’s member count.

Custodian balances are tracked directly in the corresponding share contract and can be queried through ``OrgShare.custodianBalanceOf``.

.. code-block:: python

    >>> cust
    <OwnedCustodian Contract object '0x3BcC6Ad6CFbB1997eb9DA056946FC38a6b5E270D'>
    >>> share.balanceOf(accounts[1])
    10000
    >>> share.custodianBalanceOf(accounts[1], cust)
    0
    >>> share.balanceOf(cust)
    0
    >>> share.transfer(cust, 5000, {'from': accounts[1]})

    Transaction sent: 0x4b09b29216d130dc06798ee673759a4e77e4823655c6477e895242f027726412
    BookShare.transfer confirmed - block: 16   gas used: 155761 (1.95%)
    <Transaction object '0x4b09b29216d130dc06798ee673759a4e77e4823655c6477e895242f027726412'>
    >>> share.balanceOf(accounts[1])
    5000
    >>> share.custodianBalanceOf(accounts[1], cust)
    5000
    >>> share.balanceOf(cust)
    5000


Share Transfers
===============

There are three types of share transfers related to Custodians.

* **Inbound**: transfers from a member into the Custodian contract.
* **Outbound**: transfers out of the Custodian contract to a member's wallet.
* **Internal**: transfers involving a change of ownership within the Custodian contract. This is the only type of transfer that involves a change of ownership of the share, however no tokens actually move.

In order to perform these transfers, Custodian contracts interact with OrgCode and BookShare contracts via the following methods. None of these methods are user-facing; if you are only using the standard Custodian contracts within the protocol you can skip the rest of this section.

Inbound
-------

Inbound transfers are those where a member sends shares into the Custodian. They are initiated in the same way as any other transfer, by calling the ``BookShare.transfer`` or ``BookShare.transferFrom`` methods. Inbound transfers do not register a change of beneficial ownership, however if the sender previously had a 0 balance with the custodian they will be added to that custodian's list of beneficial owners.

During an inbound transfer the following method is called:

.. method:: ICustodian.receiveTransfer(address _share, bytes32 _id, uint256 _value)

    * ``_share``: ``OrgShare`` addresss being transferred to the the Custodian
    * ``_id``: Sender ID
    * ``_value``: Amount being transferred

    Called from ``OrgCode.transferShares``. Used to update the custodian's balance and member counts. Revert or return ``false`` to block the transfer.

Outbound
--------

Outbound transfers are those where shares are sent from the Custodian to a member's wallet. Depending on the type of custodian and intended use case they may be initiated in several different ways.

Internally, the Custodian contract sends shares back to a member using the normal ``BookShare.transfer`` method. No change of beneficial ownership is recorded.

Internal
--------

Internal transfers involve a change of beneficial ownership records within the Custodian contract. Shares do not enter or leave the Custodian contract, but a call is made to the corresponding share contract to verify that the transfer is permitted.

The Custodian contract can call the following share methods relating to  internal transfers.

.. method:: OrgShare.checkTransferCustodian(address _cust, address _from, address _to, uint256 _value)

    Checks if a custodian internal transfer of shares is permitted.

    * ``_cust``: Address of the custodian
    * ``_from``: Address of the sender
    * ``_to``: Address of the recipient
    * ``_value``: Amount of shares to be transferred

    Returns ``true`` if the transfer is permitted. If the transfer is not permitted, the call will revert with the reason given in the error string.

    Permissioning checks for custodial transfers are identical to those of normal transfers.

.. method:: BookShare.transferCustodian(address[2] _addr, uint256 _value)

    Modifies member counts and ownership records based on an internal transfer of ownership within the Custodian contract.

    * ``_addr``: Array of sender and receiver addresses
    * ``_value``: Amount of shares being transferred


Minimal Implementation
======================

The `ICustodian <https://github.com/zerolawtech/ZAP-Tech/blob/master/contracts/interfaces/ICustodian.sol>`__ interface defines a minimal implementation required for custodian contracts to interact with an OrgCode contract. Notably absent from this interface are methods for internal custodian transfers, or to transfer out of the contract. Depending on the type of custodian and intended use case, outgoing transfers may be implemented in different ways.

.. method:: IBaseCustodian.ownerID()

    Public bytes32 hash representing the owner of the contract.

.. method:: IBaseCustodian.receiveTransfer(address _share, bytes32 _id, uint256 _value)

    * ``_share``: ``OrgShare`` address being transferred to the the Custodian
    * ``_id``: Sender ID
    * ``_value``: Amount being transferred

    Called from ``OrgCode.transferShares`` when shares are being sent into the Custodian contract. It should be used to update the custodian's balance and member counts. Revert or return ``false`` to block the transfer.
