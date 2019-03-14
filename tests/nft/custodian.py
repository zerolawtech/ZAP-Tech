#!/usr/bin/python3

from brownie import *
from scripts.deployment import main


# THIS IS NOWHERE NEAR COMPLETE
def setup():
    config['test']['always_transact'] = False
    config['test']['default_contract_owner'] = True
    main(NFToken)
    global token, issuer, cust
    token = NFToken[0]
    issuer = IssuingEntity[0]
    token.mint(issuer, 1000000, 0, "0x00", {'from': accounts[0]})
    cust = OwnedCustodian.deploy(a[0], [a[0]], 1)
    issuer.addCustodian(cust)


def to_and_from_issuer():
    '''Send from and to issuer'''
    token.transfer(a[2], 10000)
    token.transfer(a[0], 10000, {'from': a[2]})
    check.equal(issuer.getInvestorCounts()[0][0:3], (0, 0, 0))


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
    token.transfer(a[1], 10000)
    token.transfer(cust, 5000, {'from': a[1]})
    check.equal(token.custodianBalanceOf(a[1], cust), 5000)
    cust.transferInternal(token, a[1], a[2], 5000)
    check.equal(token.custodianBalanceOf(a[1], cust), 0)
    check.equal(token.custodianBalanceOf(a[2], cust), 5000)
    check.equal(issuer.getInvestorCounts()[0][0:3], (2, 1, 1))
    token.transfer(a[2], 5000)
    check.equal(issuer.getInvestorCounts()[0][0:3], (2, 1, 1))


def cust_out():
    '''Transfer out of custodian'''
    token.transfer(a[1], 10000)
    token.transfer(cust, 10000, {'from': a[1]})
    check.equal(token.rangesOf(a[1]), ((1, 10001),))
    check.equal(token.custodianBalanceOf(a[1], cust), 10000)
    check.equal(token.balanceOf(a[1]), 0)
    cust.transferInternal(token, a[1], a[2], 10000)
    check.equal(issuer.getInvestorCounts()[0][0:3], (1, 0, 1))
    check.equal(token.balanceOf(a[2]), 0)
    check.equal(token.custodianBalanceOf(a[1], cust), 0)
    check.equal(token.custodianBalanceOf(a[2], cust), 10000)
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


def issuer_txfrom():
    '''Issuer transferFrom custodian'''
    token.transfer(a[2], 10000)
    token.transfer(cust, 10000, {'from': a[2]})
    token.transferFrom(cust, a[2], 5000, {'from': a[0]})
    check.equal(token.balanceOf(a[2]), 5000)
    check.equal(token.balanceOf(cust), 5000)
    check.equal(token.custodianBalanceOf(a[2], cust), 5000)
