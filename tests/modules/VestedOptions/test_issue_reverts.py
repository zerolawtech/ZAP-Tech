#!/usr/bin/python3

import pytest

from brownie import accounts, rpc


def test_exercise_price_zero(options, id1):
    '''exercise price cannot be zero'''
    with pytest.reverts("dev: exercise price == 0"):
        options.issueOptions(id1, 0, False, [1, 2], [1, 2], {'from': accounts[0]})


def test_mismatch(options, id1):
    '''arrays must be of same length'''
    with pytest.reverts("dev: length mismatch"):
        options.issueOptions(id1, 10, False, [1, 2], [1, 2, 3], {'from': accounts[0]})


def test_vest_exceeds_expiration(options, id1):
    '''vesting months cannot exceed expiration'''
    with pytest.reverts("dev: vest > expiration"):
        options.issueOptions(id1, 10, False, [1, 2], [1, 100], {'from': accounts[0]})
    options.issueOptions(id1, 10, False, [1, 2], [1, 99], {'from': accounts[0]})


def test_exceeds_authorized_supply(share, options, id1):
    '''options + shares cannot exceed authorized supply'''
    options.issueOptions(id1, 10, False, [250000, 250000], [1, 2], {'from': accounts[0]})
    share.mint(accounts[1], 250000, {'from': accounts[0]})
    with pytest.reverts("dev: exceeds authorized"):
        options.issueOptions(id1, 20, False, [250000, 250000], [1, 2], {'from': accounts[0]})
    options.issueOptions(id1, 20, False, [250000], [4], {'from': accounts[0]})
    with pytest.reverts("dev: exceeds authorized"):
        options.issueOptions(id1, 10, False, [1], [4], {'from': accounts[0]})


def test_iso_mismatch(options, id1):
    '''cannot change iso in same expiration period'''
    options.issueOptions(id1, 10, False, [100, 100], [1, 2], {'from': accounts[0]})
    with pytest.reverts("dev: iso mismatch"):
        options.issueOptions(id1, 10, True, [100, 100], [1, 2], {'from': accounts[0]})
    options.issueOptions(id1, 10, False, [100, 100], [1, 2], {'from': accounts[0]})
    rpc.sleep(2592000)
    options.issueOptions(id1, 10, True, [100, 100], [1, 2], {'from': accounts[0]})
