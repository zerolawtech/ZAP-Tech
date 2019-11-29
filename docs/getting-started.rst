.. _getting-started:

###############
Getting Started
###############

This is a quick explanation of the minimum steps required to deploy and use each contract within ZAP.

To setup a simple test environment using the brownie console:

.. code-block:: python

    $ brownie console
    Brownie v1.0.0 - Python development framework for Ethereum

    Brownie environment is ready.
    >>> run('deployment')

This runs the ``main`` function in `scripts/deployment.py <https://github.com/zerolawtech/ZAP-Tech/blob/master/scripts/deployment.py>`__ which:

* Deploys ``IDVerifierRegistrar`` from ``accounts[0]``
* Deploys ``OrgCode`` from ``accounts[0]``
* Deploys ``BookShare`` from ``accounts[0]`` with an initial authorized supply of 1,000,000 shares
* Associates the contracts
* Approves ``accounts[1:7]`` in ``IDVerifierRegistrar``, with member ratings 1-2 and country codes 1-3
* Approves members from country codes 1-3 in ``OrgCode``

From this configuration, the contracts are ready to mint and transfer shares:

.. code-block:: python

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

ID Verifier
=============

There are two types of member verifier contracts:

* `IDVerifierRegistrar.sol <https://github.com/zerolawtech/ZAP-Tech/blob/master/contracts/IDVerifierRegistrar.sol>`__ can be maintained by one or more authorities and used as a shared whitelist by many orgs
* `IDVerifierOrg.sol <https://github.com/zerolawtech/ZAP-Tech/blob/master/contracts/IDVerifierOrg.sol>`__ is a more bare-bones verifier, unique to a single org

Owner addresses are able to add members to the verifier whitelist using ``IDVerifierRegistrar.addMember``.

.. code-block:: python

    >>> kyc = accounts[0].deploy(IDVerifierRegistrar, [accounts[0]], 1)

    Transaction sent: 0xd10264c1445aad4e9dc84e04615936624e0b96596fec2097bebc83f9d3e69664
    IDVerifierRegistrar.constructor confirmed - block: 2   gas used: 2853810 (35.67%)
    IDVerifierRegistrar deployed at: 0x40b49Ad1B8D6A8Df6cEdB56081D51b69e6569e06
    <IDVerifierRegistrar Contract object '0x40b49Ad1B8D6A8Df6cEdB56081D51b69e6569e06'>
    >>>
    >>> kyc.addMember("0x1234", 784, "0x465500", 2, 9999999999, (accounts[3],), {'from': accounts[0]})

    Transaction sent: 0x47581e5b276298427f6a520353622b96cdecb29dff7269f03d7c957435398ebd
    IDVerifierRegistrar.addMember confirmed - block: 3   gas used: 120707 (1.51%)
    <Transaction object '0x47581e5b276298427f6a520353622b96cdecb29dff7269f03d7c957435398ebd'>


See the :ref:`kyc` page for a detailed explanation of how to use verifier contracts.

Issuing Shares
==============

Issuing shares and being able to transfer them requires the following steps:

**1.** Deploy `OrgCode.sol <https://github.com/zerolawtech/ZAP-Tech/blob/master/contracts/OrgCode.sol>`__.

    .. code-block:: python

        >>> org = accounts[0].deploy(OrgCode, [accounts[0]], 1)

        Transaction sent: 0xb37d8d16b266796e64fde6a4e9813ae0673dddaeb63022d91c706612ee741972
        OrgCode.constructor confirmed - block: 2   gas used: 6473451 (80.92%)
        OrgCode deployed at: 0xa79269260195879dBA8CEFF2767B7F2B5F2a54D8
        <OrgCode Contract object '0xa79269260195879dBA8CEFF2767B7F2B5F2a54D8'>

**2.** Call ``OrgCode.setRegistrar`` to add one or more verifiers. You may maintain your own verifier and/or use those belonging to trusted third parties.

    .. code-block:: python

        >>> org.setVerifier(kyc, True, {'from': accounts[0]})

        Transaction sent: 0x606326c8b2b8f1541c333ef5a5cd44592efb50530c6326e260e728095b3ec2bd
        OrgCode.setRegistrar confirmed - block: 3   gas used: 61246 (0.77%)
        <Transaction object '0x606326c8b2b8f1541c333ef5a5cd44592efb50530c6326e260e728095b3ec2bd'>

