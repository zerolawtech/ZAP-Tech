#!/usr/bin/python3

import pytest

from brownie import accounts

zero = "0x0000000000000000000000000000000000000000"


@pytest.fixture(scope="module", autouse=True)
def setup(approve_many, nft):
    nft.mint(accounts[1], 10000, 0, "0x01", {'from': accounts[0]})
    nft.mint(accounts[2], 10000, 0, "0x01", {'from': accounts[0]})
    nft.mint(accounts[3], 10000, 0, "0x01", {'from': accounts[0]})


def test_modify_range(nft):
    '''Modify range'''
    nft.modifyRange(10001, 0, "0x1234")
    assert nft.getRange(1) == (accounts[1], 1, 10001, 0, "0x0001", zero)
    assert nft.getRange(10001) == (accounts[2], 10001, 20001, 0, "0x1234", zero)
    assert nft.getRange(20001) == (accounts[3], 20001, 30001, 0, "0x0001", zero)


def test_modify_ranges(nft):
    '''Modify ranges'''
    nft.modifyRanges(5000, 25000, 0, "0x1234", {'from': accounts[0]})
    assert nft.rangesOf(accounts[1]) == ((1, 5000), (5000, 10001))
    assert nft.rangesOf(accounts[2]) == ((10001, 20001),)
    assert nft.rangesOf(accounts[3]) == ((20001, 25000), (25000, 30001))


def test_modify_many(nft):
    '''Modify many rangels'''
    nft.modifyRanges(5000, 25000, 0, "0x1234")
    nft.modifyRanges(7000, 15000, 0, "0x1111")
    nft.modifyRanges(14800, 22000, 0, "0x9999")
    assert nft.getRange(5001) == (accounts[1], 5000, 7000, 0, "0x1234", zero)
    assert nft.getRange(7001) == (accounts[1], 7000, 10001, 0, "0x1111", zero)
    assert nft.getRange(10002) == (accounts[2], 10001, 14800, 0, "0x1111", zero)
    assert nft.getRange(14810) == (accounts[2], 14800, 20001, 0, "0x9999", zero)
    assert nft.getRange(20002) == (accounts[3], 20001, 22000, 0, "0x9999", zero)


def test_modify_join(nft):
    '''Split and join ranges with modifyRange'''
    nft.modifyRanges(2000, 4000, 0, "0x1234")
    assert nft.rangesOf(accounts[1]) == ((1, 2000), (4000, 10001), (2000, 4000))
    nft.modifyRange(2000, 0, "0x01")
    assert nft.rangesOf(accounts[1]) == ((1, 10001),)


def test_modify_join_many(nft):
    '''Split and join with modifyRanges'''
    nft.modifyRanges(2000, 4000, 0, "0x1234")
    nft.modifyRanges(1000, 6000, 0, "0x01")
    assert nft.rangesOf(accounts[1]) == ((1, 10001),)
