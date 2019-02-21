#!/usr/bin/python3

from brownie import *

def setup():
    global a, countries
    countries = [1,2,3]
    a = accounts
    global owner1, owner2
    global authority1, authority2
    global investor1, investor2
    global scratch1 
    owner1 = a[0]; 
    owner2 = a[1]
    authority1 = a[2]; 
    authority2 = a[3]
    investor1 = a[4]; 
    investor2 = a[5]
    scratch1 = a[9]


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

def test_generateID():
    registrar = a[0].deploy(KYCRegistrar, [a[0]], 1)
    check.confirms(registrar.generateID, ["this is some string"])

def test_getInvestorByID():
    registrar = a[0].deploy(KYCRegistrar, [a[0]], 1)
    id_ = "foobar"
    registrar.addInvestor(id_, 3, 1, 2, 9999999999, [a[1]], {'from': a[0]})
    investor = registrar.getInvestorByID(id_)
    check.equal(investor[0], True)
    check.equal(investor[1], 2)
    check.equal(investor[2], 3)

def test_getInvestorsByID():
    registrar = a[0].deploy(KYCRegistrar, [a[0]], 1)
    id1 = "investor1"
    id2 = "investor2"
    registrar.addInvestor(id1, 3, 1, 4, 9999999999, [a[1]], {'from': a[0]})
    registrar.addInvestor(id2, 2, 1, 5, 9999999999, [a[2]], {'from': a[0]})
    investors = registrar.getInvestorsByID(id1, id2)
    check.equal(investors[0][0], True)
    check.equal(investors[0][1], True)
    check.equal(investors[1][0], 4)
    check.equal(investors[1][1], 5)
    check.equal(investors[2][0], 3)
    check.equal(investors[2][1], 2)

def test_getInvestors():
    registrar = a[0].deploy(KYCRegistrar, [a[0]], 1)
    id1 = "0x01"
    id2 = "0x02"
    registrar.addInvestor(id1, 3, 1, 4, 9999999999, [a[1]], {'from': a[0]})
    registrar.addInvestor(id2, 2, 1, 5, 9999999999, [a[2]], {'from': a[0]})
    investors = registrar.getInvestors(a[1], a[2])
    check.equal(investors[0][0], id1)
    check.equal(investors[0][1], id2)
    check.equal(investors[1][0], True)
    check.equal(investors[1][1], True)
    check.equal(investors[2][0], 4)
    check.equal(investors[2][1], 5)
    check.equal(investors[3][0], 3)
    check.equal(investors[3][1], 2)

def test_isRegistered():
    registrar = a[0].deploy(KYCRegistrar, [a[0]], 1)
    id1 = "investor1"
    id2 = "investor2"
    registrar.addInvestor(id1, 3, 1, 4, 9999999999, [a[1]], {'from': a[0]})
    check.equal(registrar.isRegistered(id1), True)
    check.equal(registrar.isRegistered(id2), False)
