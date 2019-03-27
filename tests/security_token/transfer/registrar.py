#!/usr/bin/python3

from brownie import *
from scripts.deployment import main


def setup():
    main(SecurityToken)
    global token, issuer, kyc, kyc2
    token = SecurityToken[0]
    issuer = IssuingEntity[0]
    kyc = KYCRegistrar[0]
    kyc2 = a[0].deploy(KYCRegistrar, [a[0]], 1)
    kyc2.addInvestor("investor1", 1, 'aws', 1, 9999999999, [a[1]], {'from': a[0]})
    issuer.setRegistrar(kyc2, True, {'from': a[0]})
    token.mint(issuer, 1000000, {'from': a[0]})

def unknown_address():
    '''unknown address'''
    check.reverts(
        token.transfer,
        (a.add(), 1000, {'from': a[0]}),
        "Address not registered"
    )

def registrar_restricted():
    '''registrar restricted'''
    token.transfer(a[2], 1000, {'from': a[0]})
    issuer.setRegistrar(kyc, False, {'from': a[0]})
    check.reverts(
        token.transfer,
        (a[2], 1000, {'from': a[0]}),
        "Registrar restricted"
    )

def switch_registrars():
    '''switch between registrars'''
    id_ = issuer.getID(a[1])
    token.transfer(a[1], 1000, {'from': a[0]})
    check.true(issuer.getInvestorRegistrar(id_) == kyc)
    issuer.setRegistrar(kyc, False, {'from': a[0]})
    token.transfer(a[1], 1000, {'from': a[0]})
    check.true(issuer.getInvestorRegistrar(id_) == kyc2)
    issuer.setRegistrar(kyc, True, {'from': a[0]})
    token.transfer(a[1], 1000, {'from': a[0]})
    check.true(issuer.getInvestorRegistrar(id_) == kyc2)
    issuer.setRegistrar(kyc2, False, {'from': a[0]})
    token.transfer(a[1], 1000, {'from': a[0]})
    check.true(issuer.getInvestorRegistrar(id_) == kyc)