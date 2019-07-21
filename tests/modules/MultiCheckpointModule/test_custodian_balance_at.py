#!/usr/bin/python3

import pytest

from brownie import accounts, rpc


@pytest.fixture(scope="module", autouse=True)
def setup(approve_many, token, cust):
    for i in range(1, 6):
        token.mint(accounts[i], 3000 * i, {'from': accounts[0]})
        token.transfer(cust, 1000 * i, {'from': accounts[i]})


def test_check_balances(cp, token, cust, cptime):
    '''check balances'''
    cp.newCheckpoint(token, cptime, {'from': accounts[0]})
    rpc.sleep(110)
    for i in range(1, 6):
        assert cp.custodianBalanceAt(token, accounts[i], cust, cptime) == i * 1000


def test_moved_before(cp, token, cust, cptime):
    '''moved before checkpoint'''
    cp.newCheckpoint(token, cptime, {'from': accounts[0]})
    for i in range(1, 6):
        cust.transferInternal(token, accounts[i], accounts[0], 1000, {'from': accounts[0]})
    rpc.sleep(110)
    for i in range(1, 6):
        assert cp.custodianBalanceAt(token, accounts[i], cust, cptime) == (i - 1) * 1000


def test_moved_after(cp, token, cust, cptime):
    '''moved after checkpoint'''
    cp.newCheckpoint(token, cptime, {'from': accounts[0]})
    rpc.sleep(110)
    for i in range(1, 6):
        assert cp.custodianBalanceAt(token, accounts[i], cust, cptime) == i * 1000
        cust.transferInternal(token, accounts[i], accounts[0], 1000, {'from': accounts[0]})
        assert cp.custodianBalanceAt(token, accounts[i], cust, cptime) == i * 1000


def test_moved_before_after(cp, token, cust, cptime):
    '''moved before and after checkpoint'''
    cp.newCheckpoint(token, cptime, {'from': accounts[0]})
    for i in range(1, 6):
        cust.transferInternal(token, accounts[i], accounts[0], 1000, {'from': accounts[0]})
    rpc.sleep(110)
    for i in range(1, 6):
        assert cp.custodianBalanceAt(token, accounts[i], cust, cptime) == (i - 1) * 1000
        cust.transferInternal(token, accounts[0], accounts[i], 1000, {'from': accounts[0]})
        assert cp.custodianBalanceAt(token, accounts[i], cust, cptime) == (i - 1) * 1000


def test_two_checkpoints(cp, token, cust, cptime):
    '''check balances - two checkpoints'''
    cp.newCheckpoint(token, cptime, {'from': accounts[0]})
    cp.newCheckpoint(token, cptime + 100, {'from': accounts[0]})
    rpc.sleep(110)
    for i in range(1, 6):
        assert cp.custodianBalanceAt(token, accounts[i], cust, cptime) == i * 1000
    rpc.sleep(110)
    for i in range(1, 6):
        assert cp.custodianBalanceAt(token, accounts[i], cust, cptime) == i * 1000
        assert cp.custodianBalanceAt(token, accounts[i], cust, cptime + 100) == i * 1000


def test_two_moved_before(cp, token, cust, cptime):
    '''two checkpoints - moved before'''
    cp.newCheckpoint(token, cptime, {'from': accounts[0]})
    cp.newCheckpoint(token, cptime + 100, {'from': accounts[0]})
    for i in range(1, 6):
        cust.transferInternal(token, accounts[i], accounts[0], 1000, {'from': accounts[0]})
    rpc.sleep(110)
    for i in range(1, 6):
        assert cp.custodianBalanceAt(token, accounts[i], cust, cptime) == (i - 1) * 1000
    rpc.sleep(110)
    for i in range(1, 6):
        assert cp.custodianBalanceAt(token, accounts[i], cust, cptime) == (i - 1) * 1000
        assert cp.custodianBalanceAt(token, accounts[i], cust, cptime + 100) == (i - 1) * 1000


def test_two_moved_in_between(cp, token, cust, cptime):
    '''two checkpoints - moved in between'''
    cp.newCheckpoint(token, cptime, {'from': accounts[0]})
    cp.newCheckpoint(token, cptime + 100, {'from': accounts[0]})
    rpc.sleep(110)
    for i in range(1, 6):
        cust.transferInternal(token, accounts[i], accounts[0], 1000, {'from': accounts[0]})
    rpc.sleep(110)
    for i in range(1, 6):
        assert cp.custodianBalanceAt(token, accounts[i], cust, cptime) == i * 1000
        assert cp.custodianBalanceAt(token, accounts[i], cust, cptime + 100) == (i - 1) * 1000


def test_two_moved_after(cp, token, cust, cptime):
    '''two checkpoints - moved after'''
    cp.newCheckpoint(token, cptime, {'from': accounts[0]})
    cp.newCheckpoint(token, cptime + 100, {'from': accounts[0]})
    rpc.sleep(210)
    for i in range(1, 6):
        cust.transferInternal(token, accounts[i], accounts[0], 1000, {'from': accounts[0]})
        assert cp.custodianBalanceAt(token, accounts[i], cust, cptime) == i * 1000
        assert cp.custodianBalanceAt(token, accounts[i], cust, cptime + 100) == i * 1000


