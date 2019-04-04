#!/usr/bin/python3

from brownie import *
from scripts.deployment import main


def setup():
    config['test']['always_transact'] = False
    main(NFToken)
    global token, issuer
    token = NFToken[0]
    issuer = IssuingEntity[0]

def mint_zero():
    '''mint 0 tokens'''
    check.reverts(
        token.mint,
        (issuer, 0, 0, "0x00", {'from': a[0]}),
        "dev: mint 0"
    )
    token.mint(issuer, 10000, 0, "0x00", {'from': a[0]})
    check.reverts(
        token.mint,
        (issuer, 0, 0, "0x00", {'from': a[0]}),
        "dev: mint 0"
    )

def burn_zero():
    '''burn 0 tokens'''
    check.reverts(
        token.burn,
        (1, 1, {'from': a[0]}),
        "dev: burn 0"
    )
    token.mint(issuer, 10000, 0, "0x00", {'from': a[0]})
    check.reverts(
        token.burn,
        (1, 1, {'from': a[0]}),
        "dev: burn 0"
    )

def authorized_below_total():
    '''authorized supply below total supply'''
    token.mint(issuer, 100000, "0x00", 0, {'from': a[0]})
    check.reverts(
        token.modifyAuthorizedSupply,
        (10000, {'from': a[0]}),
        "dev: auth below total"
    )

def total_above_authorized():
    '''total supply above authorized'''
    token.modifyAuthorizedSupply(10000, {'from': a[0]})
    check.reverts(
        token.mint,
        (issuer, 20000, 0, "0x00", {'from': a[0]}),
        "dev: exceed auth"
    )
    token.mint(issuer, 6000, 0, "0x00", {'from': a[0]})
    check.reverts(
        token.mint,
        (issuer, 6000, 0, "0x00", {'from': a[0]}),
        "dev: exceed auth"
    )
    token.mint(issuer, 4000, 0, "0x00", {'from': a[0]})
    check.reverts(
        token.mint,
        (issuer, 1, 0, "0x00", {'from': a[0]}),
        "dev: exceed auth"
    )
    check.reverts(
        token.mint,
        (issuer, 0, 0, "0x00", {'from': a[0]}),
        "dev: mint 0"
    )

def burn_exceeds_balance():
    '''burn exceeds balance'''
    check.reverts(
        token.burn,
        (1, 101, {'from': a[0]}),
        "dev: exceeds upper bound"
    )
    token.mint(issuer, 4000, 0, "0x00", {'from': a[0]})
    check.reverts(
        token.burn,
        (1, 5001, {'from': a[0]}),
        "dev: exceeds upper bound"
    )
    token.burn(1, 3001, {'from': a[0]})
    check.reverts(
        token.burn,
        (3001, 4002, {'from': a[0]}),
        "dev: exceeds upper bound"
    )
    token.burn(3001, 4001, {'from': a[0]})
    check.reverts(
        token.burn,
        (4001, 4101, {'from': a[0]}),
        "dev: exceeds upper bound"
    )
    