#!/usr/bin/python3

import functools
import pytest

from brownie import accounts


@pytest.fixture(scope="module", autouse=True)
def setup(approve_many, org, nft):
    nft.mint(org, 100000, 0, "0x00", {'from': accounts[0]})


@pytest.fixture
def transfer(no_call_coverage, org, nft):
    yield functools.partial(_transfer, org, nft)


@pytest.fixture
def ts(org, nft):
    yield functools.partial(_totalSupply, org, nft)


def test_simple(transfer):
    '''Simple transfer'''
    transfer(0, 1, 12345)


def test_no_intersect(transfer, ts):
    '''No intersection'''
    transfer(0, 1, 10)
    transfer(0, 2, 1000)
    transfer(0, 3, 10)
    transfer(2, 4, 50)
    transfer(2, 4, 900)
    transfer(2, 4, 49)
    transfer(2, 4, 1)
    transfer(4, 2, 1000)
    ts(5)


def test_middle(transfer, ts):
    '''Intersect on both sides'''
    transfer(0, 1, 100)
    transfer(0, 2, 120)
    transfer(0, 1, 3)
    transfer(2, 1, 120)
    ts(3)


def test_start(transfer, ts):
    '''Intersect at start'''
    transfer(0, 1, 3040)
    transfer(0, 2, 33)
    transfer(1, 2, 41)
    transfer(1, 2, 2999)
    ts(3)


def test_stop(transfer, ts):
    '''Intersect at end'''
    transfer(0, 1, 100)
    transfer(0, 2, 100)
    transfer(0, 3, 42)
    transfer(3, 2, 19)
    transfer(3, 2, 22)
    transfer(3, 2, 1)
    ts(4)


def test_one(transfer, ts):
    '''One nft'''
    transfer(0, 1, 1)
    transfer(0, 2, 1)
    transfer(0, 3, 1)
    transfer(0, 4, 1)
    transfer(0, 5, 1)
    transfer(1, 4, 1)
    transfer(2, 3, 1)
    transfer(5, 4, 1)
    transfer(3, 4, 2)
    ts(6)


def test_split(transfer, nft, org, skip_coverage):
    '''many ranges'''
    nft.modifyAuthorizedSupply("1000 gwei", {'from': accounts[0]})
    nft.mint(org, "100 gwei", 0, "0x00", {'from': accounts[0]})
    for i in range(2, 7):
        transfer(0, 1, 12345678)
        transfer(0, i, 12345678)
        transfer(0, 1, 12345678)
        transfer(0, i, 12345678)
    for i in range(6, 1):
        transfer(1, i, nft.balanceOf(accounts[1]) // 2)
    for i in range(1, 5):
        transfer(i, 6, nft.balanceOf(accounts[i]))


def _totalSupply(org, nft, limit):
    b = nft.balanceOf(org)
    for i in range(limit):
        c = nft.balanceOf(accounts[i])
        b += c
    assert nft.totalSupply() == b


def _transfer(org, nft, from_, to, amount):
    if from_ == 0:
        from_bal = nft.balanceOf(org)
    else:
        from_bal = nft.balanceOf(accounts[from_])
    if to == 0:
        to_bal = nft.balanceOf(org)
    else:
        to_bal = nft.balanceOf(accounts[to])
    nft.transfer(accounts[to], amount, {'from': accounts[from_]})
    if from_ == 0 or to == 0:
        return
    assert nft.balanceOf(accounts[from_]) == from_bal - amount
    assert nft.balanceOf(accounts[to]) == to_bal + amount
    assert nft.balanceOf(accounts[from_]) == (
        sum((i[1] - i[0]) for i in nft.rangesOf(accounts[from_]))
    )
    assert nft.balanceOf(accounts[to]) == (
        sum((i[1] - i[0]) for i in nft.rangesOf(accounts[to]))
    )