def test_two_moved_before_after(cp, token, cust, cptime):
    '''two checkpoints - moved before and after'''
    cp.newCheckpoint(token, cptime, {'from': accounts[0]})
    cp.newCheckpoint(token, cptime + 100, {'from': accounts[0]})
    for i in range(1, 6):
        cust.transferInternal(token, accounts[i], accounts[0], 1000, {'from': accounts[0]})
    rpc.sleep(210)
    for i in range(1, 6):
        cust.transferInternal(token, accounts[0], accounts[i], 1000, {'from': accounts[0]})
        assert cp.custodianBalanceAt(token, accounts[i], cust, cptime) == (i - 1) * 1000
        assert cp.custodianBalanceAt(token, accounts[i], cust, cptime + 100) == (i - 1) * 1000


def test_two_moved_before_in_between_after(cp, token, cust, cptime):
    '''two checkpoints - moved before, in between, after'''
    cp.newCheckpoint(token, cptime, {'from': accounts[0]})
    cp.newCheckpoint(token, cptime + 100, {'from': accounts[0]})
    for i in range(1, 6):
        cust.transferInternal(token, accounts[i], accounts[0], 1000, {'from': accounts[0]})
    rpc.sleep(110)
    for i in range(1, 6):
        cust.transferInternal(token, accounts[0], accounts[i], 1000, {'from': accounts[0]})
    rpc.sleep(110)
    for i in range(1, 6):
        cust.transferInternal(token, accounts[i], accounts[0], 1000, {'from': accounts[0]})
        assert cp.custodianBalanceAt(token, accounts[i], cust, cptime) == (i - 1) * 1000
        assert cp.custodianBalanceAt(token, accounts[i], cust, cptime + 100) == i * 1000


def test_three_checkpoints(cp, token, cust, cptime):
    '''check balances - three checkpoints'''
    cp.newCheckpoint(token, cptime, {'from': accounts[0]})
    cp.newCheckpoint(token, cptime + 100, {'from': accounts[0]})
    cp.newCheckpoint(token, cptime + 200, {'from': accounts[0]})
    rpc.sleep(110)
    for i in range(1, 6):
        assert cp.custodianBalanceAt(token, accounts[i], cust, cptime) == i * 1000
    rpc.sleep(110)
    for i in range(1, 6):
        assert cp.custodianBalanceAt(token, accounts[i], cust, cptime) == i * 1000
        assert cp.custodianBalanceAt(token, accounts[i], cust, cptime + 100) == i * 1000
    rpc.sleep(110)
    for i in range(1, 6):
        assert cp.custodianBalanceAt(token, accounts[i], cust, cptime) == i * 1000
        assert cp.custodianBalanceAt(token, accounts[i], cust, cptime + 100) == i * 1000
        assert cp.custodianBalanceAt(token, accounts[i], cust, cptime + 200) == i * 1000


def test_three_before(cp, token, cust, cptime):
    '''three checkpoints - moved before'''
    cp.newCheckpoint(token, cptime, {'from': accounts[0]})
    cp.newCheckpoint(token, cptime + 100, {'from': accounts[0]})
    cp.newCheckpoint(token, cptime + 200, {'from': accounts[0]})
    for i in range(1, 6):
        cust.transferInternal(token, accounts[i], accounts[0], 1000, {'from': accounts[0]})
    rpc.sleep(310)
    for i in range(1, 6):
        assert cp.custodianBalanceAt(token, accounts[i], cust, cptime) == (i - 1) * 1000
        assert cp.custodianBalanceAt(token, accounts[i], cust, cptime + 100) == (i - 1) * 1000
        assert cp.custodianBalanceAt(token, accounts[i], cust, cptime + 200) == (i - 1) * 1000


def test_three_after(cp, token, cust, cptime):
    '''three checkpoints - moved after'''
    cp.newCheckpoint(token, cptime, {'from': accounts[0]})
    cp.newCheckpoint(token, cptime + 100, {'from': accounts[0]})
    cp.newCheckpoint(token, cptime + 200, {'from': accounts[0]})
    rpc.sleep(310)
    for i in range(1, 6):
        cust.transferInternal(token, accounts[i], accounts[0], 1000, {'from': accounts[0]})
        assert cp.custodianBalanceAt(token, accounts[i], cust, cptime) == i * 1000
        assert cp.custodianBalanceAt(token, accounts[i], cust, cptime + 100) == i * 1000
        assert cp.custodianBalanceAt(token, accounts[i], cust, cptime + 200) == i * 1000


