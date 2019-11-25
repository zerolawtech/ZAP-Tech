#!/usr/bin/python3

import pytest

from brownie import accounts, rpc


@pytest.fixture(scope="module", autouse=True)
def setup(approve_many, share, cust):
    for i in range(1, 6):
        share.mint(accounts[i], 3000 * i, {'from': accounts[0]})
        share.transfer(cust, 1000 * i, {'from': accounts[i]})


def test_check_balances(cp, share, cust, cptime):
    '''check balances'''
    cp.newCheckpoint(share, cptime, {'from': accounts[0]})
    rpc.sleep(110)
    for i in range(1, 6):
        assert cp.custodianBalanceAt(share, accounts[i], cust, cptime) == i * 1000


def test_moved_before(cp, share, cust, cptime):
    '''moved before checkpoint'''
    cp.newCheckpoint(share, cptime, {'from': accounts[0]})
    for i in range(1, 6):
        cust.transferInternal(share, accounts[i], accounts[0], 1000, {'from': accounts[0]})
    rpc.sleep(110)
    for i in range(1, 6):
        assert cp.custodianBalanceAt(share, accounts[i], cust, cptime) == (i - 1) * 1000


def test_moved_after(cp, share, cust, cptime):
    '''moved after checkpoint'''
    cp.newCheckpoint(share, cptime, {'from': accounts[0]})
    rpc.sleep(110)
    for i in range(1, 6):
        assert cp.custodianBalanceAt(share, accounts[i], cust, cptime) == i * 1000
        cust.transferInternal(share, accounts[i], accounts[0], 1000, {'from': accounts[0]})
        assert cp.custodianBalanceAt(share, accounts[i], cust, cptime) == i * 1000


def test_moved_before_after(cp, share, cust, cptime):
    '''moved before and after checkpoint'''
    cp.newCheckpoint(share, cptime, {'from': accounts[0]})
    for i in range(1, 6):
        cust.transferInternal(share, accounts[i], accounts[0], 1000, {'from': accounts[0]})
    rpc.sleep(110)
    for i in range(1, 6):
        assert cp.custodianBalanceAt(share, accounts[i], cust, cptime) == (i - 1) * 1000
        cust.transferInternal(share, accounts[0], accounts[i], 1000, {'from': accounts[0]})
        assert cp.custodianBalanceAt(share, accounts[i], cust, cptime) == (i - 1) * 1000


def test_two_checkpoints(cp, share, cust, cptime):
    '''check balances - two checkpoints'''
    cp.newCheckpoint(share, cptime, {'from': accounts[0]})
    cp.newCheckpoint(share, cptime + 100, {'from': accounts[0]})
    rpc.sleep(110)
    for i in range(1, 6):
        assert cp.custodianBalanceAt(share, accounts[i], cust, cptime) == i * 1000
    rpc.sleep(110)
    for i in range(1, 6):
        assert cp.custodianBalanceAt(share, accounts[i], cust, cptime) == i * 1000
        assert cp.custodianBalanceAt(share, accounts[i], cust, cptime + 100) == i * 1000


def test_two_moved_before(cp, share, cust, cptime):
    '''two checkpoints - moved before'''
    cp.newCheckpoint(share, cptime, {'from': accounts[0]})
    cp.newCheckpoint(share, cptime + 100, {'from': accounts[0]})
    for i in range(1, 6):
        cust.transferInternal(share, accounts[i], accounts[0], 1000, {'from': accounts[0]})
    rpc.sleep(110)
    for i in range(1, 6):
        assert cp.custodianBalanceAt(share, accounts[i], cust, cptime) == (i - 1) * 1000
    rpc.sleep(110)
    for i in range(1, 6):
        assert cp.custodianBalanceAt(share, accounts[i], cust, cptime) == (i - 1) * 1000
        assert cp.custodianBalanceAt(share, accounts[i], cust, cptime + 100) == (i - 1) * 1000


def test_two_moved_in_between(cp, share, cust, cptime):
    '''two checkpoints - moved in between'''
    cp.newCheckpoint(share, cptime, {'from': accounts[0]})
    cp.newCheckpoint(share, cptime + 100, {'from': accounts[0]})
    rpc.sleep(110)
    for i in range(1, 6):
        cust.transferInternal(share, accounts[i], accounts[0], 1000, {'from': accounts[0]})
    rpc.sleep(110)
    for i in range(1, 6):
        assert cp.custodianBalanceAt(share, accounts[i], cust, cptime) == i * 1000
        assert cp.custodianBalanceAt(share, accounts[i], cust, cptime + 100) == (i - 1) * 1000


def test_two_moved_after(cp, share, cust, cptime):
    '''two checkpoints - moved after'''
    cp.newCheckpoint(share, cptime, {'from': accounts[0]})
    cp.newCheckpoint(share, cptime + 100, {'from': accounts[0]})
    rpc.sleep(210)
    for i in range(1, 6):
        cust.transferInternal(share, accounts[i], accounts[0], 1000, {'from': accounts[0]})
        assert cp.custodianBalanceAt(share, accounts[i], cust, cptime) == i * 1000
        assert cp.custodianBalanceAt(share, accounts[i], cust, cptime + 100) == i * 1000


