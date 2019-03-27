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

def zero_tokens():
    '''cannot send 0 tokens'''
    check.reverts(
        token.transfer,
        (a[1], 0, {'from':a[0]}),
        "Cannot send 0 tokens"
    )

def insufficient_balance_investor():
    '''insufficient balance - investor to investor'''
    token.transfer(a[1], 1000, {'from':a[0]})
    check.reverts(
        token.transfer,
        (a[2], 2000, {'from':a[1]}),
        "Insufficient Balance"
    )

def insufficient_balance_issuer():
    '''insufficient balance - issuer to investor'''
    check.reverts(
        token.transfer,
        (a[1], 20000000000, {'from':a[0]}),
        "Insufficient Balance"
    )
