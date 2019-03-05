from brownie import *

def setup():
    config['test']['default_contract_owner'] = True

    global a, countries
    countries = [1,2,3]
    a = accounts
    global owner1, owner2
    global authority1, authority2
    global scratch1 
    owner1 = a[0];
    owner2 = a[1]
    authority1 = a[2]; 
    authority2 = a[3]
    scratch1 = a[9]

#################################
# addAuthority failing path tests

def addAuthority_threshold_of_zero_fails():
    registrar = a[0].deploy(KYCRegistrar, [accounts[0]], 1)
    check.reverts(registrar.addAuthority, [[a[1]], countries, 0])

def threshold_of_two_multisig_check_one_owner_cant_multisig():
    registrar = a[0].deploy(KYCRegistrar, [a[0], a[1]], 2)
    check.false(registrar.addAuthority([a[3]], countries, 1, {'from':a[0]}).return_value)
    # same owner makes the call again
    check.reverts(registrar.addAuthority, ([a[3]], countries, 1, {'from':a[0]}))

def setAuthorityThreshold_cannot_set_threshold_to_zero():
    registrar = a[0].deploy(KYCRegistrar, [a[0], a[1]], 1)
    check.true(registrar.addAuthority([a[3]], countries, 1, {'from':a[1]}).return_value)
    authority_id = registrar.getID(a[3])
    check.reverts(registrar.setAuthorityThreshold, [authority_id, 0])

def setAuthorityThreshold_cant_be_called_on_nonauthority():
    registrar = a[0].deploy(KYCRegistrar, [accounts[0]], 1)
    registrar.addInvestor(b"investor8", 1, b'abc', 1, 9999999999, [scratch1], {'from':owner1})
    id_ = registrar.getID(scratch1)
    txr = check.reverts(registrar.setAuthorityThreshold, (id_, 1, {'from': owner1}))

#################################
# addAuthority success path tests

def addAuthority_threshold_of_one_passses():
    registrar = a[0].deploy(KYCRegistrar, [accounts[0]], 1)
    txr = registrar.addAuthority([a[1]], countries, 1)
    check.true(txr.return_value)
    check.event_fired(txr, 'NewAuthority')

def addAuthority_multisig():
    registrar = a[0].deploy(KYCRegistrar, [a[0], a[1]], 2)
    check.false(registrar.addAuthority([a[3]], countries, 1, {'from':a[0]}).return_value)
    txr = registrar.addAuthority([a[3]], countries, 1, {'from':a[1]})
    check.true(txr.return_value)
    check.event_fired(txr, 'NewAuthority')

#################################
# setAuthorityRestriction success path tests

# See the _investors tests for tests that the restriction
# is enforced

def setAuthorityRestriction_threshold_of_one_passses():
    registrar = a[0].deploy(KYCRegistrar, [accounts[0]], 1)
    registrar.addAuthority([authority1], countries, 1)
    id_ = registrar.getID(authority1)
    txr = registrar.setAuthorityRestriction(id_, False)
    check.true(txr.return_value)
    check.event_fired(txr, 'AuthorityRestriction')
    check.reverts(registrar.addInvestor, (b"investor8", 1, b'abc', 1, 9999999999, [scratch1], {'from':authority1}))
    # now unwind the restriction and check we can addInvestor
    txr = registrar.setAuthorityRestriction(id_, True)
    check.event_fired(txr, 'AuthorityRestriction')
    txr = registrar.addInvestor(b"investor8", 1, b'abc', 1, 9999999999, [scratch1], {'from':authority1})
    check.event_fired(txr, 'NewInvestor')

def setAuthorityRestriction_multisig():
    registrar = a[0].deploy(KYCRegistrar, [a[0], a[1]], 2)
    registrar.addAuthority([authority1], countries, 1, {'from':a[0]})
    registrar.addAuthority([authority1], countries, 1, {'from':a[1]})
    id_ = registrar.getID(authority1)
    txr = registrar.setAuthorityRestriction(id_, False, {'from':a[0]})
    check.event_not_fired(txr, 'AuthorityRestriction')
    txr = registrar.setAuthorityRestriction(id_, False, {'from':a[1]})
    check.event_fired(txr, 'AuthorityRestriction')
    check.reverts(registrar.addInvestor, (b"investor8", 1, b'abc', 1, 9999999999, [scratch1], {'from':authority1}))
    # now unwind the restriction and check we can addInvestor
    txr = registrar.setAuthorityRestriction(id_, True, {'from':a[0]})
    check.event_not_fired(txr, 'AuthorityRestriction')
    txr = registrar.setAuthorityRestriction(id_, True, {'from':a[1]})
    check.event_fired(txr, 'AuthorityRestriction')
    txr = registrar.addInvestor(b"investor8", 1, b'abc', 1, 9999999999, [scratch1], {'from':authority1})
    check.event_fired(txr, 'NewInvestor')

#################################
# setAuthorityRestriction fail path tests

def setAuthorityRestriction_cant_be_called_on_nonauthority():
    registrar = a[0].deploy(KYCRegistrar, [accounts[0]], 1)
    registrar.addInvestor(b"investor8", 1, b'abc', 1, 9999999999, [scratch1], {'from':owner1})
    id_ = registrar.getID(scratch1)
    txr = check.reverts(registrar.setAuthorityRestriction, (id_, False, {'from': owner1}))




#######################################
# setInvestorRestriction

def owner_can_restrict_an_investor():
    investorID = b"investor8"
    registrar = a[0].deploy(KYCRegistrar, [accounts[0]], 1)
    registrar.addInvestor(investorID, 3, b'abc', 1, 9999999999, [scratch1])
    txr = registrar.setInvestorRestriction(investorID, False)
    check.event_fired(txr, 'InvestorRestriction')

#######################################
# setAuthorityCountries

# TODO: permissive and restrictive - add or remove
# TODO: effect on an investor if a country is removed? .. shouldn't matter.
# authority doesn't exist
# is not owner
# test that it works?

def setAuthorityCountries_multisig():
    registrar = a[0].deploy(KYCRegistrar, [a[0], a[1]], 2)
    registrar.addAuthority([authority1], countries, 1, {'from':a[0]})
    registrar.addAuthority([authority1], countries, 1, {'from':a[1]})
    id_ = registrar.getID(authority1)
    txr = registrar.setAuthorityCountries(id_, [5], True, {'from':a[0]})
    check.false(txr.return_value)
    txr = registrar.setAuthorityCountries(id_, [5], True, {'from':a[1]})
    check.true(txr.return_value)
