#!/usr/bin/python3

import pytest

from brownie import accounts


def test_mint_zero(org, token):
    '''mint 0 tokens'''
    with pytest.reverts("dev: mint 0"):
        token.mint(org, 0, {'from': accounts[0]})
    token.mint(org, 10000, {'from': accounts[0]})
    with pytest.reverts("dev: mint 0"):
        token.mint(org, 0, {'from': accounts[0]})


def test_burn_zero(org, token):
    '''burn 0 tokens'''
    with pytest.reverts("dev: burn 0"):
        token.burn(org, 0, {'from': accounts[0]})
    token.mint(org, 10000, {'from': accounts[0]})
    with pytest.reverts("dev: burn 0"):
        token.burn(org, 0, {'from': accounts[0]})


def test_authorized_below_total(org, token):
    '''authorized supply below total supply'''
    token.mint(org, 100000, {'from': accounts[0]})
    with pytest.reverts("dev: auth below total"):
        token.modifyAuthorizedSupply(10000, {'from': accounts[0]})


def test_total_above_authorized(org, token):
    '''total supply above authorized'''
    token.modifyAuthorizedSupply(10000, {'from': accounts[0]})
    with pytest.reverts("dev: exceed auth"):
        token.mint(org, 20000, {'from': accounts[0]})
    token.mint(org, 6000, {'from': accounts[0]})
    with pytest.reverts("dev: exceed auth"):
        token.mint(org, 6000, {'from': accounts[0]})
    token.mint(org, 4000, {'from': accounts[0]})
    with pytest.reverts("dev: exceed auth"):
        token.mint(org, 1, {'from': accounts[0]})
    with pytest.reverts("dev: mint 0"):
        token.mint(org, 0, {'from': accounts[0]})


def test_burn_exceeds_balance(org, token):
    '''burn exceeds balance'''
    with pytest.reverts():
        token.burn(org, 100, {'from': accounts[0]})
    token.mint(org, 4000, {'from': accounts[0]})
    with pytest.reverts():
        token.burn(org, 5000, {'from': accounts[0]})
    token.burn(org, 3000, {'from': accounts[0]})
    with pytest.reverts():
        token.burn(org, 1001, {'from': accounts[0]})
    token.burn(org, 1000, {'from': accounts[0]})
    with pytest.reverts():
        token.burn(org, 100, {'from': accounts[0]})


def test_mint_to_custodian(org, token, cust):
    '''mint to custodian'''
    with pytest.reverts("dev: custodian"):
        token.mint(cust, 6000, {'from': accounts[0]})


def test_burn_from_custodian(org, token, cust):
    '''burn from custodian'''
    token.mint(org, 10000, {'from': accounts[0]})
    token.transfer(cust, 10000, {'from': accounts[0]})
    with pytest.reverts("dev: custodian"):
        token.burn(cust, 5000, {'from': accounts[0]})


def test_global_lock(org, token, id1):
    '''mint - token lock'''
    org.setTokenRestriction(token, True, {'from': accounts[0]})
    with pytest.reverts("dev: token locked"):
        token.mint(accounts[1], 1, {'from': accounts[0]})
