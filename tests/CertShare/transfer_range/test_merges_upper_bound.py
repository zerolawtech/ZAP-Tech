#!/usr/bin/python3

import pytest

from brownie import accounts


@pytest.fixture(scope="module", autouse=True)
def setup(approve_many, nft):
    nft.modifyAuthorizedSupply(2 ** 48, {"from": accounts[0]})
    nft.mint(accounts[1], 2 ** 48 - 20002, 0, "0x00", {"from": accounts[0]})
    nft.mint(accounts[2], 10000, 0, "0x00", {"from": accounts[0]})
    nft.mint(accounts[3], 10000, 0, "0x00", {"from": accounts[0]})


def test_initial(check_ranges):
    check_ranges(
        [(1, 2 ** 48 - 20001)],
        [(2 ** 48 - 20001, 2 ** 48 - 10001)],
        [(2 ** 48 - 10001, 2 ** 48 - 1)],
        [],
    )


def test_whole_range_right_abs(check_ranges, nft):
    """whole range, merge right, absolute"""
    nft.transferRange(
        accounts[3], 2 ** 48 - 20001, 2 ** 48 - 10001, {"from": accounts[2]}
    )
    check_ranges([(1, 2 ** 48 - 20001)], [], [(2 ** 48 - 20001, 2 ** 48 - 1)], [])


def test_whole_range_same_both(check_ranges, nft):
    """whole range, merge both sides, absolute both"""
    nft.transferRange(accounts[3], 1, 2 ** 48 - 20001, {"from": accounts[1]})
    nft.transferRange(
        accounts[3], 2 ** 48 - 20001, 2 ** 48 - 10001, {"from": accounts[2]}
    )
    check_ranges([], [], [(1, 2 ** 48 - 1)], [])


def test_whole_range_same_right(check_ranges, nft):
    """whole range, merge both sides, absolute right"""
    nft.transferRange(accounts[3], 5000, 2 ** 48 - 20001, {"from": accounts[1]})
    nft.transferRange(
        accounts[3], 2 ** 48 - 20001, 2 ** 48 - 10001, {"from": accounts[2]}
    )
    check_ranges([(1, 5000)], [], [(5000, 2 ** 48 - 1)], [])


def test_stop_absolute(check_ranges, nft):
    """partial, touch stop, absolute"""
    nft.transferRange(accounts[4], 2 ** 48 - 5000, 2 ** 48 - 1, {"from": accounts[3]})
    check_ranges(
        [(1, 2 ** 48 - 20001)],
        [(2 ** 48 - 20001, 2 ** 48 - 10001)],
        [(2 ** 48 - 10001, 2 ** 48 - 5000)],
        [(2 ** 48 - 5000, 2 ** 48 - 1)],
    )


def test_stop_partial_same_abs(check_ranges, nft):
    """partial, touch stop, merge, absolute"""
    nft.transferRange(
        accounts[3], 2 ** 48 - 15000, 2 ** 48 - 10001, {"from": accounts[2]}
    )
    check_ranges(
        [(1, 2 ** 48 - 20001)],
        [(2 ** 48 - 20001, 2 ** 48 - 15000)],
        [(2 ** 48 - 15000, 2 ** 48 - 1)],
        [],
    )
