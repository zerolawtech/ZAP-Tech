#!/usr/bin/python3


from brownie import *
from scripts.deploy_simple import main

def setup():
    config['test']['default_contract_owner'] = False

    global a, countries
    global owner1, owner2
    global authority1, authority2
    global scratch1, scratch2
    global registrar
    global investorID, investorID2
    global issuer, token, mint
    countries = [1,2,3]
    owner1 = accounts[0]
    owner2 = accounts[1]
    unknown_address = accounts[9]
    investorID = b"aaaainvestor"

    kyc = accounts[0].deploy(KYCRegistrar, [owner1], 1)
    issuer = owner1.deploy(IssuingEntity, [owner1], 1)
    token = owner1.deploy(SecurityToken, issuer, "Test Token", "TST", 1000000)
    issuer.addToken(token, {'from': owner1})
    issuer.setRegistrar(kyc, True, {'from': owner1})

    # Approves investors from country codes 1-3 in IssuingEntity
    issuer.setCountries([1,2,3],[1,1,1],[0,0,0], {'from': owner1})

# TODO: review for completeness, these are mainly just the original tests

# TODO: These are part of the original tests before Brownie was updated to use
#       a setup function and reset the EVM between tests.

# def dividend_setup():
#     '''Dividend: deploy and attach'''
#     global dividend_time, dividend, cust
#     cust = accounts[0].deploy(Custodian, [a[0]], 1)
#     issuer.addCustodian(cust)
#     dividend_time = int(time.time()+3)
#     dividend = check.confirms(
#         owner1.deploy,
#         (DividendModule, token.address, issuer.address, dividend_time),
#         "Should have deployed Dividend module")
#     # Account 2 was able to attach
#     check.reverts(
#         issuer.attachModule,
#         (token.address, dividend.address, {'from':accounts[2]}))
#     check.confirms(
#         issuer.attachModule,
#         (token.address, dividend.address),
#         "Unable to attach module")

# def dividend_transfer():
#     '''Dividend: transfer tokens before claim time'''
#     token.transfer(accounts[2], 100)
#     token.transfer(cust,100,{'from':accounts[2]})
#     cust.transfer(token,accounts[2],100,False)
#     token.transfer(accounts[2], 300)
#     token.transfer(accounts[3], 200)
#     token.transfer(accounts[4], 500)
#     token.transfer(accounts[5], 100, {'from':accounts[4]})
#     token.transfer(accounts[6], 900)
#     token.transfer(cust,200,{'from':accounts[6]})
#     token.transferFrom(accounts[6], accounts[7], 600, {'from':owner1})
#     check.equal(token.circulatingSupply(), 2000, "Circulating supply is wrong")

# def dividend_mint():
#     '''Dividend: attach MintBurn, mint and burn tokens'''
#     issuer.attachModule(issuer.address, mint.address)
#     mint.mint(token.address, 1000000)
#     mint.burn(token.address, 500000)
#     issuer.detachModule(issuer.address, mint.address)

# def dividend_transfer2():
#     '''Dividend: transfer tokens after claim time'''
#     if dividend_time > time.time():
#         time.sleep(dividend_time-time.time()+1)
#     token.transfer(accounts[2], 100000)
#     token.transfer(accounts[2], 10000)

# def dividend_issue():
#     '''Dividend: issue the dividend'''
#     # Dividend was successfully issued by account 2
#     check.reverts(
#         dividend.issueDividend,
#         (100, {'from':accounts[2], 'value':"10 ether"}))
#     # Was able to issue a dividend without sending any eth
#     check.reverts(dividend.issueDividend, (100,))
#     check.confirms(
#         dividend.issueDividend,
#         (100, {'value':"20 ether"}),
#         "Unable to issue Dividend")
#     # Was able to call issueDividend twice
#     check.reverts(
#         dividend.issueDividend,
#         (100, {'value':"10 ether"}))

# def dividend_claim():
#     '''Dividend: claim dividends'''
#     blank = "0x"+("0"*40)
#     # Issuer was able to claim
#     check.reverts(
#         dividend.claimDividend,
#         (owner1,))
#     dividend.claimCustodianDividend(cust,issuer.getID(a[6]),a[6],{'from':a[6]})
#     # Was able to claim custodian dividend twice
#     check.reverts(
#         dividend.claimCustodianDividend,
#         (cust,issuer.getID(a[6]),a[6],{'from':a[6]})
#     )
#     for i,final in enumerate([wei(4e18), wei(2e18), wei(4e18), wei(1e18), wei(1e18), wei(6e18)], start=2):
#         balance = accounts[i].balance()
#         tx = dividend.claimDividend(accounts[i], {'from':accounts[i]})
#         check.equal(accounts[i].balance(), balance+final-(tx.gasUsed*tx.gasPrice), "Dividend payout wrong: {}".format(i))
#         check.reverts(dividend.claimDividend,(accounts[i],), "Able to claim twice")

# def dividend_close():
#     '''Dividend: close dividends'''
#     dividend.closeDividend()
#     token.transfer(accounts[2], 100)