**3.** Deploy `BookShare.sol <https://github.com/zerolawtech/ZAP-Tech/blob/master/contracts/BookShare.sol>`__. Enter the address of the ``OrgCode`` contract from step one in the constructor. The authorized supply is set at deployment, the initial total supply will be zero.

    .. code-block:: python

        >>> share = accounts[0].deploy(BookShare, org, "Test Share", "TST", 1000000)

        Transaction sent: 0x4d2bbbc01d026de176bf5749e6e1bd22ba6eb40a225d2a71390f767b2845bacb
        BookShare.constructor confirmed - block: 4   gas used: 3346083 (41.83%)
        BookShare deployed at: 0x099c68D84815532A2C33e6382D6aD2C634E92ef6
        <BookShare Contract object '0x099c68D84815532A2C33e6382D6aD2C634E92ef6'>

**4.** Call ``OrgCode.addShare`` to attach the share to the org.

    .. code-block:: python

        >>> org.addShare(share, {'from': accounts[0]})

        Transaction sent: 0x8e93cd6b85d1e993755e9fe31eb14ce600706eaf98d606156447d8e431db5db9
        OrgCode.addShare confirmed - block: 5   gas used: 61630 (0.77%)
        <Transaction object '0x8e93cd6b85d1e993755e9fe31eb14ce600706eaf98d606156447d8e431db5db9'>

**5.** Call ``OrgCode.setCountries`` to approve members from specific countries to hold the shares.

    .. code-block:: python

        >>> org.setCountries([784],[1],[0], {'from': accounts[0]})

        Transaction sent: 0x7299b96013acb4661f4b7f05016c0de6726d2337032740aa29f5407cdabde0c3
        OrgCode.setCountries confirmed - block: 6   gas used: 72379 (0.90%)
        <Transaction object '0x7299b96013acb4661f4b7f05016c0de6726d2337032740aa29f5407cdabde0c3'>

**6.** Call ``BookShare.mint`` to create new shares, up to the authorized supply.

    .. code-block:: python

        >>> share.mint(accounts[1], 1000, {'from': accounts[0]})

        Transaction sent: 0x77ec76224d90763641971cd61e99711c911828053612cc16eb2e5d7faa20815e
        BookShare.mint confirmed - block: 13   gas used: 229092 (2.86%)
        <Transaction object '0x77ec76224d90763641971cd61e99711c911828053612cc16eb2e5d7faa20815e'>


At this point, the org will be able to transfer shares to any address that has been whitelisted by one of the approved member registries *if the member meets the country and rating requirements*.

Note that the org's balance is assigned to the ``OrgCode`` contract. The org can transfer these shares with a normal call to ``BookShare.transfer`` from any approved address. Sending tokens to any address associated with the org will increase the balance on the ``OrgCode`` contract.

See the :ref:`org-code` and :ref:`security-share` pages for detailed explanations of how to use these contracts.

Transferring Shares
===================

`BookShare.sol <https://github.com/zerolawtech/ZAP-Tech/blob/master/contracts/BookShare.sol>`__ is based on the `ERC20 Token Standard <https://eips.ethereum.org/EIPS/eip-20>`__. Share transfers may be performed in the same ways as any share using this standard. However, in order to send or receive tokens you must:

* Be approved in one of the verifiers associated to the ``OrgCode``
* Meet the approved country and rating requirements as set by the org
* Pass any additional checks set by the org

You can check if a transfer will succeed without performing a transaction by calling the ``BookShare.checkTransfer`` method within the share contract.

.. code-block:: python

    >>> share.checkTransfer(accounts[8], accounts[2], 500)
      File "/contract.py", line 277, in call
    raise VirtualMachineError(e)
    VirtualMachineError: VM Exception while processing transaction: revert Address not registered

    >>> share.checkTransfer(accounts[1], accounts[2], 500)
    True

