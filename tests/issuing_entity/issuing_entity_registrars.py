from brownie import *

def setup():
    config['test']['default_contract_owner'] = False

    global a, countries
    global owner1, owner2
    global authority1, authority2
    global investor1, investor2
    global scratch1
    global ahash, investorID1, investorID2
    global registrar, token
    countries = [1,2,3]
    a = accounts
    owner1 = a[0]
    owner2 = a[1]
    authority1 = a[2]
    authority2 = a[3]
    investor1 = a[4]
    investor2 = a[5]
    scratch1 = a[9]
    investorID1 = "0xaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"
    investorID2 = "0xbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb"
    registrar = owner1.deploy(KYCRegistrar, [owner1], 1)
    registrar.addInvestor(investorID1, 3, b'abc', 1, 9999999999, [investor1], {'from':owner1})
    registrar.addInvestor(investorID2, 3, b'abc', 1, 9999999999, [investor2], {'from':owner1})


# TODO: setRegistrar tests: multisig

#########################################
# getInvestorRegistrar success path tests

# TODO: success path - investor has done a transaction before calling getInvestorRegistrar
# and is thus know to the contract

def getInvestorRegistrar_of_inactive_investor_returns_zero():
    issuer = owner1.deploy(IssuingEntity, [owner1], 1)
    check.true(issuer.setRegistrar(registrar, True, {'from':owner1}).return_value)
    addr = issuer.getInvestorRegistrar(investorID1)
    check.equal(addr, 0x00)

# Test needs fixing - countres need to be set up properly
def getInvestorRegistrar_returns_registrar(skip=True):
    issuer = owner1.deploy(IssuingEntity, [owner1], 1)
    check.true(issuer.setRegistrar(registrar, True, {'from':owner1}).return_value)
    token = owner1.deploy(SecurityToken, issuer.address, "TOKEN", "TKN", 1000)
    issuer.addToken(token.address, {'from':owner1})
    token.checkTransfer(issuer.address, investor1, 1)
    addr = issuer.getInvestorRegistrar(investorID1)
    check.equal(addr, registrar.address)
