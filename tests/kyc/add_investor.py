#!/usr/bin/python3

from brownie import *
from scripts.deployment import main


def setup():
    config['test']['always_transact'] = False
    kyc = accounts[0].deploy(KYCRegistrar, [accounts[0]], 1)
    issuer = accounts[0].deploy(IssuingEntity, [accounts[0]], 1)
    token = accounts[0].deploy(token_contract, issuer, "Test NFT", "NFT", 1000000)
    issuer.addToken(token, {'from': accounts[0]})
    issuer.setRegistrar(kyc, True, {'from': accounts[0]})