#!/usr/bin/python3

import functools
import pytest

from brownie import accounts


@pytest.fixture(scope="module", autouse=True)
def setup(approve_many, nft):
    nft.mint(accounts[1], 10000, 0, "0x00", {"from": accounts[0]})
    nft.mint(accounts[2], 10000, 0, "0x00", {"from": accounts[0]})
    nft.mint(accounts[3], 10000, 0, "0x00", {"from": accounts[0]})


@pytest.fixture(scope="module")
def check_ranges(nft, cust):
    upper = nft.totalSupply() + 1
    yield functools.partial(_check, nft, cust, upper)


def test_inside(check_ranges, nft, cust):
    """inside"""
    nft.transferRange(cust, 12000, 13000, {"from": accounts[2]})
    check_ranges(
        ([(1, 10001)], []),
        ([(10001, 12000), (13000, 20001)], [(12000, 13000)]),
        ([(20001, 30001)], []),
    )


def test_start_partial_different(check_ranges, nft, cust):
    """partial, touch start, no merge"""
    nft.transferRange(cust, 10001, 11001, {"from": accounts[2]})
    check_ranges(
        ([(1, 10001)], []), ([(11001, 20001)], [(10001, 11001)]), ([(20001, 30001)], [])
    )


def test_start_partial_same(check_ranges, nft, cust):
    """partial, touch start, merge, absolute"""
    nft.transferRange(cust, 1, 10001, {"from": accounts[1]})
    nft.transferRange(accounts[1], 10001, 20001, {"from": accounts[2]})
    nft.transferRange(cust, 10001, 11001, {"from": accounts[1]})
    check_ranges(([(11001, 20001)], [(1, 11001)]), ([], []), ([(20001, 30001)], []))


def test_start_partial_same_abs(check_ranges, nft, cust):
    """partial, touch start, merge"""
    nft.transferRange(cust, 5000, 10001, {"from": accounts[1]})
    nft.transferRange(accounts[1], 10001, 20001, {"from": accounts[2]})
    nft.transferRange(cust, 10001, 11001, {"from": accounts[1]})
    check_ranges(
        ([(1, 5000), (11001, 20001)], [(5000, 11001)]), ([], []), ([(20001, 30001)], [])
    )


def test_start_absolute(check_ranges, nft, cust):
    """touch start, absolute"""
    nft.transferRange(cust, 1, 100, {"from": accounts[1]})
    check_ranges(
        ([(100, 10001)], [(1, 100)]), ([(10001, 20001)], []), ([(20001, 30001)], [])
    )


def test_stop_partial_different(check_ranges, nft, cust):
    """partial, touch stop, no merge"""
    nft.transferRange(cust, 19000, 20001, {"from": accounts[2]})
    check_ranges(
        ([(1, 10001)], []), ([(10001, 19000)], [(19000, 20001)]), ([(20001, 30001)], [])
    )


def test_stop_partial_same_abs(check_ranges, nft, cust):
    """partial, touch stop, merge, absolute"""
    nft.transferRange(cust, 20001, 30001, {"from": accounts[3]})
    nft.transferRange(accounts[3], 10001, 20001, {"from": accounts[2]})
    nft.transferRange(cust, 19000, 20001, {"from": accounts[3]})
    check_ranges(([(1, 10001)], []), ([], []), ([(10001, 19000)], [(19000, 30001)]))


def test_stop_partial_same(check_ranges, nft, cust):
    """partial, touch stop, merge"""
    nft.transferRange(cust, 20001, 25000, {"from": accounts[3]})
    nft.transferRange(accounts[3], 10001, 20001, {"from": accounts[2]})
    nft.transferRange(cust, 19000, 20001, {"from": accounts[3]})
    check_ranges(
        ([(1, 10001)], []),
        ([], []),
        ([(10001, 19000), (25000, 30001)], [(19000, 25000)]),
    )


def test_stop_absolute(check_ranges, nft, cust):
    """partial, touch stop, absolute"""
    nft.transferRange(cust, 29000, 30001, {"from": accounts[3]})
    check_ranges(
        ([(1, 10001)], []), ([(10001, 20001)], []), ([(20001, 29000)], [(29000, 30001)])
    )


def test_whole_range_different(check_ranges, nft, cust):
    """whole range, no merge"""
    nft.transferRange(cust, 10001, 20001, {"from": accounts[2]})
    check_ranges(([(1, 10001)], []), ([], [(10001, 20001)]), ([(20001, 30001)], []))


def test_whole_range_same(check_ranges, nft, cust):
    """whole range, merge both sides"""
    nft.transferRange(accounts[2], 5000, 10001, {"from": accounts[1]})
    nft.transferRange(accounts[2], 20001, 25000, {"from": accounts[3]})
    nft.transferRange(cust, 5000, 10001, {"from": accounts[2]})
    nft.transferRange(cust, 20001, 25000, {"from": accounts[2]})
    nft.transferRange(cust, 10001, 20001, {"from": accounts[2]})
    check_ranges(([(1, 5000)], []), ([], [(5000, 25000)]), ([(25000, 30001)], []))


