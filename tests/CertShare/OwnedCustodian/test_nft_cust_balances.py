#!/usr/bin/python3

import pytest

from brownie import accounts


@pytest.fixture(scope="module", autouse=True)
def setup(approve_many, org, nft):
    nft.mint(org, 100000, 0, "0x00", {'from': accounts[0]})


def test_into_custodian(nft, cust):
    '''Transfer into custodian - member'''
    nft.transfer(accounts[1], 10000, {'from': accounts[0]})
    nft.transfer(accounts[2], 10000, {'from': accounts[0]})
    nft.transfer(cust, 4000, {'from': accounts[1]})
    nft.transfer(cust, 10000, {'from': accounts[2]})
    assert nft.balanceOf(accounts[1]) == 6000
    assert nft.custodianBalanceOf(accounts[1], cust) == 4000
    assert nft.balanceOf(accounts[2]) == 0
    assert nft.custodianBalanceOf(accounts[2], cust) == 10000
    assert nft.balanceOf(cust) == 14000


def test_into_custodian_transferRange(nft, cust, no_call_coverage):
    '''Transfer into custodian - transferRange'''
    nft.transfer(accounts[1], 10000, {'from': accounts[0]})
    nft.transfer(accounts[2], 10000, {'from': accounts[0]})
    nft.transferRange(cust, 1000, 5000, {'from': accounts[1]})
    nft.transferRange(cust, 10001, 20001, {'from': accounts[2]})
    assert nft.balanceOf(accounts[1]) == 6000
    assert nft.custodianBalanceOf(accounts[1], cust) == 4000
    assert nft.balanceOf(accounts[2]) == 0
    assert nft.custodianBalanceOf(accounts[2], cust) == 10000
    assert nft.balanceOf(cust) == 14000


def test_cust_internal(nft, cust):
    '''Custodian transfer internal - member to member'''
    nft.transfer(accounts[2], 10000, {'from': accounts[0]})
    nft.transfer(cust, 5000, {'from': accounts[2]})
    cust.transferInternal(nft, accounts[2], accounts[3], 5000, {'from': accounts[0]})
    assert nft.balanceOf(accounts[2]) == 5000
    assert nft.custodianBalanceOf(accounts[1], cust) == 0
    assert nft.balanceOf(accounts[3]) == 0
    assert nft.custodianBalanceOf(accounts[3], cust) == 5000
    assert nft.balanceOf(cust) == 5000


def test_cust_out(nft, cust, no_call_coverage):
    '''Transfer out of custodian - member'''
    nft.transfer(accounts[1], 10000, {'from': accounts[0]})
    nft.transfer(cust, 10000, {'from': accounts[1]})
    cust.transferInternal(nft, accounts[1], accounts[2], 10000, {'from': accounts[0]})
    cust.transfer(nft, accounts[2], 10000, {'from': accounts[0]})
    assert nft.balanceOf(accounts[1]) == 0
    assert nft.custodianBalanceOf(accounts[1], cust) == 0
    assert nft.balanceOf(accounts[2]) == 10000
    assert nft.custodianBalanceOf(accounts[2], cust) == 0
    assert nft.balanceOf(cust) == 0


def test_org_cust_in(org, nft, cust, no_call_coverage):
    '''Transfers into custodian - org'''
    nft.transfer(cust, 10000, {'from': accounts[0]})
    assert nft.balanceOf(accounts[0]) == 0
    assert nft.custodianBalanceOf(accounts[0], cust) == 0
    assert nft.balanceOf(org) == 90000
    assert nft.custodianBalanceOf(org, cust) == 10000
    assert nft.balanceOf(cust) == 10000
    nft.transfer(cust, 90000, {'from': accounts[0]})
    assert nft.balanceOf(accounts[0]) == 0
    assert nft.custodianBalanceOf(accounts[0], cust) == 0
    assert nft.balanceOf(org) == 0
    assert nft.custodianBalanceOf(org, cust) == 100000
    assert nft.balanceOf(cust) == 100000


def test_org_cust_internal(org, nft, cust, no_call_coverage):
    '''Custodian internal transfers - org / member'''
    nft.transfer(cust, 10000, {'from': accounts[0]})
    cust.transferInternal(nft, org, accounts[1], 10000, {'from': accounts[0]})
    assert nft.balanceOf(accounts[0]) == 0
    assert nft.custodianBalanceOf(accounts[0], cust) == 0
    assert nft.balanceOf(org) == 90000
    assert nft.custodianBalanceOf(org, cust) == 0
    assert nft.balanceOf(accounts[1]) == 0
    assert nft.custodianBalanceOf(accounts[1], cust) == 10000
    assert nft.balanceOf(cust) == 10000
    cust.transferInternal(nft, accounts[1], org, 5000, {'from': accounts[0]})
    assert nft.balanceOf(accounts[0]) == 0
    assert nft.custodianBalanceOf(accounts[0], cust) == 0
    assert nft.balanceOf(org) == 90000
    assert nft.custodianBalanceOf(org, cust) == 5000
    assert nft.balanceOf(accounts[1]) == 0
    assert nft.custodianBalanceOf(accounts[1], cust) == 5000
    assert nft.balanceOf(cust) == 10000
    cust.transferInternal(nft, accounts[1], accounts[0], 5000, {'from': accounts[0]})
    assert nft.balanceOf(accounts[0]) == 0
    assert nft.custodianBalanceOf(accounts[0], cust) == 0
    assert nft.balanceOf(org) == 90000
    assert nft.custodianBalanceOf(org, cust) == 10000
    assert nft.balanceOf(accounts[1]) == 0
    assert nft.custodianBalanceOf(accounts[1], cust) == 0
    assert nft.balanceOf(cust) == 10000


def test_org_cust_out(org, nft, cust, no_call_coverage):
    '''Transfers out of custodian - org'''
    nft.transfer(cust, 10000, {'from': accounts[0]})
    assert nft.balanceOf(accounts[0]) == 0
    assert nft.custodianBalanceOf(accounts[0], cust) == 0
    assert nft.balanceOf(org) == 90000
    assert nft.custodianBalanceOf(org, cust) == 10000
    assert nft.balanceOf(cust) == 10000
    cust.transfer(nft, org, 3000, {'from': accounts[0]})
    assert nft.balanceOf(accounts[0]) == 0
    assert nft.custodianBalanceOf(accounts[0], cust) == 0
    assert nft.balanceOf(org) == 93000
    assert nft.custodianBalanceOf(org, cust) == 7000
    assert nft.balanceOf(cust) == 7000
    cust.transfer(nft, accounts[0], 7000, {'from': accounts[0]})
    assert nft.balanceOf(accounts[0]) == 0
    assert nft.custodianBalanceOf(accounts[0], cust) == 0
    assert nft.balanceOf(org) == 100000
    assert nft.custodianBalanceOf(org, cust) == 0
    assert nft.balanceOf(cust) == 0
