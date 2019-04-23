.. _kyc-getters-events:

#########################
Shared Methods and Events
#########################

Both registrar implementations are derived from a common base contract `KYC.sol <https://github.com/HyperLink-Technology/SFT-Protocol/tree/master/contracts/bases/KYC.sol>`__ that defines standard getter functions and events. These are outlined below.

Getting Investor Info
=====================

There are a variey of getter methods available for issuers and custodians to query information about investors. In some cases these calls will revert if no investor data is found.

Calls that Return False
-----------------------

The following calls will not revert, instead returning ``false`` or an empty result:

.. method:: KYCBase.getID(address _addr)

    Given an address, returns the investor or authority ID associated to it. If there is no association it will return an empty bytes32.

    .. code-block:: python

        >>> kyc.getID(accounts[1])
        0x1d285a37d3afce3a200a1eeb6697e59d15e8dc0d9b5132391e3ee53c7a69f18a
        >>> kyc.getID(accounts[2])
        0x0000000000000000000000000000000000000000000000000000000000000000

.. method:: KYCBase.isRegistered(bytes32 _id)

    Returns a boolean to indicate if an ID is known to the registrar contract. No permissioning checks are applied.

    .. code-block:: python

        >>> kyc.isRegistered('0x1d285a37d3afce3a200a1eeb6697e59d15e8dc0d9b5132391e3ee53c7a69f18a')
        True
        >>> kyc.isRegistered('0x81a5c449c2409c87d702e0c4a675313347faf1c39576af357dd75efe7cad4793')
        False

.. method:: KYCBase.isPermitted(address _addr)

    Given an address, returns a boolean to indicate if this address is permitted to transfer based on the following conditions:

    * Is the registring authority restricted?
    * Is the investor ID restricted?
    * Is the address restricted?
    * Has the investor's rating expired?

    .. code-block:: python

        >>> kyc.isPermitted(accounts[1])
        True
        >>> kyc.isPermitted(accounts[2])
        False

.. method:: KYCBase.isPermittedID(bytes32 _id)

    Returns a transfer permission boolean similar to ``KYCBase.isPermitted``, without a check on a specific address.

    .. code-block:: python

        >>> kyc.isPermittedID('0x1d285a37d3afce3a200a1eeb6697e59d15e8dc0d9b5132391e3ee53c7a69f18a(')
        True
        >>> kyc.isPermittedID('0x81a5c449c2409c87d702e0c4a675313347faf1c39576af357dd75efe7cad4793')
        False

Calls that Revert
-----------------

The remaining calls **will revert under some conditions**:

.. method:: KYCBase.getInvestor(address _addr)

    Returns the investor ID, permission status (based on the input address), rating, and country code for an investor.

    Reverts if the address is not registered.

    .. note:: This function is designed to maximize gas efficiency when calling for information prior to performing a token transfer.

    .. code-block:: python

        >>> kyc.getInvestor(a[1]).dict()
        {
            '_country': 784,
            '_id': "0x1d285a37d3afce3a200a1eeb6697e59d15e8dc0d9b5132391e3ee53c7a69f18a",
            '_permitted': True,
            '_rating': 1
        }
        >>> kyc..getInvestor(a[0])
        File "contract.py", line 277, in call
          raise VirtualMachineError(e)
        VirtualMachineError: VM Exception while processing transaction: revert Address not registered

.. method:: KYCBase.getInvestors(address _from, address _to)

    The two investor version of ``KYCBase.getInvestor``. Also used to maximize gas efficiency.

    .. code-block:: python

        >>> kyc.getInvestors(accounts[1], accounts[2]).dict()
        {
            '_country': (784, 784),
            '_id': ("0x1d285a37d3afce3a200a1eeb6697e59d15e8dc0d9b5132391e3ee53c7a69f18a", "0x9becd445b3c5703a4f1abc15870dd10c56bb4b4a70c68dba05e116551ab11b44"),
            '_permitted': (True, False),
            '_rating': (1, 2)
        }
        >>> kyc.getInvestors(accounts[1], accounts[3])
        File "contract.py", line 277, in call
          raise VirtualMachineError(e)
        VirtualMachineError: VM Exception while processing transaction: revert Receiver not Registered

.. method:: KYCBase.getRating(bytes32 _id)

    Returns the investor rating number for a given ID.

    Reverts if the ID is not registered.

    .. code-block:: python

        >>> kyc.getRating("0x1d285a37d3afce3a200a1eeb6697e59d15e8dc0d9b5132391e3ee53c7a69f18a")
        1
        >>> kyc.getRating("0x00")
        File "contract.py", line 277, in call
          raise VirtualMachineError(e)
        VirtualMachineError: VM Exception while processing transaction: revert

.. method:: KYCBase.getRegion(bytes32 _id)

    Returns the investor region code for a given ID.

    Reverts if the ID is not registered.

    .. code-block:: python

        >>> kyc.getRegion("0x1d285a37d3afce3a200a1eeb6697e59d15e8dc0d9b5132391e3ee53c7a69f18a")
        0x653500
        >>> kyc.getRegion("0x00")
        File "contract.py", line 277, in call
          raise VirtualMachineError(e)
        VirtualMachineError: VM Exception while processing transaction: revert

.. method:: KYCBase.getCountry(bytes32 _id)

    Returns the investor country code for a given ID.

    Reverts if the ID is not registered.

    .. code-block:: python

        >>> kyc.getCountry("0x1d285a37d3afce3a200a1eeb6697e59d15e8dc0d9b5132391e3ee53c7a69f18a")
        784
        >>> kyc.getCountry("0x00")
        File "contract.py", line 277, in call
          raise VirtualMachineError(e)
        VirtualMachineError: VM Exception while processing transaction: revert

.. method:: KYCBase.getExpires(bytes32 _id)

    Returns the investor rating expiration date (in epoch time) for a given ID.

    Reverts if the ID is not registered or the rating has expired.

    .. code-block:: python

        >>> kyc.getExpires("0x1d285a37d3afce3a200a1eeb6697e59d15e8dc0d9b5132391e3ee53c7a69f18a")
        1600000000
        >>> kyc.getExpires("0x00")
        File "contract.py", line 277, in call
          raise VirtualMachineError(e)
        VirtualMachineError: VM Exception while processing transaction: revert

Events
======

Both KYC implementations include the following events.

The ``authority`` value in each event is the ID hash of the authority that called the method where the event was emitted.

.. method:: KYCBase.NewInvestor(bytes32 indexed id, uint16 indexed country, bytes3 region, uint8 rating, uint40 expires, bytes32 indexed authority)

    Emitted when a new investor is added to the registry.

.. method:: KYCBase.UpdatedInvestor(bytes32 indexed id, bytes3 region, uint8 rating, uint40 expires, bytes32 indexed authority)

    Emitted when data about an existing investor is modified.

.. method:: KYCBase.InvestorRestriction(bytes32 indexed id, bool permitted, bytes32 indexed authority)

    Emitted when a restriction upon an investor is set or removed.

.. method:: KYCBase.RegisteredAddresses(bytes32 indexed id, address[] addr, bytes32 indexed authority)

    Emitted when new addresses are associated with an investor ID, or a existing addresses have a restriction removed.

.. method:: KYCBase.RestrictedAddresses(bytes32 indexed id, address[] addr, bytes32 indexed authority)

    Emitted when a restriction is set upon addresses associated with an investor ID.
