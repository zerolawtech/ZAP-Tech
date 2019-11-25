#!/usr/bin/python3

import pytest

from brownie import accounts


@pytest.fixture(scope="module", autouse=True)
def setup(approve_many, org, nft):
    nft.mint(org, 100000, 0, "0x00", {'from': accounts[0]})


def test_zero_nfts(nft):
    '''cannot send 0 nfts'''
    with pytest.reverts("Cannot send 0 tokens"):
        nft.transfer(accounts[1], 0, {'from': accounts[0]})


def test_overflow(nft):
    '''cannot send >2**48 nfts'''
    with pytest.reverts("Value too large"):
        nft.transfer(accounts[1], 2**49, {'from': accounts[0]})


def test_to_self(nft):
    '''cannot send to self'''
    with pytest.reverts("Cannot send to self"):
        nft.transfer(accounts[0], 100, {'from': accounts[0]})


def test_insufficient_balance_investor(nft):
    '''insufficient balance - investor to investor'''
    nft.transfer(accounts[1], 1000, {'from': accounts[0]})
    with pytest.reverts("Insufficient Balance"):
        nft.transfer(accounts[2], 2000, {'from': accounts[1]})


def test_insufficient_balance_org(nft):
    '''insufficient balance - org to investor'''
    with pytest.reverts("Insufficient Balance"):
        nft.transfer(accounts[1], 20000000000, {'from': accounts[0]})


def test_balance(nft):
    '''successful transfer'''
    nft.transfer(accounts[1], 1000, {'from': accounts[0]})
    assert nft.balanceOf(accounts[1]) == 1000
    nft.transfer(accounts[2], 400, {'from': accounts[1]})
    assert nft.balanceOf(accounts[1]) == 600
    assert nft.balanceOf(accounts[2]) == 400


def test_balance_org(org, nft):
    '''org balances'''
    assert nft.balanceOf(accounts[0]) == 0
    assert nft.balanceOf(org) == 100000
    nft.transfer(accounts[1], 1000, {'from': accounts[0]})
    assert nft.balanceOf(accounts[0]) == 0
    assert nft.balanceOf(org) == 99000
    nft.transfer(accounts[0], 1000, {'from': accounts[1]})
    assert nft.balanceOf(accounts[0]) == 0
    assert nft.balanceOf(org) == 100000
    nft.transfer(accounts[1], 1000, {'from': accounts[0]})
    nft.transfer(org, 1000, {'from': accounts[1]})
    assert nft.balanceOf(accounts[0]) == 0
    assert nft.balanceOf(org) == 100000


def test_authority_permission(org, nft):
    '''org subauthority balances'''
    org.addAuthority([accounts[-1]], ["0xa9059cbb"], 2000000000, 1, {'from': accounts[0]})
    nft.transfer(accounts[1], 1000, {'from': accounts[-1]})
    assert nft.balanceOf(accounts[0]) == 0
    assert nft.balanceOf(accounts[-1]) == 0
    assert nft.balanceOf(org) == 99000
    nft.transfer(accounts[-1], 1000, {'from': accounts[1]})
    assert nft.balanceOf(accounts[0]) == 0
    assert nft.balanceOf(accounts[-1]) == 0
    assert nft.balanceOf(org) == 100000
