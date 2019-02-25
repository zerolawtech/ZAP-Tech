#!/usr/bin/python3

from brownie import *

import itertools

def main():
    kyc = accounts[0].deploy(KYCRegistrar, [accounts[0]], 1)
    issuer = accounts[1].deploy(IssuingEntity, [accounts[1]], 1)
    token = accounts[1].deploy(NFToken, issuer, "Test NFToken", "NFT", 1000000)
    issuer.addToken(token, {'from': accounts[1]})
    token.mint(issuer, 1000000, 0, "0x00", {'from': accounts[1]})
    issuer.setRegistrar(kyc, True, {'from': accounts[1]})
    
    # Approves accounts[2:8] in KYCRegistrar, with investor ratings 1-2 and country codes 1-3
    for count,country,rating in [(c,i[0],i[1]) for c,i in enumerate(itertools.product([1,2,3], [1,2]), start=2)]:
        kyc.addInvestor("investor"+str(count), country, 'aws', rating, 9999999999, [accounts[count]], {'from': accounts[0]})
    
    # Approves investors from country codes 1-3 in IssuingEntity
    issuer.setCountries([1,2,3],[1,1,1],[0,0,0], {'from': accounts[1]})
