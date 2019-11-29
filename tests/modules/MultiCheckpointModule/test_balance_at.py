#!/usr/bin/python3

import pytest

from brownie import accounts, rpc


@pytest.fixture(scope="module", autouse=True)
def setup(approve_many, share):
    for i in range(1, 6):
        share.mint(accounts[i], 1000 * i, {'from': accounts[0]})


def test_check_balances(cp, share, cptime):
    '''check balances'''
    cp.newCheckpoint(share, cptime, {'from': accounts[0]})
    rpc.sleep(110)
    for i in range(1, 6):
        assert cp.balanceAt(share, accounts[i], cptime) == i * 1000


def test_moved_before(cp, share, cptime):
    '''moved before checkpoint'''
    cp.newCheckpoint(share, cptime, {'from': accounts[0]})
    for i in range(1, 6):
        share.transfer(accounts[0], 1000, {'from': accounts[i]})
    rpc.sleep(110)
    for i in range(1, 6):
        assert cp.balanceAt(share, accounts[i], cptime) == (i - 1) * 1000


def test_moved_after(cp, share, cptime):
    '''moved after checkpoint'''
    cp.newCheckpoint(share, cptime, {'from': accounts[0]})
    rpc.sleep(110)
    for i in range(1, 6):
        assert cp.balanceAt(share, accounts[i], cptime) == i * 1000
        share.transfer(accounts[0], 1000, {'from': accounts[i]})
        assert cp.balanceAt(share, accounts[i], cptime) == i * 1000


def test_moved_before_after(cp, share, cptime):
    '''moved before and after checkpoint'''
    cp.newCheckpoint(share, cptime, {'from': accounts[0]})
    for i in range(1, 6):
        share.transfer(accounts[0], 1000, {'from': accounts[i]})
    rpc.sleep(110)
    for i in range(1, 6):
        assert cp.balanceAt(share, accounts[i], cptime) == (i - 1) * 1000
        share.transfer(accounts[i], 1000, {'from': accounts[0]})
        assert cp.balanceAt(share, accounts[i], cptime) == (i - 1) * 1000


def test_two_checkpoints(cp, share, cptime):
    '''check balances - two checkpoints'''
    cp.newCheckpoint(share, cptime, {'from': accounts[0]})
    cp.newCheckpoint(share, cptime + 100, {'from': accounts[0]})
    rpc.sleep(110)
    for i in range(1, 6):
        assert cp.balanceAt(share, accounts[i], cptime) == i * 1000
    rpc.sleep(110)
    for i in range(1, 6):
        assert cp.balanceAt(share, accounts[i], cptime) == i * 1000
        assert cp.balanceAt(share, accounts[i], cptime + 100) == i * 1000


def test_two_moved_before(cp, share, cptime):
    '''two checkpoints - moved before'''
    cp.newCheckpoint(share, cptime, {'from': accounts[0]})
    cp.newCheckpoint(share, cptime + 100, {'from': accounts[0]})
    for i in range(1, 6):
        share.transfer(accounts[0], 1000, {'from': accounts[i]})
    rpc.sleep(110)
    for i in range(1, 6):
        assert cp.balanceAt(share, accounts[i], cptime) == (i - 1) * 1000
    rpc.sleep(110)
    for i in range(1, 6):
        assert cp.balanceAt(share, accounts[i], cptime) == (i - 1) * 1000
        assert cp.balanceAt(share, accounts[i], cptime + 100) == (i - 1) * 1000


def test_two_moved_in_between(cp, share, cptime):
    '''two checkpoints - moved in between'''
    cp.newCheckpoint(share, cptime, {'from': accounts[0]})
    cp.newCheckpoint(share, cptime + 100, {'from': accounts[0]})
    rpc.sleep(110)
    for i in range(1, 6):
        share.transfer(accounts[0], 1000, {'from': accounts[i]})
    rpc.sleep(110)
    for i in range(1, 6):
        assert cp.balanceAt(share, accounts[i], cptime) == i * 1000
        assert cp.balanceAt(share, accounts[i], cptime + 100) == (i - 1) * 1000


def test_two_moved_after(cp, share, cptime):
    '''two checkpoints - moved after'''
    cp.newCheckpoint(share, cptime, {'from': accounts[0]})
    cp.newCheckpoint(share, cptime + 100, {'from': accounts[0]})
    rpc.sleep(210)
    for i in range(1, 6):
        share.transfer(accounts[0], 1000, {'from': accounts[i]})
        assert cp.balanceAt(share, accounts[i], cptime) == i * 1000
        assert cp.balanceAt(share, accounts[i], cptime + 100) == i * 1000