def test_two_moved_before_after(cp, share, cust, cptime):
    '''two checkpoints - moved before and after'''
    cp.newCheckpoint(share, cptime, {'from': accounts[0]})
    cp.newCheckpoint(share, cptime + 100, {'from': accounts[0]})
    for i in range(1, 6):
        cust.transferInternal(share, accounts[i], accounts[0], 1000, {'from': accounts[0]})
    rpc.sleep(210)
    for i in range(1, 6):
        cust.transferInternal(share, accounts[0], accounts[i], 1000, {'from': accounts[0]})
        assert cp.custodianBalanceAt(share, accounts[i], cust, cptime) == (i - 1) * 1000
        assert cp.custodianBalanceAt(share, accounts[i], cust, cptime + 100) == (i - 1) * 1000


def test_two_moved_before_in_between_after(cp, share, cust, cptime):
    '''two checkpoints - moved before, in between, after'''
    cp.newCheckpoint(share, cptime, {'from': accounts[0]})
    cp.newCheckpoint(share, cptime + 100, {'from': accounts[0]})
    for i in range(1, 6):
        cust.transferInternal(share, accounts[i], accounts[0], 1000, {'from': accounts[0]})
    rpc.sleep(110)
    for i in range(1, 6):
        cust.transferInternal(share, accounts[0], accounts[i], 1000, {'from': accounts[0]})
    rpc.sleep(110)
    for i in range(1, 6):
        cust.transferInternal(share, accounts[i], accounts[0], 1000, {'from': accounts[0]})
        assert cp.custodianBalanceAt(share, accounts[i], cust, cptime) == (i - 1) * 1000
        assert cp.custodianBalanceAt(share, accounts[i], cust, cptime + 100) == i * 1000


def test_three_checkpoints(cp, share, cust, cptime):
    '''check balances - three checkpoints'''
    cp.newCheckpoint(share, cptime, {'from': accounts[0]})
    cp.newCheckpoint(share, cptime + 100, {'from': accounts[0]})
    cp.newCheckpoint(share, cptime + 200, {'from': accounts[0]})
    rpc.sleep(110)
    for i in range(1, 6):
        assert cp.custodianBalanceAt(share, accounts[i], cust, cptime) == i * 1000
    rpc.sleep(110)
    for i in range(1, 6):
        assert cp.custodianBalanceAt(share, accounts[i], cust, cptime) == i * 1000
        assert cp.custodianBalanceAt(share, accounts[i], cust, cptime + 100) == i * 1000
    rpc.sleep(110)
    for i in range(1, 6):
        assert cp.custodianBalanceAt(share, accounts[i], cust, cptime) == i * 1000
        assert cp.custodianBalanceAt(share, accounts[i], cust, cptime + 100) == i * 1000
        assert cp.custodianBalanceAt(share, accounts[i], cust, cptime + 200) == i * 1000


def test_three_before(cp, share, cust, cptime):
    '''three checkpoints - moved before'''
    cp.newCheckpoint(share, cptime, {'from': accounts[0]})
    cp.newCheckpoint(share, cptime + 100, {'from': accounts[0]})
    cp.newCheckpoint(share, cptime + 200, {'from': accounts[0]})
    for i in range(1, 6):
        cust.transferInternal(share, accounts[i], accounts[0], 1000, {'from': accounts[0]})
    rpc.sleep(310)
    for i in range(1, 6):
        assert cp.custodianBalanceAt(share, accounts[i], cust, cptime) == (i - 1) * 1000
        assert cp.custodianBalanceAt(share, accounts[i], cust, cptime + 100) == (i - 1) * 1000
        assert cp.custodianBalanceAt(share, accounts[i], cust, cptime + 200) == (i - 1) * 1000


def test_three_after(cp, share, cust, cptime):
    '''three checkpoints - moved after'''
    cp.newCheckpoint(share, cptime, {'from': accounts[0]})
    cp.newCheckpoint(share, cptime + 100, {'from': accounts[0]})
    cp.newCheckpoint(share, cptime + 200, {'from': accounts[0]})
    rpc.sleep(310)
    for i in range(1, 6):
        cust.transferInternal(share, accounts[i], accounts[0], 1000, {'from': accounts[0]})
        assert cp.custodianBalanceAt(share, accounts[i], cust, cptime) == i * 1000
        assert cp.custodianBalanceAt(share, accounts[i], cust, cptime + 100) == i * 1000
        assert cp.custodianBalanceAt(share, accounts[i], cust, cptime + 200) == i * 1000


