#!/usr/bin/python3

import pytest

from brownie import accounts


@pytest.fixture(scope="module", autouse=True)
def setup(approve_many, org, share):
    share.mint(org, 100000, {"from": accounts[0]})


def test_zero_shares(share):
    """cannot send 0 shares"""
    with pytest.reverts("Cannot send 0 shares"):
        share.transfer(accounts[1], 0, {"from": accounts[0]})


def test_insufficient_balance_member(share):
    """insufficient balance - member to member"""
    share.transfer(accounts[1], 1000, {"from": accounts[0]})
    with pytest.reverts("Insufficient Balance"):
        share.transfer(accounts[2], 2000, {"from": accounts[1]})


def test_insufficient_balance_org(share):
    """insufficient balance - org to member"""
    with pytest.reverts("Insufficient Balance"):
        share.transfer(accounts[1], 20000000000, {"from": accounts[0]})


def test_balance(share):
    """successful transfer"""
    share.transfer(accounts[1], 1000, {"from": accounts[0]})
    assert share.balanceOf(accounts[1]) == 1000
    share.transfer(accounts[2], 400, {"from": accounts[1]})
    assert share.balanceOf(accounts[1]) == 600
    assert share.balanceOf(accounts[2]) == 400


def test_balance_org(org, share):
    """org balances"""
    assert share.balanceOf(accounts[0]) == 0
    assert share.balanceOf(org) == 100000
    share.transfer(accounts[1], 1000, {"from": accounts[0]})
    assert share.balanceOf(accounts[0]) == 0
    assert share.balanceOf(org) == 99000
    share.transfer(accounts[0], 1000, {"from": accounts[1]})
    assert share.balanceOf(accounts[0]) == 0
    assert share.balanceOf(org) == 100000
    share.transfer(accounts[1], 1000, {"from": accounts[0]})
    share.transfer(org, 1000, {"from": accounts[1]})
    assert share.balanceOf(accounts[0]) == 0
    assert share.balanceOf(org) == 100000


def test_authority_permission(org, share):
    """org subauthority balances"""
    org.addAuthority(
        [accounts[-1]], ["0xa9059cbb"], 2000000000, 1, {"from": accounts[0]}
    )
    share.transfer(accounts[1], 1000, {"from": accounts[-1]})
    assert share.balanceOf(accounts[0]) == 0
    assert share.balanceOf(accounts[-1]) == 0
    assert share.balanceOf(org) == 99000
    share.transfer(accounts[-1], 1000, {"from": accounts[1]})
    assert share.balanceOf(accounts[0]) == 0
    assert share.balanceOf(accounts[-1]) == 0
    assert share.balanceOf(org) == 100000
