#!/usr/bin/python3

from brownie import *
from scripts.deployment import main


def setup():
    config['test']['always_transact'] = False
    global kyc, issuer, auth_id
    kyc = a[0].deploy(KYCRegistrar, [a[0]], 1)
    issuer = a[0].deploy(IssuingEntity, [a[0]], 1)
    #token = accounts[0].deploy(token_contract, issuer, "Test NFT", "NFT", 1000000)
    #issuer.addToken(token, {'from': accounts[0]})
    issuer.setRegistrar(kyc, True, {'from': a[0]})
    kyc.addAuthority((a[-1],a[-2]), (1,2,3), 1, {'from': a[0]})
    auth_id = kyc.getAuthorityID(a[-1])


def add_threshold_zero():
    '''add - zero threshold'''
    check.reverts(
        kyc.addAuthority,
        ((a[1],), (1,2,3), 0, {'from': a[0]}),
        "dev: zero threshold"
    )

def add_exists_as_investor():
    '''add - ID already assigned to investor'''
    tx = kyc.addAuthority((a[1],), (1,2,3), 1, {'from': a[0]})
    id_ = kyc.getAuthorityID(a[1])
    rpc.revert()
    kyc.addInvestor(id_, 1, 1, 1, 9999999999, (a[1], a[2]), {'from': a[0]})
    check.reverts(
        kyc.addAuthority,
        ((a[1],), (1,2,3), 1, {'from': a[0]}),
        "dev: investor ID"
    )

def authority_exists():
    '''add - authority already exists'''
    kyc.addAuthority((a[1],), (1,2,3), 1, {'from': a[0]})
    check.reverts(
        kyc.addAuthority,
        ((a[1],), (1,2,3), 1, {'from': a[0]}),
        "dev: authority exists"
    )

def add_threshold_high():
    '''add - threshold exceed address count'''
    check.reverts(
        kyc.addAuthority,
        ((a[1],), (1,2,3), 2, {'from': a[0]}),
        "dev: threshold too high"
    )

def add_repeat_address():
    '''add - repeat address'''
    check.reverts(
        kyc.addAuthority,
        ((a[1],a[1]), (1,2,3), 2, {'from': a[0]}),
        "dev: known address"
    )

def threshold_zero():
    '''set threshold - zero'''
    check.reverts(
        kyc.setAuthorityThreshold,
        (auth_id, 0, {'from': a[0]}),
        "dev: zero threshold"
    )

def threshold_not_auth():
    '''set threshold - not an authority'''
    check.reverts(
        kyc.setAuthorityThreshold,
        ("0x1234", 1, {'from': a[0]}),
        "dev: not authority"
    )

def threshold_too_high():
    '''set threshold - too high'''
    check.reverts(
        kyc.setAuthorityThreshold,
        (auth_id, 3, {'from': a[0]}),
        "dev: threshold too high"
    )