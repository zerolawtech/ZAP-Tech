#!/usr/bin/python3

import pytest

from brownie import accounts


@pytest.fixture(scope="module", autouse=True)
def setup(approve_many, org, token, cust):
    token.mint(org, 100000, {'from': accounts[0]})
    token.transfer(accounts[2], 1000, {'from': accounts[0]})
    token.transfer(cust, 500, {'from': accounts[0]})
    token.transfer(cust, 500, {'from': accounts[2]})
    org.setEntityRestriction(cust.ownerID(), True, {'from': accounts[0]})


def test_from_org(token, cust):
    '''restricted custodian - org to custodian'''
    with pytest.reverts("Receiver restricted: Issuer"):
        token.transfer(cust, 1000, {'from': accounts[0]})


def test_from_investor(token, cust):
    '''restricted custodian - investor to custodian'''
    with pytest.reverts("Receiver restricted: Issuer"):
        token.transfer(cust, 1000, {'from': accounts[2]})


def test_transferInternal(token, cust):
    '''restricted custodian - internal transfer'''
    with pytest.reverts("Authority restricted"):
        cust.transferInternal(token, accounts[2], accounts[3], 500, {'from': accounts[0]})


def test_to_org(token, cust):
    '''restricted custodian - to org'''
    with pytest.reverts("Sender restricted: Issuer"):
        cust.transfer(token, accounts[0], 500, {'from': accounts[0]})


def test_to_investor(token, cust):
    '''restricted custodian - to investor'''
    with pytest.reverts("Sender restricted: Issuer"):
        cust.transfer(token, accounts[2], 500, {'from': accounts[0]})


def test_org_transferFrom(token, cust):
    '''restricted custodian - org transfer out with transferFrom'''
    token.transferFrom(cust, accounts[2], 500, {'from': accounts[0]})
