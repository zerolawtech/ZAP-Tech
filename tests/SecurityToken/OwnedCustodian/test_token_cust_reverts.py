#!/usr/bin/python3

import pytest

from brownie import accounts


@pytest.fixture(scope="module", autouse=True)
def setup(id1, id2, org, token):
    token.mint(org, 100000, {'from': accounts[0]})


def test_zero(token, cust):
    '''Custodian transfer internal - zero value'''
    token.transfer(accounts[1], 10000, {'from': accounts[0]})
    token.transfer(cust, 5000, {'from': accounts[1]})
    with pytest.reverts("Cannot send 0 tokens"):
        cust.transferInternal(token, accounts[1], accounts[2], 0, {'from': accounts[0]})


def test_exceed(token, cust):
    '''Custodian transfer internal - exceed balance'''
    token.transfer(accounts[1], 10000, {'from': accounts[0]})
    token.transfer(cust, 5000, {'from': accounts[1]})
    with pytest.reverts("Insufficient Custodial Balance"):
        cust.transferInternal(token, accounts[1], accounts[2], 6000, {'from': accounts[0]})


def test_cust_to_cust(OwnedCustodian, org, token, cust):
    '''custodian to custodian'''
    cust2 = accounts[0].deploy(OwnedCustodian, [accounts[0]], 1)
    org.addCustodian(cust2, {'from': accounts[0]})
    token.transfer(accounts[1], 10000, {'from': accounts[0]})
    token.transfer(cust, 5000, {'from': accounts[1]})
    with pytest.reverts("Custodian to Custodian"):
        cust.transferInternal(token, accounts[1], cust2, 500, {'from': accounts[0]})


def test_mint(token, cust):
    '''mint to custodian'''
    with pytest.reverts():
        token.mint(cust, 1000, {'from': accounts[0]})
