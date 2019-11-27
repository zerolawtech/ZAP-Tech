#!/usr/bin/python3

import pytest

from brownie import accounts


@pytest.fixture(scope="module", autouse=True)
def setup(approve_many, org, nft):
    nft.mint(org, 100000, 0, "0x00", {'from': accounts[0]})


def test_zero(nft, cust):
    '''Custodian transfer internal - zero value'''
    nft.transfer(accounts[2], 10000, {'from': accounts[0]})
    nft.transfer(cust, 5000, {'from': accounts[2]})
    with pytest.reverts("Cannot send 0 shares"):
        cust.transferInternal(nft, accounts[2], accounts[3], 0, {'from': accounts[0]})


def test_exceed(nft, cust):
    '''Custodian transfer internal - exceed balance'''
    nft.transfer(accounts[2], 10000, {'from': accounts[0]})
    nft.transfer(cust, 5000, {'from': accounts[2]})
    with pytest.reverts("Insufficient Custodial Balance"):
        cust.transferInternal(nft, accounts[2], accounts[3], 6000, {'from': accounts[0]})

def test_cust_to_cust(OwnedCustodian, org, nft, cust):
    '''custodian to custodian'''
    cust2 = accounts[0].deploy(OwnedCustodian, [accounts[0]], 1)
    org.addCustodian(cust2, {'from': accounts[0]})
    nft.transfer(accounts[2], 10000, {'from': accounts[0]})
    nft.transfer(cust, 5000, {'from': accounts[2]})
    with pytest.reverts("Custodian to Custodian"):
        cust.transferInternal(nft, accounts[2], cust2, 500, {'from': accounts[0]})


def test_mint(nft, cust):
    '''mint to custodian'''
    with pytest.reverts():
        nft.mint(cust, 1000, 0, "0x00", {'from': accounts[0]})


def test_transfer_range(nft, cust):
    '''transfer range - custodian'''
    nft.transferRange(cust, 100, 1000, {'from': accounts[0]})
    with pytest.reverts("dev: custodian"):
        nft.transferRange(accounts[0], 100, 1000, {'from': accounts[0]})