def test_two_moved_before_after(cp, share, cptime):
    '''two checkpoints - moved before and after'''
    cp.newCheckpoint(share, cptime, {'from': accounts[0]})
    cp.newCheckpoint(share, cptime + 100, {'from': accounts[0]})
    for i in range(1, 6):
        share.transfer(accounts[0], 1000, {'from': accounts[i]})
    rpc.sleep(210)
    for i in range(1, 6):
        share.transfer(accounts[i], 1000, {'from': accounts[0]})
        assert cp.balanceAt(share, accounts[i], cptime) == (i - 1) * 1000
        assert cp.balanceAt(share, accounts[i], cptime + 100) == (i - 1) * 1000


def test_two_moved_before_in_between_after(cp, share, cptime):
    '''two checkpoints - moved before, in between, after'''
    cp.newCheckpoint(share, cptime, {'from': accounts[0]})
    cp.newCheckpoint(share, cptime + 100, {'from': accounts[0]})
    for i in range(1, 6):
        share.transfer(accounts[0], 1000, {'from': accounts[i]})
    rpc.sleep(110)
    for i in range(1, 6):
        share.transfer(accounts[i], 1000, {'from': accounts[0]})
    rpc.sleep(110)
    for i in range(1, 6):
        share.transfer(accounts[0], 1000, {'from': accounts[i]})
        assert cp.balanceAt(share, accounts[i], cptime) == (i - 1) * 1000
        assert cp.balanceAt(share, accounts[i], cptime + 100) == i * 1000


def test_three_checkpoints(cp, share, cptime):
    '''check balances - three checkpoints'''
    cp.newCheckpoint(share, cptime, {'from': accounts[0]})
    cp.newCheckpoint(share, cptime + 100, {'from': accounts[0]})
    cp.newCheckpoint(share, cptime + 200, {'from': accounts[0]})
    rpc.sleep(110)
    for i in range(1, 6):
        assert cp.balanceAt(share, accounts[i], cptime) == i * 1000
    rpc.sleep(110)
    for i in range(1, 6):
        assert cp.balanceAt(share, accounts[i], cptime) == i * 1000
        assert cp.balanceAt(share, accounts[i], cptime + 100) == i * 1000
    rpc.sleep(110)
    for i in range(1, 6):
        assert cp.balanceAt(share, accounts[i], cptime) == i * 1000
        assert cp.balanceAt(share, accounts[i], cptime + 100) == i * 1000
        assert cp.balanceAt(share, accounts[i], cptime + 200) == i * 1000


def test_three_before(cp, share, cptime):
    '''three checkpoints - moved before'''
    cp.newCheckpoint(share, cptime, {'from': accounts[0]})
    cp.newCheckpoint(share, cptime + 100, {'from': accounts[0]})
    cp.newCheckpoint(share, cptime + 200, {'from': accounts[0]})
    for i in range(1, 6):
        share.transfer(accounts[0], 1000, {'from': accounts[i]})
    rpc.sleep(310)
    for i in range(1, 6):
        assert cp.balanceAt(share, accounts[i], cptime) == (i - 1) * 1000
        assert cp.balanceAt(share, accounts[i], cptime + 100) == (i - 1) * 1000
        assert cp.balanceAt(share, accounts[i], cptime + 200) == (i - 1) * 1000


def test_three_after(cp, share, cptime):
    '''three checkpoints - moved after'''
    cp.newCheckpoint(share, cptime, {'from': accounts[0]})
    cp.newCheckpoint(share, cptime + 100, {'from': accounts[0]})
    cp.newCheckpoint(share, cptime + 200, {'from': accounts[0]})
    rpc.sleep(310)
    for i in range(1, 6):
        share.transfer(accounts[0], 1000, {'from': accounts[i]})
        assert cp.balanceAt(share, accounts[i], cptime) == i * 1000
        assert cp.balanceAt(share, accounts[i], cptime + 100) == i * 1000
        assert cp.balanceAt(share, accounts[i], cptime + 200) == i * 1000