def test_three_between_first_second(cp, token, cust, cptime):
    '''three checkpoints - moved between first and second'''
    cp.newCheckpoint(token, cptime, {'from': accounts[0]})
    cp.newCheckpoint(token, cptime + 100, {'from': accounts[0]})
    cp.newCheckpoint(token, cptime + 200, {'from': accounts[0]})
    rpc.sleep(110)
    for i in range(1, 6):
        cust.transferInternal(token, accounts[i], accounts[0], 1000, {'from': accounts[0]})
    rpc.sleep(210)
    for i in range(1, 6):
        assert cp.custodianBalanceAt(token, accounts[i], cust, cptime) == i * 1000
        assert cp.custodianBalanceAt(token, accounts[i], cust, cptime + 100) == (i - 1) * 1000
        assert cp.custodianBalanceAt(token, accounts[i], cust, cptime + 200) == (i - 1) * 1000


def test_three_between_second_third(cp, token, cust, cptime):
    '''three checkpoints - moved between second and third'''
    cp.newCheckpoint(token, cptime, {'from': accounts[0]})
    cp.newCheckpoint(token, cptime + 100, {'from': accounts[0]})
    cp.newCheckpoint(token, cptime + 200, {'from': accounts[0]})
    rpc.sleep(210)
    for i in range(1, 6):
        cust.transferInternal(token, accounts[i], accounts[0], 1000, {'from': accounts[0]})
    rpc.sleep(110)
    for i in range(1, 6):
        assert cp.custodianBalanceAt(token, accounts[i], cust, cptime) == i * 1000
        assert cp.custodianBalanceAt(token, accounts[i], cust, cptime + 100) == i * 1000
        assert cp.custodianBalanceAt(token, accounts[i], cust, cptime + 200) == (i - 1) * 1000


def test_three_between(cp, token, cust, cptime):
    '''three checkpoints - moved in between'''
    cp.newCheckpoint(token, cptime, {'from': accounts[0]})
    cp.newCheckpoint(token, cptime + 100, {'from': accounts[0]})
    cp.newCheckpoint(token, cptime + 200, {'from': accounts[0]})
    rpc.sleep(110)
    for i in range(1, 6):
        cust.transferInternal(token, accounts[i], accounts[0], 1000, {'from': accounts[0]})
    rpc.sleep(110)
    for i in range(1, 6):
        cust.transferInternal(token, accounts[0], accounts[i], 1000, {'from': accounts[0]})
    rpc.sleep(110)
    for i in range(1, 6):
        assert cp.custodianBalanceAt(token, accounts[i], cust, cptime) == i * 1000
        assert cp.custodianBalanceAt(token, accounts[i], cust, cptime + 100) == (i - 1) * 1000
        assert cp.custodianBalanceAt(token, accounts[i], cust, cptime + 200) == i * 1000


def test_three_before_after(cp, token, cust, cptime):
    '''three checkpoints - moved before and after'''
    cp.newCheckpoint(token, cptime, {'from': accounts[0]})
    cp.newCheckpoint(token, cptime + 100, {'from': accounts[0]})
    cp.newCheckpoint(token, cptime + 200, {'from': accounts[0]})
    for i in range(1, 6):
        cust.transferInternal(token, accounts[i], accounts[0], 1000, {'from': accounts[0]})
    rpc.sleep(310)
    for i in range(1, 6):
        cust.transferInternal(token, accounts[0], accounts[i], 1000, {'from': accounts[0]})
        assert cp.custodianBalanceAt(token, accounts[i], cust, cptime) == (i - 1) * 1000
        assert cp.custodianBalanceAt(token, accounts[i], cust, cptime + 100) == (i - 1) * 1000
        assert cp.custodianBalanceAt(token, accounts[i], cust, cptime + 200) == (i - 1) * 1000


def test_three_before_in_betwee_after(cp, token, cust, cptime):
    '''three checkpoints - moved before, in between, after'''
    cp.newCheckpoint(token, cptime, {'from': accounts[0]})
    cp.newCheckpoint(token, cptime + 100, {'from': accounts[0]})
    cp.newCheckpoint(token, cptime + 200, {'from': accounts[0]})
    for i in range(1, 6):
        cust.transferInternal(token, accounts[i], accounts[0], 1000, {'from': accounts[0]})
    rpc.sleep(110)
    for i in range(1, 6):
        cust.transferInternal(token, accounts[0], accounts[i], 1000, {'from': accounts[0]})
    rpc.sleep(110)
    for i in range(1, 6):
        cust.transferInternal(token, accounts[i], accounts[0], 1000, {'from': accounts[0]})
    rpc.sleep(110)
    for i in range(1, 6):
        cust.transferInternal(token, accounts[0], accounts[i], 1000, {'from': accounts[0]})
        assert cp.custodianBalanceAt(token, accounts[i], cust, cptime) == (i - 1) * 1000
        assert cp.custodianBalanceAt(token, accounts[i], cust, cptime + 100) == i * 1000
        assert cp.custodianBalanceAt(token, accounts[i], cust, cptime + 200) == (i - 1) * 1000
