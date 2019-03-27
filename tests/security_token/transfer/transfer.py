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
        [1, 1, 1, 2, 2],    # minRating
        [1, 2, 2, 3, 3],    # limit
        {'from': a[0]}
    )
    issuer.setInvestorLimits([3, 2, 2, 1, 0, 0, 0, 0], {'from': a[0]})

def global_lock():
    '''global lock - investor / investor'''
    token.transfer(a[1], 1000, {'from': a[0]})
    issuer.setGlobalRestriction(False, {'from': a[0]})
    check.reverts(
        token.transfer,
        (a[2], 1000, {'from': a[1]}),
        "Transfers locked: Issuer"
    )
    issuer.setGlobalRestriction(True, {'from': a[0]})
    token.transfer(a[2], 1000, {'from': a[1]})

def global_lock_issuer():
    '''global lock - issuer / investor'''
    issuer.setGlobalRestriction(False, {'from': a[0]})
    token.transfer(a[1], 1000, {'from': a[0]})
    check.reverts(
        token.transfer,
        (a[0], 1000, {'from': a[1]}),
        "Transfers locked: Issuer"
    )
    issuer.setGlobalRestriction(True, {'from': a[0]})
    token.transfer(a[0], 1000, {'from': a[1]})

def token_lock():
    '''token lock - investor / investor'''
    token.transfer(a[1], 1000, {'from': a[0]})
    issuer.setTokenRestriction(token, False, {'from': a[0]})
    check.reverts(
        token.transfer,
        (a[2], 1000, {'from': a[1]}),
        "Transfers locked: Token"
    )
    issuer.setTokenRestriction(token, True, {'from': a[0]})
    token.transfer(a[2], 1000, {'from': a[1]})

def token_lock_issuer():
    '''token lock - issuer / investor'''
    issuer.setTokenRestriction(token, False, {'from': a[0]})
    token.transfer(a[1], 1000, {'from': a[0]})
    check.reverts(
        token.transfer,
        (a[0], 1000, {'from': a[1]}),
        "Transfers locked: Token"
    )
    issuer.setTokenRestriction(token, True, {'from': a[0]})
    token.transfer(a[0], 1000, {'from': a[1]})

def sender_restricted():
    '''sender restricted - investor / investor'''
    id_ = kyc.getID(a[1])
    token.transfer(a[1], 1000, {'from': a[0]})
    issuer.setInvestorRestriction(id_, False, {'from': a[0]})
    check.reverts(
        token.transfer,
        (a[2], 1000, {'from': a[1]}),
        "Sender restricted: Issuer"
    )
    issuer.setInvestorRestriction(id_, True, {'from': a[0]})
    token.transfer(a[2], 1000, {'from': a[1]})

def sender_restricted_issuer():
    '''sender restricted - issuer / investor'''
    check.reverts(
        issuer.setInvestorRestriction,
        (issuer.ownerID(), False, {'from': a[0]})
    )
    issuer.addAuthorityAddresses(issuer.ownerID(), [a[-1]], {'from':a[0]})
    token.transfer(a[1], 1000, {'from': a[-1]})
    issuer.removeAuthorityAddresses(issuer.ownerID(), [a[-1]], {'from':a[0]})
    check.reverts(
        token.transfer,
        (a[1], 1000, {'from': a[-1]}),
        "Restricted Authority Address"
    )
    issuer.addAuthorityAddresses(issuer.ownerID(), [a[-1]], {'from':a[0]})
    token.transfer(a[1], 1000, {'from': a[-1]})

def sender_restricted_kyc_id():
    '''sender ID restricted at kyc'''
    token.transfer(a[1], 1000, {'from': a[0]})
    kyc.setInvestorRestriction(kyc.getID(a[1]), False, {'from':a[0]})
    check.reverts(
        token.transfer,
        (a[2], 1000, {'from': a[1]}),
        "Sender restricted: Registrar"
    )

def sender_restricted_kyc_addr():
    '''sender address restricted at kyc'''
    token.transfer(a[1], 1000, {'from': a[0]})
    kyc.restrictAddresses(kyc.getID(a[1]), [a[1]], {'from':a[0]})
    check.reverts(
        token.transfer,
        (a[2], 1000, {'from': a[1]}),
        "Sender restricted: Registrar"
    )

def receiver_restricted_issuer():
    '''receiver restricted'''
    issuer.setInvestorRestriction(issuer.getID(a[1]), False, {'from': a[0]})
    check.reverts(
        token.transfer,
        (a[1], 1000, {'from': a[0]}),
        "Receiver restricted: Issuer"
    )

def receiver_restricted_kyc_id():
    '''receiver ID restricted at kyc'''
    kyc.setInvestorRestriction(kyc.getID(a[1]), False, {'from':a[0]})
    check.reverts(
        token.transfer,
        (a[1], 1000, {'from': a[0]}),
        "Receiver restricted: Registrar"
    )

def receiver_restricted_kyc_addr():
    '''receiver address restricted at kyc'''
    kyc.restrictAddresses(kyc.getID(a[1]), [a[1]], {'from':a[0]})
    check.reverts(
        token.transfer,
        (a[1], 1000, {'from': a[0]}),
        "Receiver restricted: Registrar"
    )

def receiver_blocked_country():
    '''receiver blocked - country'''
    issuer.setCountry(1, False, 0, [0]*8, {'from':a[0]})
    check.reverts(
        token.transfer,
        (a[1], 1000, {'from': a[0]}),
        "Receiver blocked: Country"
    )

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

def country_investor_limit_blocked_issuer_investor():
    '''country investor limit - blocked, issuer to investor'''
    issuer.setCountry(1, True, 1, [1,0,0,0,0,0,0,0], {'from': a[0]})
    token.transfer(a[1], 1000, {'from': a[0]})
    check.reverts(
        token.transfer,
        (a[2], 1000, {'from': a[0]}),
        "Country Investor Limit"
    )

def country_investor_limit_blocked_investor_investor():
    '''country investor limit - blocked, investor to investor'''
    issuer.setCountry(1, True, 1, [1,0,0,0,0,0,0,0], {'from': a[0]})
    token.transfer(a[1], 1000, {'from': a[0]})
    check.reverts(
        token.transfer,
        (a[2], 500, {'from': a[1]}),
        "Country Investor Limit"
    )

def country_investor_limit_issuer_investor():
    '''country investor limit - issuer to existing investor'''
    issuer.setCountry(1, True, 1, [1,0,0,0,0,0,0,0], {'from': a[0]})
    token.transfer(a[1], 1000, {'from': a[0]})
    token.transfer(a[1], 1000, {'from': a[0]})

def country_investor_limit_investor_investor():
    '''country investor limit - investor to investor, full balance'''
    issuer.setCountry(1, True, 1, [1,0,0,0,0,0,0,0], {'from': a[0]})
    token.transfer(a[1], 1000, {'from': a[0]})
    token.transfer(a[2], 1000, {'from': a[1]})

def country_investor_limit_investor_investor_different_country():
    '''country investor limit, investor to investor, different country'''
    issuer.setCountry(1, True, 1, [1,0,0,0,0,0,0,0], {'from': a[0]})
    token.transfer(a[1], 1000, {'from': a[0]})
    token.transfer(a[3], 500, {'from': a[1]})