#!/usr/bin/python3

from brownie import *

def setup():
    # is this passing a threshold of zero?
    global a, countries
    countries = [1,2,3]
    a = accounts
    global owner1, owner2
    owner1 = a[0]; owner2 = a[1]
    global scratch1 
    scratch1 = a[-1]

# TODO: restricted addresses
# TODO: multisig for owners and authorities
# TODO: When restricing addresses associated to an authority, you cannot reduce the number of addresses such that the total remaining is lower than the multi-sig threshold value for that authority.

################################################
# Addresses

# Owners controlling owners

def owner_can_add_a_new_owner_address():
    registrar = owner1.deploy(KYCRegistrar, [owner1, owner2], 1)
    ownerID = registrar.getID(owner1)
    txr = registrar.registerAddresses(ownerID, [scratch1])
    check.equal(txr.return_value, True)
    check.equal(registrar.getID(scratch1), ownerID) # new address gets added to existing ID
    
def one_owner_cant_add_a_new_owner_address_when_multisig():
    registrar = owner1.deploy(KYCRegistrar, [owner1, owner2], 2)
    ownerID = registrar.getID(owner1)
    txr = registrar.registerAddresses(ownerID, [scratch1])
    check.equal(txr.return_value, False)

def owner_cant_restrict_an_owner_address_multisig():
    registrar = owner1.deploy(KYCRegistrar, [owner1, owner2], 2)
    ownerID = registrar.getID(owner1)
    txr = registrar.restrictAddresses(ownerID, [owner2])
    check.equal(txr.return_value, False)
    check.event_not_fired(txr, 'RestrictedAddresses')

def owner_can_restrict_an_owner_address():
    registrar = owner1.deploy(KYCRegistrar, [owner1, owner2], 1)
    ownerID = registrar.getID(owner1)
    txr = registrar.restrictAddresses(ownerID, [owner2])
    check.equal(txr.return_value, True)
    check.event_fired(txr, 'RestrictedAddresses' , 1)

def owner_can_unrestrict_an_owner_address():
    registrar = owner1.deploy(KYCRegistrar, [owner1, owner2], 1)
    ownerID = registrar.getID(owner1)
    txr = registrar.restrictAddresses(ownerID, [owner2], {'from':owner1})
    check.equal(txr.return_value, True)
    check.event_fired(txr, 'RestrictedAddresses' , 1)
    txr = registrar.registerAddresses(ownerID, [owner2], {'from':owner1})
    check.equal(txr.return_value, True)
    check.event_fired(txr, 'RegisteredAddresses' , 1)

def owner_cant_unrestrict_their_own_address():
    registrar = owner1.deploy(KYCRegistrar, [owner1, owner2], 1)
    ownerID = registrar.getID(owner1)
    txr = registrar.restrictAddresses(ownerID, [owner2])
    txr = registrar.registerAddresses(ownerID, [owner2], {'from':owner2})
    check.false(registrar.isPermitted(owner2))

def restricted_owner_calling_registerAddresses_doesnt_fire_RegisteredAddresses(pending=True):
    registrar = owner1.deploy(KYCRegistrar, [owner1, owner2], 1)
    ownerID = registrar.getID(owner1)
    txr = registrar.restrictAddresses(ownerID, [owner2])
    check.equal(txr.return_value, True)
    check.event_fired(txr, 'RestrictedAddresses' , 1)
    txr = registrar.registerAddresses(ownerID, [owner2], {'from':owner2})
    check.false(registrar.isPermitted(owner2), False)
    check.event_not_fired(txr, 'RegisteredAddresses')
    check.equal(txr.return_value, False)

def restricted_owner_address_cant_add_a_new_owner_address(pending=True):
    registrar = owner1.deploy(KYCRegistrar, [owner1, owner2], 1)
    ownerID = registrar.getID(owner1)
    txr = registrar.restrictAddresses(ownerID, [owner2])
    txr = registrar.registerAddresses(ownerID, [scratch1], {'from':owner2})
    check.not_equal(registrar.getID(scratch1), ownerID)

# Owners controlling authorities

def owner_can_add_a_new_authority_address(skip=True):
    pass

def owner_can_restrict_an_authority_address(skip=True):
    pass

def restricted_owner_address_cant_add_a_new_authority_address(skip=True):
    pass

def restricted_owner_address_cant_restrict_an_authority_address(skip=True):
    pass

# Authorities

def authority_cant_add_a_new_authority_address(skip=True):
    # only owner can do this
    pass

def authority_cant_add_a_new_owner_address(skip=True):
    # only owner can do this
    pass

def authority_can_add_a_new_investor_address_in_their_country(skip=True):
    # given two authorities for country X then both can add addresses
    # for an investor in that country
    pass

# Investors

def investor_cant_add_a_new_address(skip=True):
    # only owner/authorities can do this
    pass




