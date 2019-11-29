#!/usr/bin/python3

import pytest

from brownie import accounts


@pytest.fixture(scope="module", autouse=True)
def setup(id1, id2, org, share):
    share.mint(org, 100000, {'from': accounts[0]})


def test_org_txfrom(share, cust):
    '''Org transferFrom custodian'''
    share.transfer(accounts[1], 10000, {'from': accounts[0]})
    share.transfer(cust, 10000, {'from': accounts[1]})
    share.transferFrom(cust, accounts[1], 5000, {'from': accounts[0]})
    assert share.balanceOf(accounts[1]) == 5000
    assert share.balanceOf(cust) == 5000
    assert share.custodianBalanceOf(accounts[1], cust) == 5000


def test_member_txfrom(share, cust):
    '''Member transferFrom custodian'''
    share.transfer(accounts[1], 10000, {'from': accounts[0]})
    share.transfer(cust, 10000, {'from': accounts[1]})
    with pytest.reverts("Insufficient allowance"):
        share.transferFrom(cust, accounts[1], 5000, {'from': accounts[1]})
    with pytest.reverts("Insufficient allowance"):
        share.transferFrom(cust, accounts[1], 5000, {'from': accounts[2]})
