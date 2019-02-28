#!/usr/bin/python3


from brownie import *
from scripts.deploy_simple import main

def setup():
    config['test']['default_contract_owner'] = False

    global a, countries
    global owner1, owner2
    global unknown_address
    global registrar
    global investorID
    global issuer, token
    countries = [1,2,3]
    owner1 = accounts[0]
    owner2 = accounts[1]
    unknown_address = accounts[9]
    investorID = b"aaaainvestor"

    issuer = owner1.deploy(IssuingEntity, [owner1], 1)
    token = owner1.deploy(SecurityToken, issuer, "Test Token", "TST", 1000000)
    issuer.addToken(token, {'from': owner1})
    
    # Approves investors from country codes 1-3 in IssuingEntity
    issuer.setCountries([1,2,3],[1,1,1],[0,0,0], {'from': owner1})
    issuer = IssuingEntity[0]
    token = SecurityToken[0]


# TODO: mint directly to Investor
# TODO: review for completeness, these are mainly just the original tests

def mint_tokens_to_issuer():
    token.mint(token.address, 1000000, {'from':owner1})
    check.equal(token.balanceOf(issuer.address), 1000000)

def mint_tokens_by_unauthorised_address():
    check.reverts(
        token.mint,
        [token.address, 1, {'from':unknown_address}]
    )

def successful_burn():
    token.mint(token.address, 1000000, {'from':owner1})
    token.burn(token.address, 1000000, {'from':owner1})
    check.equal(token.balanceOf(issuer.address), 0)

def burn_by_unauthorised_address():
    token.mint(token.address, 1000000, {'from':owner1})
    check.reverts(
        token.burn, 
        [token.address, 1000000, {'from':unknown_address}]
        )

def attempt_to_burn_more_tokens_than_balance():
    token.mint(token.address, 1000000, {'from':owner1})
    check.reverts(
        token.burn, 
        [token.address, 2000000, {'from':owner1}]
        )

def attempt_to_burn_when_balance_is_zero():
    check.reverts(
        token.burn, 
        [token.address, 1, {'from':owner1}]
        )

