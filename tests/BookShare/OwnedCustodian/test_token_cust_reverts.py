#!/usr/bin/python3

import pytest

from brownie import accounts


@pytest.fixture(scope="module", autouse=True)
def setup(id1, id2, org, share):
    share.mint(org, 100000, {"from": accounts[0]})


def test_zero(share, cust):
    """Custodian transfer internal - zero value"""
    share.transfer(accounts[1], 10000, {"from": accounts[0]})
    share.transfer(cust, 5000, {"from": accounts[1]})
    with pytest.reverts("Cannot send 0 shares"):
        cust.transferInternal(share, accounts[1], accounts[2], 0, {"from": accounts[0]})


def test_exceed(share, cust):
    """Custodian transfer internal - exceed balance"""
    share.transfer(accounts[1], 10000, {"from": accounts[0]})
    share.transfer(cust, 5000, {"from": accounts[1]})
    with pytest.reverts("Insufficient Custodial Balance"):
        cust.transferInternal(
            share, accounts[1], accounts[2], 6000, {"from": accounts[0]}
        )


def test_cust_to_cust(OwnedCustodian, org, share, cust):
    """custodian to custodian"""
    cust2 = accounts[0].deploy(OwnedCustodian, [accounts[0]], 1)
    org.addCustodian(cust2, {"from": accounts[0]})
    share.transfer(accounts[1], 10000, {"from": accounts[0]})
    share.transfer(cust, 5000, {"from": accounts[1]})
    with pytest.reverts("Custodian to Custodian"):
        cust.transferInternal(share, accounts[1], cust2, 500, {"from": accounts[0]})


def test_mint(share, cust):
    """mint to custodian"""
    with pytest.reverts():
        share.mint(cust, 1000, {"from": accounts[0]})
