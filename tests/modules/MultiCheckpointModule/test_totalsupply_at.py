#!/usr/bin/python3

import pytest

from brownie import accounts, rpc


def _sleep(seconds):
    rpc.sleep(seconds)
    rpc.mine()


@pytest.fixture(scope="module", autouse=True)
def setup(id1, share):
    share.mint(accounts[1], 100000, {"from": accounts[0]})


def test_check_balances(cp, share, cptime):
    """check totalSupply"""
    cp.newCheckpoint(share, cptime, {"from": accounts[0]})
    _sleep(110)
    assert cp.totalSupplyAt(share, cptime) == 100000


def test_mint_before(cp, share, cptime):
    """minted before checkpoint"""
    cp.newCheckpoint(share, cptime, {"from": accounts[0]})
    share.mint(accounts[1], 100000, {"from": accounts[0]})
    _sleep(110)
    assert cp.totalSupplyAt(share, cptime) == 200000


def test_mint_after(cp, share, cptime):
    """minted after checkpoint"""
    cp.newCheckpoint(share, cptime, {"from": accounts[0]})
    _sleep(110)
    share.mint(accounts[1], 100000, {"from": accounts[0]})
    assert cp.totalSupplyAt(share, cptime) == 100000


def test_mint_before_after(cp, share, cptime):
    """minted before and after checkpoint"""
    cp.newCheckpoint(share, cptime, {"from": accounts[0]})
    share.mint(accounts[1], 100000, {"from": accounts[0]})
    _sleep(110)
    share.mint(accounts[1], 100000, {"from": accounts[0]})
    assert cp.totalSupplyAt(share, cptime) == 200000


def test_two_checkpoints(cp, share, cptime):
    """check totalSupply - two checkpoints"""
    cp.newCheckpoint(share, cptime, {"from": accounts[0]})
    cp.newCheckpoint(share, cptime + 100, {"from": accounts[0]})
    _sleep(110)
    assert cp.totalSupplyAt(share, cptime) == 100000
    _sleep(110)
    assert cp.totalSupplyAt(share, cptime) == 100000
    assert cp.totalSupplyAt(share, cptime + 100) == 100000


def test_two_mint_before(cp, share, cptime):
    """two checkpoints - mint before"""
    cp.newCheckpoint(share, cptime, {"from": accounts[0]})
    cp.newCheckpoint(share, cptime + 100, {"from": accounts[0]})
    share.mint(accounts[1], 100000, {"from": accounts[0]})
    _sleep(110)
    assert cp.totalSupplyAt(share, cptime) == 200000
    _sleep(110)
    assert cp.totalSupplyAt(share, cptime) == 200000
    assert cp.totalSupplyAt(share, cptime + 100) == 200000


def test_two_mint_in_between(cp, share, cptime):
    """two checkpoints - mint in between"""
    cp.newCheckpoint(share, cptime, {"from": accounts[0]})
    cp.newCheckpoint(share, cptime + 100, {"from": accounts[0]})
    _sleep(110)
    assert cp.totalSupplyAt(share, cptime) == 100000
    share.mint(accounts[1], 100000, {"from": accounts[0]})
    _sleep(110)
    assert cp.totalSupplyAt(share, cptime) == 100000
    assert cp.totalSupplyAt(share, cptime + 100) == 200000


def test_two_mint_after(cp, share, cptime):
    """two checkpoints - mint after"""
    cp.newCheckpoint(share, cptime, {"from": accounts[0]})
    cp.newCheckpoint(share, cptime + 100, {"from": accounts[0]})
    _sleep(110)
    assert cp.totalSupplyAt(share, cptime) == 100000
    _sleep(110)
    share.mint(accounts[1], 100000, {"from": accounts[0]})
    assert cp.totalSupplyAt(share, cptime) == 100000
    assert cp.totalSupplyAt(share, cptime + 100) == 100000


def test_two_mint_before_after(cp, share, cptime):
    """two checkpoints - mint before and after"""
    cp.newCheckpoint(share, cptime, {"from": accounts[0]})
    cp.newCheckpoint(share, cptime + 100, {"from": accounts[0]})
    share.mint(accounts[1], 100000, {"from": accounts[0]})
    _sleep(110)
    assert cp.totalSupplyAt(share, cptime) == 200000
    _sleep(110)
    share.mint(accounts[1], 100000, {"from": accounts[0]})
    assert cp.totalSupplyAt(share, cptime) == 200000
    assert cp.totalSupplyAt(share, cptime + 100) == 200000


def test_two_mint_before_inbetween_after(cp, share, cptime):
    """two checkpoints - mint before, in between, after"""
    cp.newCheckpoint(share, cptime, {"from": accounts[0]})
    cp.newCheckpoint(share, cptime + 100, {"from": accounts[0]})
    share.mint(accounts[1], 100000, {"from": accounts[0]})
    _sleep(110)
    assert cp.totalSupplyAt(share, cptime) == 200000
    share.mint(accounts[1], 100000, {"from": accounts[0]})
    _sleep(110)
    share.mint(accounts[1], 100000, {"from": accounts[0]})
    assert cp.totalSupplyAt(share, cptime) == 200000
    assert cp.totalSupplyAt(share, cptime + 100) == 300000


