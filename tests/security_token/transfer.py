#!/usr/bin/python3

from brownie import *
from scripts.deployment import main


def setup():
    main(SecurityToken)
    global token, issuer
    token = SecurityToken[0]
    issuer = IssuingEntity[0]
    token.mint(issuer, 1000000, {'from': a[0]})

def issuer_to_investor():
    '''transfer from issuer to investors'''
    token.transfer(a[1], 1000, {'from': a[0]})
    check.equal(issuer.getInvestorCounts()[0][0], 1)