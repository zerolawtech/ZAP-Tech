#!/usr/bin/python3

import pytest

from brownie import accounts


@pytest.fixture(scope="module", autouse=True)
def setup(id1, id2, org, token):
    token.mint(org, 100000, {'from': accounts[0]})


def test_global_lock(org, token):
    '''global lock - investor / investor'''
    token.transfer(accounts[1], 1000, {'from': accounts[0]})
    org.setGlobalRestriction(True, {'from': accounts[0]})
    with pytest.reverts("Transfers locked: Issuer"):
        token.transfer(accounts[2], 1000, {'from': accounts[1]})
    org.setGlobalRestriction(False, {'from': accounts[0]})
    token.transfer(accounts[2], 1000, {'from': accounts[1]})


def test_global_lock_org(org, token):
    '''global lock - org / investor'''
    org.setGlobalRestriction(True, {'from': accounts[0]})
    token.transfer(accounts[1], 1000, {'from': accounts[0]})
    with pytest.reverts("Transfers locked: Issuer"):
        token.transfer(accounts[0], 1000, {'from': accounts[1]})
    org.setGlobalRestriction(False, {'from': accounts[0]})
    token.transfer(accounts[0], 1000, {'from': accounts[1]})


def test_token_lock(org, token):
    '''token lock - investor / investor'''
    token.transfer(accounts[1], 1000, {'from': accounts[0]})
    org.setTokenRestriction(token, True, {'from': accounts[0]})
    with pytest.reverts("Transfers locked: Token"):
        token.transfer(accounts[2], 1000, {'from': accounts[1]})
    org.setTokenRestriction(token, False, {'from': accounts[0]})
    token.transfer(accounts[2], 1000, {'from': accounts[1]})


def test_token_lock_org(org, token):
    '''token lock - org / investor'''
    org.setTokenRestriction(token, True, {'from': accounts[0]})
    token.transfer(accounts[1], 1000, {'from': accounts[0]})
    with pytest.reverts("Transfers locked: Token"):
        token.transfer(accounts[0], 1000, {'from': accounts[1]})
    org.setTokenRestriction(token, False, {'from': accounts[0]})
    token.transfer(accounts[0], 1000, {'from': accounts[1]})
