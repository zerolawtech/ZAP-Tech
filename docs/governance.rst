.. _governance:

##########
Governance
##########

The ``Goveranance`` contract is a special type of module that may optionally be attached to an :ref:`org-code`.  It is used to add on-chain voting functionality for share holders.  When attached, it adds a permissioning check before increasing authorized token supplies or adding new tokens.

ZAP includes a very minimal proof of concept as a starting point for developing a governance contract. It can be combined with a checkpoint module to build whatever specific setup is required by an org.

It may be useful to view source code for the following contracts while reading this document:

* `Governance.sol <https://github.com/zerolawtech/ZAP-Tech/blob/master/contracts/modules/Governance.sol>`__: A minimal implementation of ``Goverance``, intended for testing purposes or as a base for building a functional contract.
* `IGovernance.sol <https://github.com/zerolawtech/ZAP-Tech/blob/master/contracts/interfaces/IGovernance.sol>`__: The minimum contract interface required for a governance module to interact with an ``OrgCode`` contract.

Public Constants
================

.. method:: Governance.orgCode()

    The address of the associated ``OrgCode`` contract.

    .. code-block:: python

        >>> governance.orgCode()
        0x40b49Ad1B8D6A8Df6cEdB56081D51b69e6569e06

Checking Permissions
====================

The following methods must return ``true`` in order for the calling methods to execute.

.. method:: Governance.addShare(address _share)

    Called by ``OrgCode.addShare`` before associating a new share contract.

.. method:: Governance.modifyAuthorizedSupply(address _share, uint256 _value)

    Called by ``OrgShare.modifyAuthorizedSupply`` before modifying the authorized supply.
