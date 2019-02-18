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


