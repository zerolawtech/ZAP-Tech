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

def whitelist_public_abi():
    '''Public ABI only contains the expected methods'''
    registrar = a[0].deploy(KYCRegistrar, [a[0], a[1]], 2)
    methods = set(registrar.signatures.keys())
    expected_methods = set([
        "addAuthority",
        "setAuthorityCountries",
        "setAuthorityThreshold",
        "setAuthorityRestriction",
        "generateID",
        "addInvestor",
        "updateInvestor",
        "setInvestorRestriction",
        "setInvestorAuthority",
        "registerAddresses",
        "restrictAddresses",
        "isRegistered",
        "getID",
        "isPermitted",
        "isPermittedID",
        "getInvestor",
        "getInvestorByID",
        "getInvestors",
        "getInvestorsByID",
        "getRating",
        "getRegion",
        "getCountry",
        "getExpires",
    ])
    check.true(methods == expected_methods, "Unexpected ["+", ".join(methods.difference(expected_methods))+"] or missing ["+", ".join(expected_methods.difference(methods))+"] methods in the publically exposed ABI")

def constructor_with_threshold_of_zero_fails():
    '''Contract will not deploy with _threshold of 0'''
    check.reverts(a[0].deploy, [KYCRegistrar, [accounts[0]], 0])

def constructor_with_threshold_too_high_fails():
    '''Contract will not deploy with _threshold > #owners'''
    check.reverts(a[0].deploy, [KYCRegistrar, [a[0]], 2])

################################################
# Owners

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
    tx_receipt = registrar.addAuthority([a[1]], countries, 1)
    check.true(tx_receipt.return_value)
    check.true(tx_receipt.events[-1]['name'] == 'NewAuthority')

def threshold_of_two_multisig_check_both_owners_can_multisig():
    '''Check two owners can increase multisig counts'''
    registrar = a[0].deploy(KYCRegistrar, [a[0], a[1]], 2)
    check.false(registrar.addAuthority([a[3]], countries, 1, {'from':a[0]}).return_value)
    check.true(registrar.addAuthority([a[3]], countries, 1, {'from':a[1]}).return_value)

def check_multisig_resets():
    '''multisig resets when call is successful'''
    registrar = a[0].deploy(KYCRegistrar, [a[0], a[1]], 2)
    check.false(registrar.addAuthority([a[3]], countries, 1, {'from':a[0]}).return_value)
    check.true(registrar.addAuthority([a[3]], countries, 1, {'from':a[1]}).return_value)
    authority_id = registrar.getID(a[3])
    # we just pick setAuthorityThreshold as something an owner could do twice
    check.false(registrar.setAuthorityThreshold(authority_id, 1, {'from':a[0]}).return_value)
    check.true(registrar.setAuthorityThreshold(authority_id, 1, {'from':a[1]}).return_value)
    check.false(registrar.setAuthorityThreshold(authority_id, 1, {'from':a[0]}).return_value)
    check.true(registrar.setAuthorityThreshold(authority_id, 1, {'from':a[1]}).return_value)


