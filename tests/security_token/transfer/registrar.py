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

def unknown_address():
    '''unknown address'''
    check.reverts(
        token.transfer,
        (a[-1], 1000, {'from': a[0]}),
        "Address not registered"
    )

def registrar_restricted():
    '''registrar restricted'''
    token.transfer(a[1], 1000, {'from': a[0]})
    issuer.setRegistrar(kyc, False, {'from': a[0]})
    check.reverts(
        token.transfer,
        (a[1], 1000, {'from': a[0]}),
        "Registrar restricted"
    )

def new_registrar():
    '''registrar restricted, use new registrar'''
    token.transfer(a[1], 1000, {'from': a[0]})
    issuer.setRegistrar(kyc, False, {'from': a[0]})
    k = a[0].deploy(KYCRegistrar, [a[0]], 1)
    k.addInvestor("investor1", 1, 'aws', 1, 9999999999, [a[1]], {'from': a[0]})
    issuer.setRegistrar(k, True, {'from': a[0]})
    token.transfer(a[1], 1000, {'from': a[0]})

# todo multiple registrars, restrict and then lift