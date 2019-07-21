#!/usr/bin/python3

import pytest

from brownie import accounts, rpc


@pytest.fixture(scope="module", autouse=True)
def setup(approve_many, issuer, nft):
    nft.mint(issuer, 100000, 0, "0x00", {'from': accounts[0]})


def test_global_lock(issuer, nft):
    '''global lock - investor / investor'''
    nft.transfer(accounts[1], 1000, {'from': accounts[0]})
    issuer.setGlobalRestriction(True, {'from': accounts[0]})
    with pytest.reverts("Transfers locked: Issuer"):
        nft.transfer(accounts[2], 1000, {'from': accounts[1]})
    issuer.setGlobalRestriction(False, {'from': accounts[0]})
    nft.transfer(accounts[2], 1000, {'from': accounts[1]})


def test_global_lock_issuer(issuer, nft):
    '''global lock - issuer / investor'''
    issuer.setGlobalRestriction(True, {'from': accounts[0]})
    nft.transfer(accounts[1], 1000, {'from': accounts[0]})
    with pytest.reverts("Transfers locked: Issuer"):
        nft.transfer(accounts[0], 1000, {'from': accounts[1]})
    issuer.setGlobalRestriction(False, {'from': accounts[0]})
    nft.transfer(accounts[0], 1000, {'from': accounts[1]})


def test_nft_lock(issuer, nft):
    '''nft lock - investor / investor'''
    nft.transfer(accounts[1], 1000, {'from': accounts[0]})
    issuer.setTokenRestriction(nft, True, {'from': accounts[0]})
    with pytest.reverts("Transfers locked: Token"):
        nft.transfer(accounts[2], 1000, {'from': accounts[1]})
    issuer.setTokenRestriction(nft, False, {'from': accounts[0]})
    nft.transfer(accounts[2], 1000, {'from': accounts[1]})


def test_nft_lock_issuer(issuer, nft):
    '''nft lock - issuer / investor'''
    issuer.setTokenRestriction(nft, True, {'from': accounts[0]})
    nft.transfer(accounts[1], 1000, {'from': accounts[0]})
    with pytest.reverts("Transfers locked: Token"):
        nft.transfer(accounts[0], 1000, {'from': accounts[1]})
    issuer.setTokenRestriction(nft, False, {'from': accounts[0]})
    nft.transfer(accounts[0], 1000, {'from': accounts[1]})


def test_time(nft):
    '''Block transfers with range time lock'''
    nft.mint(accounts[1], 10000, rpc.time() + 20, "0x00", {'from': accounts[0]})
    with pytest.reverts():
        nft.transfer(accounts[2], 1000, {'from': accounts[1]})
    rpc.sleep(21)
    nft.transfer(accounts[2], 1000, {'from': accounts[1]})


def test_time_partial(nft):
    '''Partially block a transfer with range time lock'''
    nft.mint(accounts[1], 10000, 0, "0x00", {'from': accounts[0]})
    nft.modifyRanges(102001, 106001, rpc.time() + 20, "0x00", {'from': accounts[0]})
    assert nft.getRange(102001)['_stop'] == 106001
    nft.transfer(accounts[2], 4000, {'from': accounts[1]})
    assert nft.rangesOf(accounts[1]) == ((108001, 110001), (102001, 106001))
    rpc.sleep(25)
    nft.transfer(accounts[2], 6000, {'from': accounts[1]})
    assert nft.rangesOf(accounts[2]) == ((100001, 110001),)