def test_three_between_first_second(cp, share, cptime):
    '''three checkpoints - moved between first and second'''
    cp.newCheckpoint(share, cptime, {'from': accounts[0]})
    cp.newCheckpoint(share, cptime + 100, {'from': accounts[0]})
    cp.newCheckpoint(share, cptime + 200, {'from': accounts[0]})
    rpc.sleep(110)
    for i in range(1, 6):
        share.transfer(accounts[0], 1000, {'from': accounts[i]})
    rpc.sleep(210)
    for i in range(1, 6):
        assert cp.balanceAt(share, accounts[i], cptime) == i * 1000
        assert cp.balanceAt(share, accounts[i], cptime + 100) == (i - 1) * 1000
        assert cp.balanceAt(share, accounts[i], cptime + 200) == (i - 1) * 1000


def test_three_between_second_third(cp, share, cptime):
    '''three checkpoints - moved between second and third'''
    cp.newCheckpoint(share, cptime, {'from': accounts[0]})
    cp.newCheckpoint(share, cptime + 100, {'from': accounts[0]})
    cp.newCheckpoint(share, cptime + 200, {'from': accounts[0]})
    rpc.sleep(210)
    for i in range(1, 6):
        share.transfer(accounts[0], 1000, {'from': accounts[i]})
    rpc.sleep(110)
    for i in range(1, 6):
        assert cp.balanceAt(share, accounts[i], cptime) == i * 1000
        assert cp.balanceAt(share, accounts[i], cptime + 100) == i * 1000
        assert cp.balanceAt(share, accounts[i], cptime + 200) == (i - 1) * 1000


def test_three_between(cp, share, cptime):
    '''three checkpoints - moved in between'''
    cp.newCheckpoint(share, cptime, {'from': accounts[0]})
    cp.newCheckpoint(share, cptime + 100, {'from': accounts[0]})
    cp.newCheckpoint(share, cptime + 200, {'from': accounts[0]})
    rpc.sleep(110)
    for i in range(1, 6):
        share.transfer(accounts[0], 1000, {'from': accounts[i]})
    rpc.sleep(110)
    for i in range(1, 6):
        share.transfer(accounts[i], 1000, {'from': accounts[0]})
    rpc.sleep(110)
    for i in range(1, 6):
        assert cp.balanceAt(share, accounts[i], cptime) == i * 1000
        assert cp.balanceAt(share, accounts[i], cptime + 100) == (i - 1) * 1000
        assert cp.balanceAt(share, accounts[i], cptime + 200) == i * 1000


def test_three_before_after(cp, share, cptime):
    '''three checkpoints - moved before and after'''
    cp.newCheckpoint(share, cptime, {'from': accounts[0]})
    cp.newCheckpoint(share, cptime + 100, {'from': accounts[0]})
    cp.newCheckpoint(share, cptime + 200, {'from': accounts[0]})
    for i in range(1, 6):
        share.transfer(accounts[0], 1000, {'from': accounts[i]})
    rpc.sleep(310)
    for i in range(1, 6):
        share.transfer(accounts[i], 1000, {'from': accounts[0]})
        assert cp.balanceAt(share, accounts[i], cptime) == (i - 1) * 1000
        assert cp.balanceAt(share, accounts[i], cptime + 100) == (i - 1) * 1000
        assert cp.balanceAt(share, accounts[i], cptime + 200) == (i - 1) * 1000


def test_three_before_in_betwee_after(cp, share, cptime):
    '''three checkpoints - moved before, in between, after'''
    cp.newCheckpoint(share, cptime, {'from': accounts[0]})
    cp.newCheckpoint(share, cptime + 100, {'from': accounts[0]})
    cp.newCheckpoint(share, cptime + 200, {'from': accounts[0]})
    for i in range(1, 6):
        share.transfer(accounts[0], 1000, {'from': accounts[i]})
    rpc.sleep(110)
    for i in range(1, 6):
        share.transfer(accounts[i], 1000, {'from': accounts[0]})
    rpc.sleep(110)
    for i in range(1, 6):
        share.transfer(accounts[0], 1000, {'from': accounts[i]})
    rpc.sleep(110)
    for i in range(1, 6):
        share.transfer(accounts[i], 1000, {'from': accounts[0]})
        assert cp.balanceAt(share, accounts[i], cptime) == (i - 1) * 1000
        assert cp.balanceAt(share, accounts[i], cptime + 100) == i * 1000
        assert cp.balanceAt(share, accounts[i], cptime + 200) == (i - 1) * 1000