def test_three_between_first_second(cp, share, cust, cptime):
    '''three checkpoints - moved between first and second'''
    cp.newCheckpoint(share, cptime, {'from': accounts[0]})
    cp.newCheckpoint(share, cptime + 100, {'from': accounts[0]})
    cp.newCheckpoint(share, cptime + 200, {'from': accounts[0]})
    rpc.sleep(110)
    for i in range(1, 6):
        cust.transferInternal(share, accounts[i], accounts[0], 1000, {'from': accounts[0]})
    rpc.sleep(210)
    for i in range(1, 6):
        assert cp.custodianBalanceAt(share, accounts[i], cust, cptime) == i * 1000
        assert cp.custodianBalanceAt(share, accounts[i], cust, cptime + 100) == (i - 1) * 1000
        assert cp.custodianBalanceAt(share, accounts[i], cust, cptime + 200) == (i - 1) * 1000


def test_three_between_second_third(cp, share, cust, cptime):
    '''three checkpoints - moved between second and third'''
    cp.newCheckpoint(share, cptime, {'from': accounts[0]})
    cp.newCheckpoint(share, cptime + 100, {'from': accounts[0]})
    cp.newCheckpoint(share, cptime + 200, {'from': accounts[0]})
    rpc.sleep(210)
    for i in range(1, 6):
        cust.transferInternal(share, accounts[i], accounts[0], 1000, {'from': accounts[0]})
    rpc.sleep(110)
    for i in range(1, 6):
        assert cp.custodianBalanceAt(share, accounts[i], cust, cptime) == i * 1000
        assert cp.custodianBalanceAt(share, accounts[i], cust, cptime + 100) == i * 1000
        assert cp.custodianBalanceAt(share, accounts[i], cust, cptime + 200) == (i - 1) * 1000


def test_three_between(cp, share, cust, cptime):
    '''three checkpoints - moved in between'''
    cp.newCheckpoint(share, cptime, {'from': accounts[0]})
    cp.newCheckpoint(share, cptime + 100, {'from': accounts[0]})
    cp.newCheckpoint(share, cptime + 200, {'from': accounts[0]})
    rpc.sleep(110)
    for i in range(1, 6):
        cust.transferInternal(share, accounts[i], accounts[0], 1000, {'from': accounts[0]})
    rpc.sleep(110)
    for i in range(1, 6):
        cust.transferInternal(share, accounts[0], accounts[i], 1000, {'from': accounts[0]})
    rpc.sleep(110)
    for i in range(1, 6):
        assert cp.custodianBalanceAt(share, accounts[i], cust, cptime) == i * 1000
        assert cp.custodianBalanceAt(share, accounts[i], cust, cptime + 100) == (i - 1) * 1000
        assert cp.custodianBalanceAt(share, accounts[i], cust, cptime + 200) == i * 1000


def test_three_before_after(cp, share, cust, cptime):
    '''three checkpoints - moved before and after'''
    cp.newCheckpoint(share, cptime, {'from': accounts[0]})
    cp.newCheckpoint(share, cptime + 100, {'from': accounts[0]})
    cp.newCheckpoint(share, cptime + 200, {'from': accounts[0]})
    for i in range(1, 6):
        cust.transferInternal(share, accounts[i], accounts[0], 1000, {'from': accounts[0]})
    rpc.sleep(310)
    for i in range(1, 6):
        cust.transferInternal(share, accounts[0], accounts[i], 1000, {'from': accounts[0]})
        assert cp.custodianBalanceAt(share, accounts[i], cust, cptime) == (i - 1) * 1000
        assert cp.custodianBalanceAt(share, accounts[i], cust, cptime + 100) == (i - 1) * 1000
        assert cp.custodianBalanceAt(share, accounts[i], cust, cptime + 200) == (i - 1) * 1000


def test_three_before_in_betwee_after(cp, share, cust, cptime):
    '''three checkpoints - moved before, in between, after'''
    cp.newCheckpoint(share, cptime, {'from': accounts[0]})
    cp.newCheckpoint(share, cptime + 100, {'from': accounts[0]})
    cp.newCheckpoint(share, cptime + 200, {'from': accounts[0]})
    for i in range(1, 6):
        cust.transferInternal(share, accounts[i], accounts[0], 1000, {'from': accounts[0]})
    rpc.sleep(110)
    for i in range(1, 6):
        cust.transferInternal(share, accounts[0], accounts[i], 1000, {'from': accounts[0]})
    rpc.sleep(110)
    for i in range(1, 6):
        cust.transferInternal(share, accounts[i], accounts[0], 1000, {'from': accounts[0]})
    rpc.sleep(110)
    for i in range(1, 6):
        cust.transferInternal(share, accounts[0], accounts[i], 1000, {'from': accounts[0]})
        assert cp.custodianBalanceAt(share, accounts[i], cust, cptime) == (i - 1) * 1000
        assert cp.custodianBalanceAt(share, accounts[i], cust, cptime + 100) == i * 1000
        assert cp.custodianBalanceAt(share, accounts[i], cust, cptime + 200) == (i - 1) * 1000
