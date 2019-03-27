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