#!/usr/bin/python3

import pytest

from brownie import accounts


@pytest.fixture(scope="module", autouse=True)
def setup(approve_many, org, token):
    token.mint(org, 100000, {'from': accounts[0]})


def test_into_custodian(check_counts, token, cust):
    '''Transfer into custodian - investor'''
    token.transfer(accounts[1], 10000, {'from': accounts[0]})
    token.transfer(accounts[2], 10000, {'from': accounts[0]})
    check_counts(one=(2, 1, 1))
    token.transfer(cust, 5000, {'from': accounts[1]})
    check_counts(one=(2, 1, 1))
    token.transfer(cust, 10000, {'from': accounts[2]})
    check_counts(one=(2, 1, 1))


def test_cust_internal(check_counts, token, cust):
    '''Custodian transfer internal - investor to investor'''
    token.transfer(accounts[2], 10000, {'from': accounts[0]})
    token.transfer(cust, 5000, {'from': accounts[2]})
    cust.transferInternal(token, accounts[2], accounts[3], 5000, {'from': accounts[0]})
    check_counts(one=(1, 0, 1), two=(1, 1, 0))
    token.transfer(accounts[3], 5000, {'from': accounts[0]})
    check_counts(one=(1, 0, 1), two=(1, 1, 0))


def test_cust_out(check_counts, org, token, cust):
    '''Transfer out of custodian - investor'''
    token.transfer(accounts[1], 10000, {'from': accounts[0]})
    token.transfer(cust, 10000, {'from': accounts[1]})
    cust.transferInternal(token, accounts[1], accounts[2], 10000, {'from': accounts[0]})
    check_counts(one=(1, 0, 1))
    cust.transfer(token, accounts[2], 10000, {'from': accounts[0]})
    check_counts(one=(1, 0, 1))
    token.transfer(org, 10000, {'from': accounts[2]})
    check_counts()


def test_org_cust_in(check_counts, token, cust):
    '''Transfers into custodian - org'''
    token.transfer(cust, 10000, {'from': accounts[0]})
    check_counts()
    token.transfer(cust, 90000, {'from': accounts[0]})
    check_counts()


def test_org_cust_internal(check_counts, org, token, cust):
    '''Custodian internal transfers - org / investor'''
    token.transfer(cust, 10000, {'from': accounts[0]})
    cust.transferInternal(token, org, accounts[1], 10000, {'from': accounts[0]})
    check_counts(one=(1, 1, 0))
    cust.transferInternal(token, accounts[1], org, 5000, {'from': accounts[0]})
    check_counts(one=(1, 1, 0))
    cust.transferInternal(token, accounts[1], accounts[0], 5000, {'from': accounts[0]})
    check_counts()


def test_org_cust_out(check_counts, org, token, cust):
    '''Transfers out of custodian - org'''
    token.transfer(cust, 10000, {'from': accounts[0]})
    check_counts()
    cust.transfer(token, org, 3000, {'from': accounts[0]})
    check_counts()
    cust.transfer(token, accounts[0], 7000, {'from': accounts[0]})
    check_counts()
