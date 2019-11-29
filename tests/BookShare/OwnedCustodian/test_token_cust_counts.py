#!/usr/bin/python3

import pytest

from brownie import accounts


@pytest.fixture(scope="module", autouse=True)
def setup(approve_many, org, share):
    share.mint(org, 100000, {'from': accounts[0]})


def test_into_custodian(check_counts, share, cust):
    '''Transfer into custodian - member'''
    share.transfer(accounts[1], 10000, {'from': accounts[0]})
    share.transfer(accounts[2], 10000, {'from': accounts[0]})
    check_counts(one=(2, 1, 1))
    share.transfer(cust, 5000, {'from': accounts[1]})
    check_counts(one=(2, 1, 1))
    share.transfer(cust, 10000, {'from': accounts[2]})
    check_counts(one=(2, 1, 1))


def test_cust_internal(check_counts, share, cust):
    '''Custodian transfer internal - member to member'''
    share.transfer(accounts[2], 10000, {'from': accounts[0]})
    share.transfer(cust, 5000, {'from': accounts[2]})
    cust.transferInternal(share, accounts[2], accounts[3], 5000, {'from': accounts[0]})
    check_counts(one=(1, 0, 1), two=(1, 1, 0))
    share.transfer(accounts[3], 5000, {'from': accounts[0]})
    check_counts(one=(1, 0, 1), two=(1, 1, 0))


def test_cust_out(check_counts, org, share, cust):
    '''Transfer out of custodian - member'''
    share.transfer(accounts[1], 10000, {'from': accounts[0]})
    share.transfer(cust, 10000, {'from': accounts[1]})
    cust.transferInternal(share, accounts[1], accounts[2], 10000, {'from': accounts[0]})
    check_counts(one=(1, 0, 1))
    cust.transfer(share, accounts[2], 10000, {'from': accounts[0]})
    check_counts(one=(1, 0, 1))
    share.transfer(org, 10000, {'from': accounts[2]})
    check_counts()


def test_org_cust_in(check_counts, share, cust):
    '''Transfers into custodian - org'''
    share.transfer(cust, 10000, {'from': accounts[0]})
    check_counts()
    share.transfer(cust, 90000, {'from': accounts[0]})
    check_counts()


def test_org_cust_internal(check_counts, org, share, cust):
    '''Custodian internal transfers - org / member'''
    share.transfer(cust, 10000, {'from': accounts[0]})
    cust.transferInternal(share, org, accounts[1], 10000, {'from': accounts[0]})
    check_counts(one=(1, 1, 0))
    cust.transferInternal(share, accounts[1], org, 5000, {'from': accounts[0]})
    check_counts(one=(1, 1, 0))
    cust.transferInternal(share, accounts[1], accounts[0], 5000, {'from': accounts[0]})
    check_counts()


def test_org_cust_out(check_counts, org, share, cust):
    '''Transfers out of custodian - org'''
    share.transfer(cust, 10000, {'from': accounts[0]})
    check_counts()
    cust.transfer(share, org, 3000, {'from': accounts[0]})
    check_counts()
    cust.transfer(share, accounts[0], 7000, {'from': accounts[0]})
    check_counts()
