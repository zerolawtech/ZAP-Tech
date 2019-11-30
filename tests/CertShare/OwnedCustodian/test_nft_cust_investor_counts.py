#!/usr/bin/python3

import pytest

from brownie import accounts


@pytest.fixture(scope="module", autouse=True)
def setup(approve_many, org, nft):
    nft.mint(org, 100000, 0, "0x00", {"from": accounts[0]})


def test_into_custodian(check_counts, nft, cust):
    """Transfer into custodian - member"""
    nft.transfer(accounts[1], 10000, {"from": accounts[0]})
    nft.transfer(accounts[2], 10000, {"from": accounts[0]})
    check_counts(one=(2, 1, 1))
    nft.transfer(cust, 5000, {"from": accounts[1]})
    check_counts(one=(2, 1, 1))
    nft.transfer(cust, 10000, {"from": accounts[2]})
    check_counts(one=(2, 1, 1))


def test_cust_internal(check_counts, nft, cust):
    """Custodian transfer internal - member to member"""
    nft.transfer(accounts[2], 10000, {"from": accounts[0]})
    nft.transfer(cust, 5000, {"from": accounts[2]})
    cust.transferInternal(nft, accounts[2], accounts[3], 5000, {"from": accounts[0]})
    check_counts(one=(1, 0, 1), two=(1, 1, 0))
    nft.transfer(accounts[3], 5000, {"from": accounts[0]})
    check_counts(one=(1, 0, 1), two=(1, 1, 0))


def test_cust_out(check_counts, org, nft, cust):
    """Transfer out of custodian - member"""
    nft.transfer(accounts[1], 10000, {"from": accounts[0]})
    nft.transfer(cust, 10000, {"from": accounts[1]})
    cust.transferInternal(nft, accounts[1], accounts[2], 10000, {"from": accounts[0]})
    check_counts(one=(1, 0, 1))
    cust.transfer(nft, accounts[2], 10000, {"from": accounts[0]})
    check_counts(one=(1, 0, 1))
    nft.transfer(org, 10000, {"from": accounts[2]})
    check_counts()


def test_org_cust_in(check_counts, nft, cust):
    """Transfers into custodian - org"""
    nft.transfer(cust, 10000, {"from": accounts[0]})
    check_counts()
    nft.transfer(cust, 90000, {"from": accounts[0]})
    check_counts()


def test_org_cust_internal(check_counts, org, nft, cust):
    """Custodian internal transfers - org / member"""
    nft.transfer(cust, 10000, {"from": accounts[0]})
    cust.transferInternal(nft, org, accounts[1], 10000, {"from": accounts[0]})
    check_counts(one=(1, 1, 0))
    cust.transferInternal(nft, accounts[1], org, 5000, {"from": accounts[0]})
    check_counts(one=(1, 1, 0))
    cust.transferInternal(nft, accounts[1], accounts[0], 5000, {"from": accounts[0]})
    check_counts()


def test_org_cust_out(check_counts, org, nft, cust):
    """Transfers out of custodian - org"""
    nft.transfer(cust, 10000, {"from": accounts[0]})
    check_counts()
    cust.transfer(nft, org, 3000, {"from": accounts[0]})
    check_counts()
    cust.transfer(nft, accounts[0], 7000, {"from": accounts[0]})
    check_counts()
