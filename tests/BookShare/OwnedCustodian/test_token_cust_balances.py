#!/usr/bin/python3

import functools
import pytest

from brownie import accounts


@pytest.fixture(scope="module", autouse=True)
def setup(approve_many, org, share):
    share.mint(org, 100000, {"from": accounts[0]})


@pytest.fixture(scope="module")
def balance(share, cust):
    yield functools.partial(_check_balance, share, cust)


def _check_balance(share, cust, account, bal, custbal):
    assert share.balanceOf(account) == bal
    assert share.custodianBalanceOf(account, cust) == custbal


def test_into_custodian(balance, share, cust):
    """Transfer into custodian - member"""
    share.transfer(accounts[1], 10000, {"from": accounts[0]})
    share.transfer(accounts[2], 10000, {"from": accounts[0]})
    share.transfer(cust, 4000, {"from": accounts[1]})
    share.transfer(cust, 10000, {"from": accounts[2]})
    balance(accounts[1], 6000, 4000)
    balance(accounts[2], 0, 10000)
    assert share.balanceOf(cust) == 14000


def test_cust_internal(balance, share, cust):
    """Custodian transfer internal - member to member"""
    share.transfer(accounts[2], 10000, {"from": accounts[0]})
    share.transfer(cust, 5000, {"from": accounts[2]})
    cust.transferInternal(share, accounts[2], accounts[3], 5000, {"from": accounts[0]})
    balance(accounts[2], 5000, 0)
    balance(accounts[3], 0, 5000)
    assert share.balanceOf(cust) == 5000


def test_cust_out(balance, share, cust):
    """Transfer out of custodian - member"""
    share.transfer(accounts[1], 10000, {"from": accounts[0]})
    share.transfer(cust, 10000, {"from": accounts[1]})
    cust.transferInternal(share, accounts[1], accounts[2], 10000, {"from": accounts[0]})
    cust.transfer(share, accounts[2], 10000, {"from": accounts[0]})
    balance(accounts[1], 0, 0)
    balance(accounts[2], 10000, 0)
    assert share.balanceOf(cust) == 0


def test_org_cust_in(balance, org, share, cust):
    """Transfers into custodian - org"""
    share.transfer(cust, 10000, {"from": accounts[0]})
    balance(accounts[0], 0, 0)
    balance(org, 90000, 10000)
    assert share.balanceOf(cust) == 10000
    share.transfer(cust, 90000, {"from": accounts[0]})
    balance(accounts[0], 0, 0)
    balance(org, 0, 100000)
    assert share.balanceOf(cust) == 100000


def test_org_cust_internal(balance, org, share, cust):
    """Custodian internal transfers - org / member"""
    share.transfer(cust, 10000, {"from": accounts[0]})
    cust.transferInternal(share, org, accounts[1], 10000, {"from": accounts[0]})
    balance(accounts[0], 0, 0)
    balance(org, 90000, 0)
    balance(accounts[1], 0, 10000)
    assert share.balanceOf(cust) == 10000
    cust.transferInternal(share, accounts[1], org, 5000, {"from": accounts[0]})
    balance(accounts[0], 0, 0)
    balance(org, 90000, 5000)
    balance(accounts[1], 0, 5000)
    assert share.balanceOf(cust) == 10000
    cust.transferInternal(share, accounts[1], accounts[0], 5000, {"from": accounts[0]})
    balance(accounts[0], 0, 0)
    balance(org, 90000, 10000)
    balance(accounts[1], 0, 0)
    assert share.balanceOf(cust) == 10000


def test_org_cust_out(balance, org, share, cust):
    """Transfers out of custodian - org"""
    share.transfer(cust, 10000, {"from": accounts[0]})
    balance(accounts[0], 0, 0)
    balance(org, 90000, 10000)
    assert share.balanceOf(cust) == 10000
    cust.transfer(share, org, 3000, {"from": accounts[0]})
    balance(accounts[0], 0, 0)
    balance(org, 93000, 7000)
    assert share.balanceOf(cust) == 7000
    cust.transfer(share, accounts[0], 7000, {"from": accounts[0]})
    balance(accounts[0], 0, 0)
    balance(org, 100000, 0)
    assert share.balanceOf(cust) == 0
