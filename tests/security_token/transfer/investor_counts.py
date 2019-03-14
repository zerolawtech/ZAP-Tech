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
    '''global investor counts - issuer/investor transfers'''
    check.equal(issuer.getInvestorCounts()[0][:3], (0, 0, 0))
    token.transfer(a[1], 1000, {'from': a[0]})
    check.equal(issuer.getInvestorCounts()[0][:3], (1, 1, 0))
    token.transfer(a[1], 1000, {'from': a[0]})
    check.equal(issuer.getInvestorCounts()[0][:3], (1, 1, 0))
    token.transfer(a[1], 998000, {'from': a[0]})
    check.equal(issuer.getInvestorCounts()[0][:3], (1, 1, 0))
    token.transfer(a[0], 1000, {'from': a[1]})
    check.equal(issuer.getInvestorCounts()[0][:3], (1, 1, 0))
    token.transfer(a[0], 999000, {'from': a[1]})
    check.equal(issuer.getInvestorCounts()[0][:3], (0, 0, 0))

def investor_to_investor():
    '''global investor counts - investor/investor transfers'''
    token.transfer(a[1], 1000, {'from': a[0]})
    token.transfer(a[2], 1000, {'from': a[0]})
    token.transfer(a[3], 1000, {'from': a[0]})
    token.transfer(a[4], 1000, {'from': a[0]})
    check.equal(issuer.getInvestorCounts()[0][:3], (4, 2, 2))
    token.transfer(a[2], 500, {'from': a[1]})
    check.equal(issuer.getInvestorCounts()[0][:3], (4, 2, 2))
    token.transfer(a[2], 500, {'from': a[1]})
    check.equal(issuer.getInvestorCounts()[0][:3], (3, 1, 2))
    token.transfer(a[3], 2000, {'from': a[2]})
    check.equal(issuer.getInvestorCounts()[0][:3], (2, 1, 1))
    token.transfer(a[3], 1000, {'from': a[4]})
    check.equal(issuer.getInvestorCounts()[0][:3], (1, 1, 0))
    token.transfer(a[4], 500, {'from': a[3]})
    check.equal(issuer.getInvestorCounts()[0][:3], (2, 1, 1))