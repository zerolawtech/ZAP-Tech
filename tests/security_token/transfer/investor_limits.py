#!/usr/bin/python3

from brownie import *
from scripts.deployment import main


def setup():
    main(SecurityToken)
    global token, issuer, kyc
    token = SecurityToken[0]
    issuer = IssuingEntity[0]
    kyc = KYCRegistrar[0]
    token.mint(issuer, 1000000, {'from': a[0]})
    issuer.setCountries(
        [1, 2, 3, 4, 5],    # country
        [1, 1, 1, 1, 1],    # minRating
        [0, 0, 0, 0, 0],    # limit
        {'from': a[0]}
    )
    issuer.setInvestorLimits([3, 2, 2, 1, 0, 0, 0, 0], {'from': a[0]})

def receiver_blocked_rating():
    '''receiver blocked - rating'''
    issuer.setCountry(1, True, 3, [0]*8, {'from':a[0]})
    check.reverts(
        token.transfer,
        (a[1], 1000, {'from': a[0]}),
        "Receiver blocked: Rating"
    )

def total_investor_limit_blocked_issuer_investor():
    '''total investor limit - blocked, issuer to investor'''
    issuer.setInvestorLimits([1,0,0,0,0,0,0,0], {'from':a[0]})
    token.transfer(a[1], 1000, {'from': a[0]})
    check.reverts(
        token.transfer,
        (a[2], 1000, {'from': a[0]}),
        "Total Investor Limit"
    )

def total_investor_limit_blocked_investor_investor():
    '''total investor limit - blocked, investor to investor'''
    issuer.setInvestorLimits([1,0,0,0,0,0,0,0], {'from':a[0]})
    token.transfer(a[1], 1000, {'from': a[0]})
    check.reverts(
        token.transfer,
        (a[2], 500, {'from': a[1]}),
        "Total Investor Limit"
    )

def total_investor_limit_issuer_investor():
    '''total investor limit - issuer to existing investor'''
    issuer.setInvestorLimits([1,0,0,0,0,0,0,0], {'from':a[0]})
    token.transfer(a[1], 1000, {'from': a[0]})
    token.transfer(a[1], 1000, {'from': a[0]})

def total_investor_limit_investor_investor():
    '''total investor limit - investor to investor, full balance'''
    issuer.setInvestorLimits([1,0,0,0,0,0,0,0], {'from':a[0]})
    token.transfer(a[1], 1000, {'from': a[0]})
    token.transfer(a[2], 1000, {'from': a[1]})

def total_investor_limit_rating_blocked_issuer_investor():
    '''total investor limit, rating - blocked, issuer to investor'''
    issuer.setInvestorLimits([0,1,0,0,0,0,0,0], {'from':a[0]})
    token.transfer(a[1], 1000, {'from': a[0]})
    check.reverts(
        token.transfer,
        (a[3], 1000, {'from': a[0]}),
        "Total Investor Limit: Rating"
    )

def total_investor_limit_rating_blocked_investor_investor():
    '''total investor limit, rating - blocked, investor to investor'''
    issuer.setInvestorLimits([0,1,0,0,0,0,0,0], {'from':a[0]})
    token.transfer(a[1], 1000, {'from': a[0]})
    check.reverts(
        token.transfer,
        (a[3], 500, {'from': a[1]}),
        "Total Investor Limit: Rating"
    )

def total_investor_limit_rating_issuer_investor():
    '''total investor limit, rating - issuer to existing investor'''
    issuer.setInvestorLimits([0,1,0,0,0,0,0,0], {'from':a[0]})
    token.transfer(a[1], 1000, {'from': a[0]})
    token.transfer(a[1], 1000, {'from': a[0]})

def total_investor_limit_rating_investor_investor():
    '''total investor limit, rating - investor to investor, full balance'''
    issuer.setInvestorLimits([0,1,0,0,0,0,0,0], {'from':a[0]})
    token.transfer(a[1], 1000, {'from': a[0]})
    token.transfer(a[2], 1000, {'from': a[1]})

def total_investor_limit_rating_investor_investor_different_country():
    '''total investor limit, rating - investor to investor, different rating'''
    issuer.setInvestorLimits([0,1,0,0,0,0,0,0], {'from':a[0]})
    token.transfer(a[1], 1000, {'from': a[0]})
    token.transfer(a[2], 500, {'from': a[1]})