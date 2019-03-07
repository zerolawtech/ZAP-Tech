from brownie import *

def setup():
    config['test']['default_contract_owner'] = False

    global a, countries
    global owner1, owner2
    global authority1, authority2
    global investor1, investor2
    global scratch1 
    global ahash, investorID
    global registrar, token
    countries = [1,2,3]
    a = accounts
    owner1 = a[0]; 
    owner2 = a[1]
    authority1 = a[2]; 
    authority2 = a[3]
    investor1 = a[4]; 
    investor2 = a[5]
    scratch1 = a[9]
    investorID1 = "0xaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"
    investorID2 = "0xbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb"
    registrar = owner1.deploy(KYCRegistrar, [owner1], 1)
    registrar.addInvestor(investorID1, 3, b'abc', 1, 9999999999, [investor1], {'from':owner1})
    registrar.addInvestor(investorID2, 3, b'abc', 1, 9999999999, [investor2], {'from':owner1})


def initial_total_supply_of_issuer_is_zero():
    issuer = owner1.deploy(IssuingEntity, [owner1], 1)
    token = owner1.deploy(SecurityToken, issuer.address, "TOKEN", "TKN", 1000)
    check.equal(token.balanceOf(issuer.address), 0, "Issuer balance is wrong")
