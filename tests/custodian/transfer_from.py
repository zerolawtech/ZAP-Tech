#!/usr/bin/python3

from brownie import *
from scripts.deployment import main


def setup():
    config['test']['always_transact'] = False
    config['test']['default_contract_owner'] = True
    main(SecurityToken)
    global token, issuer, cust
    token = SecurityToken[0]
    issuer = IssuingEntity[0]
    cust = OwnedCustodian.deploy(a[0], [a[0]], 1)
    issuer.addCustodian(cust)
    token.mint(issuer, 100000)


def issuer_txfrom():
    '''Issuer transferFrom custodian'''
    token.transfer(a[1], 10000)
    token.transfer(cust, 10000, {'from': a[1]})
    token.transferFrom(cust, a[1], 5000, {'from': a[0]})
    check.equal(token.balanceOf(a[1]), 5000)
    check.equal(token.balanceOf(cust), 5000)
    check.equal(token.custodianBalanceOf(a[1], cust), 5000)