def test_whole_range_same_left(check_ranges, nft, cust):
    """whole range, merge both sides, absolute left"""
    nft.transferRange(accounts[2], 1, 10001, {"from": accounts[1]})
    nft.transferRange(accounts[2], 20001, 25000, {"from": accounts[3]})
    nft.transferRange(cust, 1, 10001, {"from": accounts[2]})
    nft.transferRange(cust, 20001, 25000, {"from": accounts[2]})
    nft.transferRange(cust, 10001, 20001, {"from": accounts[2]})
    check_ranges(([], []), ([], [(1, 25000)]), ([(25000, 30001)], []))


def test_whole_range_same_right(check_ranges, nft, cust):
    """whole range, merge both sides, absolute right"""
    nft.transferRange(accounts[2], 5000, 10001, {"from": accounts[1]})
    nft.transferRange(accounts[2], 20001, 30001, {"from": accounts[3]})
    nft.transferRange(cust, 5000, 10001, {"from": accounts[2]})
    nft.transferRange(cust, 20001, 30001, {"from": accounts[2]})
    nft.transferRange(cust, 10001, 20001, {"from": accounts[2]})
    check_ranges(([(1, 5000)], []), ([], [(5000, 30001)]), ([], []))


def test_whole_range_same_both(check_ranges, nft, cust):
    """whole range, merge both sides, absolute both"""
    nft.transferRange(accounts[2], 1, 10001, {"from": accounts[1]})
    nft.transferRange(accounts[2], 20001, 30001, {"from": accounts[3]})
    nft.transferRange(cust, 1, 10001, {"from": accounts[2]})
    nft.transferRange(cust, 20001, 30001, {"from": accounts[2]})
    nft.transferRange(cust, 10001, 20001, {"from": accounts[2]})
    check_ranges(([], []), ([], [(1, 30001)]), ([], []))


def test_whole_range_left_abs(check_ranges, nft, cust):
    """whole range, merge left, absolute"""
    nft.transferRange(cust, 1, 10001, {"from": accounts[1]})
    nft.transferRange(accounts[1], 10001, 20001, {"from": accounts[2]})
    nft.transferRange(cust, 10001, 20001, {"from": accounts[1]})
    check_ranges(([], [(1, 20001)]), ([], []), ([(20001, 30001)], []))


def test_whole_range_left(check_ranges, nft, cust):
    """whole range, merge left"""
    nft.transferRange(cust, 5000, 10001, {"from": accounts[1]})
    nft.transferRange(accounts[1], 10001, 20001, {"from": accounts[2]})
    nft.transferRange(cust, 10001, 20001, {"from": accounts[1]})
    check_ranges(([(1, 5000)], [(5000, 20001)]), ([], []), ([(20001, 30001)], []))


def test_whole_range_right_abs(check_ranges, nft, cust):
    """whole range, merge right, absolute"""
    nft.transferRange(accounts[2], 20001, 30001, {"from": accounts[3]})
    nft.transferRange(cust, 20001, 30001, {"from": accounts[2]})
    nft.transferRange(cust, 10001, 20001, {"from": accounts[2]})
    check_ranges(([(1, 10001)], []), ([], [(10001, 30001)]), ([], []))


def test_whole_range_right(check_ranges, nft, cust):
    """whole range, merge right"""
    nft.transferRange(accounts[2], 20001, 25000, {"from": accounts[3]})
    nft.transferRange(cust, 20001, 25000, {"from": accounts[2]})
    nft.transferRange(cust, 10001, 20001, {"from": accounts[2]})
    check_ranges(([(1, 10001)], []), ([], [(10001, 25000)]), ([(25000, 30001)], []))


def _check(nft, cust, upper, *expected_ranges):
    assert nft.balanceOf(cust) == sum(
        (x[1] - x[0]) for i in expected_ranges for x in i[1] if x
    )
    for num, expected in enumerate(expected_ranges, start=1):
        held, custodied = expected
        address = accounts[num]
        ranges = nft.rangesOf(address)
        assert set(ranges) == set(held)
        assert nft.balanceOf(address) == sum((i[1] - i[0]) for i in held)
        _compare_ranges(
            nft, upper, held, num, "0x0000000000000000000000000000000000000000"
        )
        ranges = nft.custodianRangesOf(address, cust)
        assert set(ranges) == set(custodied)
        assert nft.custodianBalanceOf(address, cust) == sum(
            (i[1] - i[0]) for i in custodied
        )
        _compare_ranges(nft, upper, custodied, num, cust)


def _compare_ranges(nft, upper, ranges, num, custaddress):
    address = accounts[num]
    for start, stop in ranges:
        if stop - start == 1:
            assert nft.getRange(start) == (
                address,
                start,
                stop,
                0,
                "0x0000",
                custaddress,
            )
            continue
        for i in range(max(1, start - 1), start + 2):
            try:
                data = nft.getRange(i)
            except Exception:
                raise AssertionError(
                    f"Could not get range pointer {i} for account {num}"
                )
            if i < start:
                assert data[0] != address or data[5] != custaddress
                assert data[2] == start
            else:
                assert data[0] == address and data[5] == custaddress
                assert data[2] == stop
        for i in range(stop - 1, min(stop + 2, upper)):
            data = nft.getRange(i)
            if i < stop:
                assert data[0] == address and data[5] == custaddress
                assert data[1] == start
            else:

                assert data[0] != address or data[5] != custaddress
                assert data[1] == stop
