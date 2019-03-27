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
        [1, 2, 3, 4, 5],
        [1, 1, 1, 2, 2],
        [1, 2, 2, 3, 3],
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