def test_three_checkpoints(cp, share, cptime):
    """check totalSupply - two checkpoints"""
    cp.newCheckpoint(share, cptime, {"from": accounts[0]})
    cp.newCheckpoint(share, cptime + 100, {"from": accounts[0]})
    cp.newCheckpoint(share, cptime + 200, {"from": accounts[0]})
    _sleep(110)
    assert cp.totalSupplyAt(share, cptime) == 100000
    _sleep(110)
    assert cp.totalSupplyAt(share, cptime) == 100000
    assert cp.totalSupplyAt(share, cptime + 100) == 100000
    _sleep(110)
    assert cp.totalSupplyAt(share, cptime) == 100000
    assert cp.totalSupplyAt(share, cptime + 100) == 100000
    assert cp.totalSupplyAt(share, cptime + 200) == 100000


def test_three_before(cp, share, cptime):
    """three checkpoints - mint before"""
    cp.newCheckpoint(share, cptime, {"from": accounts[0]})
    cp.newCheckpoint(share, cptime + 100, {"from": accounts[0]})
    cp.newCheckpoint(share, cptime + 200, {"from": accounts[0]})
    share.mint(accounts[1], 100000, {"from": accounts[0]})
    _sleep(310)
    assert cp.totalSupplyAt(share, cptime) == 200000
    assert cp.totalSupplyAt(share, cptime + 100) == 200000
    assert cp.totalSupplyAt(share, cptime + 200) == 200000


def test_three_after(cp, share, cptime):
    """three checkpoints - mint after"""
    cp.newCheckpoint(share, cptime, {"from": accounts[0]})
    cp.newCheckpoint(share, cptime + 100, {"from": accounts[0]})
    cp.newCheckpoint(share, cptime + 200, {"from": accounts[0]})
    _sleep(310)
    share.mint(accounts[1], 100000, {"from": accounts[0]})
    assert cp.totalSupplyAt(share, cptime) == 100000
    assert cp.totalSupplyAt(share, cptime + 100) == 100000
    assert cp.totalSupplyAt(share, cptime + 200) == 100000


def test_three_between_first_second(cp, share, cptime):
    """three checkpoints - mint between first and second"""
    cp.newCheckpoint(share, cptime, {"from": accounts[0]})
    cp.newCheckpoint(share, cptime + 100, {"from": accounts[0]})
    cp.newCheckpoint(share, cptime + 200, {"from": accounts[0]})
    _sleep(110)
    share.mint(accounts[1], 100000, {"from": accounts[0]})
    _sleep(210)
    assert cp.totalSupplyAt(share, cptime) == 100000
    assert cp.totalSupplyAt(share, cptime + 100) == 200000
    assert cp.totalSupplyAt(share, cptime + 200) == 200000


def test_three_between_second_third(cp, share, cptime):
    """three checkpoints - mint between second and third"""
    cp.newCheckpoint(share, cptime, {"from": accounts[0]})
    cp.newCheckpoint(share, cptime + 100, {"from": accounts[0]})
    cp.newCheckpoint(share, cptime + 200, {"from": accounts[0]})
    _sleep(210)
    share.mint(accounts[1], 100000, {"from": accounts[0]})
    _sleep(110)
    assert cp.totalSupplyAt(share, cptime) == 100000
    assert cp.totalSupplyAt(share, cptime + 100) == 100000
    assert cp.totalSupplyAt(share, cptime + 200) == 200000


def test_three_between(cp, share, cptime):
    """three checkpoints - mint in between"""
    cp.newCheckpoint(share, cptime, {"from": accounts[0]})
    cp.newCheckpoint(share, cptime + 100, {"from": accounts[0]})
    cp.newCheckpoint(share, cptime + 200, {"from": accounts[0]})
    _sleep(110)
    share.mint(accounts[1], 100000, {"from": accounts[0]})
    _sleep(110)
    share.mint(accounts[1], 100000, {"from": accounts[0]})
    _sleep(110)
    assert cp.totalSupplyAt(share, cptime) == 100000
    assert cp.totalSupplyAt(share, cptime + 100) == 200000
    assert cp.totalSupplyAt(share, cptime + 200) == 300000


def test_three_before_after(cp, share, cptime):
    """three checkpoints - mint before and after"""
    cp.newCheckpoint(share, cptime, {"from": accounts[0]})
    cp.newCheckpoint(share, cptime + 100, {"from": accounts[0]})
    cp.newCheckpoint(share, cptime + 200, {"from": accounts[0]})
    share.mint(accounts[1], 100000, {"from": accounts[0]})
    _sleep(310)
    share.mint(accounts[1], 100000, {"from": accounts[0]})
    assert cp.totalSupplyAt(share, cptime) == 200000
    assert cp.totalSupplyAt(share, cptime + 100) == 200000
    assert cp.totalSupplyAt(share, cptime + 200) == 200000


def test_three_before_in_betwee_after(cp, share, cptime):
    """three checkpoints - moved before, in between, after"""
    cp.newCheckpoint(share, cptime, {"from": accounts[0]})
    cp.newCheckpoint(share, cptime + 100, {"from": accounts[0]})
    cp.newCheckpoint(share, cptime + 200, {"from": accounts[0]})
    share.mint(accounts[1], 100000, {"from": accounts[0]})
    _sleep(110)
    share.mint(accounts[1], 100000, {"from": accounts[0]})
    _sleep(110)
    share.mint(accounts[1], 100000, {"from": accounts[0]})
    _sleep(110)
    share.mint(accounts[1], 100000, {"from": accounts[0]})
    assert cp.totalSupplyAt(share, cptime) == 200000
    assert cp.totalSupplyAt(share, cptime + 100) == 300000
    assert cp.totalSupplyAt(share, cptime + 200) == 400000