Restrictions imposed on member limits, approved countries and minimum ratings are only checked when receiving shares. Unless an address has been explicitly blocked, it will always be able to send an existing balance. For example, a member may purchase tokens that are only available to accredited members, and then later their accreditation status expires. The member may still transfer the tokens they already have, but may not receive any more tokens.

Transferring a balance between two addresses associated with the same member ID does not have the same restrictions imposed, as there is no change of ownership. An member with multiple addresses may call ``BookShare.transferFrom`` to move shares from any of their addresses without first using the ``BookShare.approve`` method. The org can also use ``BookShare.transferFrom`` to move any member's tokens, without prior approval.

See the :ref:`security-share` page for a detailed explanation of how to use this contract.

Custodians
==========

There are many types of custodians possible. Included in the core ZAP contracts is `OwnedCustodian.sol <https://github.com/zerolawtech/ZAP-Tech/blob/master/contracts/custodians/OwnedCustodian.sol>`__, which is a basic implementation with a real-world owner.

Once a custodian contract is deployed you must attach it to an ``OrgCode`` with ``OrgCode.addCustodian``.

.. code-block:: python

    >>> cust = accounts[0].deploy(OwnedCustodian, [accounts[0]], 1)

    Transaction sent: 0x11540767a467504e3ddd03c8c2423840a69bd82a6f28db33ea869570b87486f0
    OwnedCustodian.constructor confirmed - block: 13   gas used: 3326386 (41.58%)
    OwnedCustodian deployed at: 0x3BcC6Ad6CFbB1997eb9DA056946FC38a6b5E270D
    <OwnedCustodian Contract object '0x3BcC6Ad6CFbB1997eb9DA056946FC38a6b5E270D'>
    >>>
    >>> org.addCustodian(cust, {'from': accounts[0]})

    Transaction sent: 0x63d13a81c73ed614ea68f1db8cc005bd860c6f2fb0ef7d590488672bd3edc5df
    OrgCode.addCustodian confirmed - block: 14   gas used: 78510 (0.98%)
    <Transaction object '0x63d13a81c73ed614ea68f1db8cc005bd860c6f2fb0ef7d590488672bd3edc5df'>

At this point, transfers work in the following ways:

* Members send shares into the custodian contract just like they would any other address, using ``BookShare.transfer`` or ``BookShare.transferFrom``.

    .. code-block:: python

        >>> share.transfer(cust, 10000, {'from': accounts[1]})

        Transaction sent: 0x4b09b29216d130dc06798ee673759a4e77e4823655c6477e895242f027726412
        BookShare.transfer confirmed - block: 16   gas used: 155761 (1.95%)
        <Transaction object '0x4b09b29216d130dc06798ee673759a4e77e4823655c6477e895242f027726412'>

* Internal transfers within the custodian are done via ``OwnedCustodian.transferInternal``.

    .. code-block:: python

        >>> cust.transferInternal(share, accounts[1], accounts[2], 5000, {'from': accounts[0]})

        Transaction sent: 0x1c5cf1d01d2d5f9b9d9e801d8e2a0b9b2eb50fa11fbe03864b69ccf0fe2c03fc
        OwnedCustodian.transferInternal confirmed - block: 17   gas used: 189610 (2.37%)
        <Transaction object '0x1c5cf1d01d2d5f9b9d9e801d8e2a0b9b2eb50fa11fbe03864b69ccf0fe2c03fc'>

* Transfers out of the custodian contract are initiated with ``OwnedCustodian.transfer``.

    .. code-block:: python

        >>> cust.transfer(share, accounts[2], 5000, {'from': accounts[0]})

        Transaction sent: 0x227f7c24d68d63aa567c16458e039a283481ef5fd79d8b9e48c88b033ff18f79
        OwnedCustodian.transfer confirmed - block: 18   gas used: 149638 (1.87%)
        <Transaction object '0x227f7c24d68d63aa567c16458e039a283481ef5fd79d8b9e48c88b033ff18f79'>


You can see a member's custodied balance using ``BookShare.custodianBalanceOf``.

.. code-block:: python

    >>> share.custodianBalanceOf(accounts[1], cust)
    5000

See the :ref:`custodian` page for a detailed explanation of how to use this contract.
