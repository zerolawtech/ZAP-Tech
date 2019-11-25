#!/usr/bin/python3

import pytest

from brownie import accounts


@pytest.fixture(scope="module", autouse=True)
def setup(approve_many, org, token):
    token.mint(org, 100000, {'from': accounts[0]})


def test_zero_tokens(token):
    '''cannot send 0 tokens'''
    with pytest.reverts("Cannot send 0 tokens"):
        token.transfer(accounts[1], 0, {'from': accounts[0]})


def test_insufficient_balance_investor(token):
    '''insufficient balance - investor to investor'''
    token.transfer(accounts[1], 1000, {'from': accounts[0]})
    with pytest.reverts("Insufficient Balance"):
        token.transfer(accounts[2], 2000, {'from': accounts[1]})


def test_insufficient_balance_org(token):
    '''insufficient balance - org to investor'''
    with pytest.reverts("Insufficient Balance"):
        token.transfer(accounts[1], 20000000000, {'from': accounts[0]})


def test_balance(token):
    '''successful transfer'''
    token.transfer(accounts[1], 1000, {'from': accounts[0]})
    assert token.balanceOf(accounts[1]) == 1000
    token.transfer(accounts[2], 400, {'from': accounts[1]})
    assert token.balanceOf(accounts[1]) == 600
    assert token.balanceOf(accounts[2]) == 400


def test_balance_org(org, token):
    '''org balances'''
    assert token.balanceOf(accounts[0]) == 0
    assert token.balanceOf(org) == 100000
    token.transfer(accounts[1], 1000, {'from': accounts[0]})
    assert token.balanceOf(accounts[0]) == 0
    assert token.balanceOf(org) == 99000
    token.transfer(accounts[0], 1000, {'from': accounts[1]})
    assert token.balanceOf(accounts[0]) == 0
    assert token.balanceOf(org) == 100000
    token.transfer(accounts[1], 1000, {'from': accounts[0]})
    token.transfer(org, 1000, {'from': accounts[1]})
    assert token.balanceOf(accounts[0]) == 0
    assert token.balanceOf(org) == 100000


def test_authority_permission(org, token):
    '''org subauthority balances'''
    org.addAuthority([accounts[-1]], ["0xa9059cbb"], 2000000000, 1, {'from': accounts[0]})
    token.transfer(accounts[1], 1000, {'from': accounts[-1]})
    assert token.balanceOf(accounts[0]) == 0
    assert token.balanceOf(accounts[-1]) == 0
    assert token.balanceOf(org) == 99000
    token.transfer(accounts[-1], 1000, {'from': accounts[1]})
    assert token.balanceOf(accounts[0]) == 0
    assert token.balanceOf(accounts[-1]) == 0
    assert token.balanceOf(org) == 100000
