#!/usr/bin/python3

import pytest

from brownie import accounts


@pytest.fixture(scope="module", autouse=True)
def setup(approve_many, issuer, nft, cust):
    nft.mint(issuer, 100000, 0, "0x00", {'from': accounts[0]})
    nft.transfer(accounts[2], 1000, {'from': accounts[0]})
    nft.transfer(cust, 500, {'from': accounts[0]})
    nft.transfer(cust, 500, {'from': accounts[2]})
    issuer.setEntityRestriction(cust.ownerID(), True, {'from': accounts[0]})


def test_from_issuer(nft, cust):
    '''restricted custodian - issuer to custodian'''
    with pytest.reverts("Receiver restricted: Issuer"):
        nft.transfer(cust, 1000, {'from': accounts[0]})


def test_from_investor(nft, cust):
    '''restricted custodian - investor to custodian'''
    with pytest.reverts("Receiver restricted: Issuer"):
        nft.transfer(cust, 1000, {'from': accounts[2]})


def test_transferInternal(nft, cust):
    '''restricted custodian - internal transfer'''
    with pytest.reverts("Authority restricted"):
        cust.transferInternal(nft, accounts[2], accounts[3], 500, {'from': accounts[0]})


def test_to_issuer(nft, cust):
    '''restricted custodian - to issuer'''
    with pytest.reverts("Sender restricted: Issuer"):
        cust.transfer(nft, accounts[0], 500, {'from': accounts[0]})


def test_to_investor(nft, cust):
    '''restricted custodian - to investor'''
    with pytest.reverts("Sender restricted: Issuer"):
        cust.transfer(nft, accounts[2], 500, {'from': accounts[0]})


def test_issuer_transferFrom(nft, cust):
    '''restricted custodian - issuer transfer out with transferFrom'''
    nft.transferFrom(cust, accounts[2], 500, {'from': accounts[0]})
