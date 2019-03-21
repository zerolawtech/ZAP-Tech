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


def into_custodian():
    '''Send into custodian'''
    token.transfer(a[1], 10000)
    check.equal(issuer.getInvestorCounts()[0][0:3], (1, 1, 0))
    token.transfer(a[2], 10000)
    check.equal(issuer.getInvestorCounts()[0][0:3], (2, 1, 1))
    token.transfer(cust, 5000, {'from': a[1]})
    check.equal(issuer.getInvestorCounts()[0][0:3], (2, 1, 1))
    token.transfer(cust, 10000, {'from': a[2]})
    check.equal(issuer.getInvestorCounts()[0][0:3], (2, 1, 1))


def cust_internal():
    '''Custodian transfer internal'''
    token.transfer(a[2], 10000)
    token.transfer(cust, 5000, {'from': a[2]})
    cust.transferInternal(token, a[2], a[3], 5000)
    check.equal(issuer.getInvestorCounts()[0][0:3], (2, 1, 1))
    token.transfer(a[3], 5000)
    check.equal(issuer.getInvestorCounts()[0][0:3], (2, 1, 1))


def cust_out():
    '''Transfer out of custodian'''
    token.transfer(a[1], 10000)
    token.transfer(cust, 10000, {'from': a[1]})
    cust.transferInternal(token, a[1], a[2], 10000)
    check.equal(issuer.getInvestorCounts()[0][0:3], (1, 0, 1))
    cust.transfer(token, a[2], 10000)
    check.equal(issuer.getInvestorCounts()[0][0:3], (1, 0, 1))
    token.transfer(issuer, 10000, {'from': a[2]})
    check.equal(issuer.getInvestorCounts()[0][0:3], (0, 0, 0))


def issuer_cust():
    '''Transfers between issuer and custodian'''
    token.transfer(cust, 10000)
    check.equal(issuer.getInvestorCounts()[0][0:3], (0, 0, 0))
    cust.transferInternal(token, issuer, a[1], 10000)
    check.equal(issuer.getInvestorCounts()[0][0:3], (1, 1, 0))
    cust.transferInternal(token, a[1], issuer, 5000)
    check.equal(issuer.getInvestorCounts()[0][0:3], (1, 1, 0))
    cust.transferInternal(token, a[1], issuer, 5000)
    check.equal(issuer.getInvestorCounts()[0][0:3], (0, 0, 0))
    cust.transfer(token, issuer, 10000)
    check.equal(issuer.getInvestorCounts()[0][0:3], (0, 0, 0))