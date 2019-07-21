#!/usr/bin/python3

import pytest

from brownie import accounts


@pytest.fixture(scope="module", autouse=True)
def setup(approve_many, issuer, nft):
    nft.mint(issuer, 100000, 0, "0x00", {'from': accounts[0]})


def test_into_custodian(nft, cust):
    '''Transfer into custodian - investor'''
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
    '''Custodian transfer internal - investor to investor'''
    nft.transfer(accounts[2], 10000, {'from': accounts[0]})
    nft.transfer(cust, 5000, {'from': accounts[2]})
    cust.transferInternal(nft, accounts[2], accounts[3], 5000, {'from': accounts[0]})
    assert nft.balanceOf(accounts[2]) == 5000
    assert nft.custodianBalanceOf(accounts[1], cust) == 0
    assert nft.balanceOf(accounts[3]) == 0
    assert nft.custodianBalanceOf(accounts[3], cust) == 5000
    assert nft.balanceOf(cust) == 5000


def test_cust_out(nft, cust, no_call_coverage):
    '''Transfer out of custodian - investor'''
    nft.transfer(accounts[1], 10000, {'from': accounts[0]})
    nft.transfer(cust, 10000, {'from': accounts[1]})
    cust.transferInternal(nft, accounts[1], accounts[2], 10000, {'from': accounts[0]})
    cust.transfer(nft, accounts[2], 10000, {'from': accounts[0]})
    assert nft.balanceOf(accounts[1]) == 0
    assert nft.custodianBalanceOf(accounts[1], cust) == 0
    assert nft.balanceOf(accounts[2]) == 10000
    assert nft.custodianBalanceOf(accounts[2], cust) == 0
    assert nft.balanceOf(cust) == 0


def test_issuer_cust_in(issuer, nft, cust, no_call_coverage):
    '''Transfers into custodian - issuer'''
    nft.transfer(cust, 10000, {'from': accounts[0]})
    assert nft.balanceOf(accounts[0]) == 0
    assert nft.custodianBalanceOf(accounts[0], cust) == 0
    assert nft.balanceOf(issuer) == 90000
    assert nft.custodianBalanceOf(issuer, cust) == 10000
    assert nft.balanceOf(cust) == 10000
    nft.transfer(cust, 90000, {'from': accounts[0]})
    assert nft.balanceOf(accounts[0]) == 0
    assert nft.custodianBalanceOf(accounts[0], cust) == 0
    assert nft.balanceOf(issuer) == 0
    assert nft.custodianBalanceOf(issuer, cust) == 100000
    assert nft.balanceOf(cust) == 100000


def test_issuer_cust_internal(issuer, nft, cust, no_call_coverage):
    '''Custodian internal transfers - issuer / investor'''
    nft.transfer(cust, 10000, {'from': accounts[0]})
    cust.transferInternal(nft, issuer, accounts[1], 10000, {'from': accounts[0]})
    assert nft.balanceOf(accounts[0]) == 0
    assert nft.custodianBalanceOf(accounts[0], cust) == 0
    assert nft.balanceOf(issuer) == 90000
    assert nft.custodianBalanceOf(issuer, cust) == 0
    assert nft.balanceOf(accounts[1]) == 0
    assert nft.custodianBalanceOf(accounts[1], cust) == 10000
    assert nft.balanceOf(cust) == 10000
    cust.transferInternal(nft, accounts[1], issuer, 5000, {'from': accounts[0]})
    assert nft.balanceOf(accounts[0]) == 0
    assert nft.custodianBalanceOf(accounts[0], cust) == 0
    assert nft.balanceOf(issuer) == 90000
    assert nft.custodianBalanceOf(issuer, cust) == 5000
    assert nft.balanceOf(accounts[1]) == 0
    assert nft.custodianBalanceOf(accounts[1], cust) == 5000
    assert nft.balanceOf(cust) == 10000
    cust.transferInternal(nft, accounts[1], accounts[0], 5000, {'from': accounts[0]})
    assert nft.balanceOf(accounts[0]) == 0
    assert nft.custodianBalanceOf(accounts[0], cust) == 0
    assert nft.balanceOf(issuer) == 90000
    assert nft.custodianBalanceOf(issuer, cust) == 10000
    assert nft.balanceOf(accounts[1]) == 0
    assert nft.custodianBalanceOf(accounts[1], cust) == 0
    assert nft.balanceOf(cust) == 10000


def test_issuer_cust_out(issuer, nft, cust, no_call_coverage):
    '''Transfers out of custodian - issuer'''
    nft.transfer(cust, 10000, {'from': accounts[0]})
    assert nft.balanceOf(accounts[0]) == 0
    assert nft.custodianBalanceOf(accounts[0], cust) == 0
    assert nft.balanceOf(issuer) == 90000
    assert nft.custodianBalanceOf(issuer, cust) == 10000
    assert nft.balanceOf(cust) == 10000
    cust.transfer(nft, issuer, 3000, {'from': accounts[0]})
    assert nft.balanceOf(accounts[0]) == 0
    assert nft.custodianBalanceOf(accounts[0], cust) == 0
    assert nft.balanceOf(issuer) == 93000
    assert nft.custodianBalanceOf(issuer, cust) == 7000
    assert nft.balanceOf(cust) == 7000
    cust.transfer(nft, accounts[0], 7000, {'from': accounts[0]})
    assert nft.balanceOf(accounts[0]) == 0
    assert nft.custodianBalanceOf(accounts[0], cust) == 0
    assert nft.balanceOf(issuer) == 100000
    assert nft.custodianBalanceOf(issuer, cust) == 0
    assert nft.balanceOf(cust) == 0
