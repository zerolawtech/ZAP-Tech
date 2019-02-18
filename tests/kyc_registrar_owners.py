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

#################################
# addAuthority failing path tests

def addAuthority_threshold_of_zero_fails():
    '''Owner can't call addAuthority with _threshold of 0'''
    registrar = a[0].deploy(KYCRegistrar, [accounts[0]], 1)
    check.reverts(registrar.addAuthority, [[a[1]], countries, 0])

def threshold_of_two_multisig_check_one_owner_cant_multisig():
    '''Check one owner can't repeatedly increase multisig counts'''
    registrar = a[0].deploy(KYCRegistrar, [a[0], a[1]], 2)
    check.false(registrar.addAuthority([a[3]], countries, 1, {'from':a[0]}).return_value)
    # same owner makes the call again
    check.reverts(registrar.addAuthority, ([a[3]], countries, 1, {'from':a[0]}))

def setAuthorityThreshold_cannot_set_threshold_to_zero():
    '''setAuthorityThreshold cannot set _threshold to 0'''
    registrar = a[0].deploy(KYCRegistrar, [a[0], a[1]], 1)
    check.true(registrar.addAuthority([a[3]], countries, 1, {'from':a[1]}).return_value)
    authority_id = registrar.getID(a[3])
    check.reverts(registrar.setAuthorityThreshold, [authority_id, 0])


#################################
# addAuthority success path tests

def addAuthority_threshold_of_one_passses():
    '''Owner can addAuthority when threshold is 1'''
    registrar = a[0].deploy(KYCRegistrar, [accounts[0]], 1)
    txr = registrar.addAuthority([a[1]], countries, 1)
    check.true(txr.return_value)
    check.event_fired(txr, 'NewAuthority')

def threshold_of_two_multisig_check_both_owners_can_multisig():
    '''Check two owners can increase multisig counts'''
    registrar = a[0].deploy(KYCRegistrar, [a[0], a[1]], 2)
    check.false(registrar.addAuthority([a[3]], countries, 1, {'from':a[0]}).return_value)
    txr = registrar.addAuthority([a[3]], countries, 1, {'from':a[1]})
    check.true(txr.return_value)
    check.event_fired(txr, 'NewAuthority')

