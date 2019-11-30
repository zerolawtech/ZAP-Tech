#!/usr/bin/python3

from brownie import accounts


def test_mint_no_merge_owner(nft, approve_many):
    """Mint and do not merge - different owners"""
    nft.mint(accounts[1], 10000, 0, "0x00", {"from": accounts[0]})
    nft.mint(accounts[2], 5000, 0, "0x00", {"from": accounts[0]})
    assert nft.totalSupply() == 15000
    assert nft.balanceOf(accounts[1]) == 10000
    assert nft.balanceOf(accounts[2]) == 5000
    assert nft.rangesOf(accounts[1]) == ((1, 10001),)
    assert nft.rangesOf(accounts[2]) == ((10001, 15001),)


def test_mint_no_merge_tag(nft):
    """Mint and do not merge - different takgs"""
    nft.mint(accounts[1], 10000, 0, "0x00", {"from": accounts[0]})
    nft.mint(accounts[1], 5000, 0, "0x01", {"from": accounts[0]})
    assert nft.totalSupply() == 15000
    assert nft.rangesOf(accounts[1]) == ((1, 10001), (10001, 15001))
    assert nft.balanceOf(accounts[1]) == 15000


def test_mint_merge(nft):
    """Mint and merge range"""
    nft.mint(accounts[1], 10000, 0, "0x00", {"from": accounts[0]})
    nft.mint(accounts[1], 5000, 0, "0x00", {"from": accounts[0]})
    assert nft.totalSupply() == 15000
    assert nft.rangesOf(accounts[1]) == ((1, 15001),)
    assert nft.balanceOf(accounts[1]) == 15000


def test_burn_range(nft):
    """Burn range"""
    nft.mint(accounts[1], 10000, 0, "0x00", {"from": accounts[0]})
    nft.mint(accounts[2], 5000, 0, "0x00", {"from": accounts[0]})
    nft.mint(accounts[1], 5000, 0, "0x00", {"from": accounts[0]})
    assert nft.totalSupply() == 20000
    assert nft.rangesOf(accounts[1]) == ((1, 10001), (15001, 20001))
    assert nft.rangesOf(accounts[2]) == ((10001, 15001),)
    nft.burn(10001, 15001, {"from": accounts[0]})
    assert nft.totalSupply() == 15000
    assert nft.rangesOf(accounts[1]) == ((1, 10001), (15001, 20001))
    assert nft.rangesOf(accounts[2]) == ()
    assert nft.balanceOf(accounts[2]) == 0


def test_burn_all(nft):
    """Burn total supply"""
    nft.mint(accounts[1], 10000, 0, "0x00", {"from": accounts[0]})
    nft.burn(1, 10001, {"from": accounts[0]})
    assert nft.totalSupply() == 0
    assert nft.balanceOf(accounts[1]) == 0
    assert nft.rangesOf(accounts[1]) == ()


def test_burn_inside(nft):
    """Burn inside"""
    nft.mint(accounts[1], 10000, 0, "0x00", {"from": accounts[0]})
    nft.burn(2000, 4000, {"from": accounts[0]})
    assert nft.totalSupply() == 8000
    assert nft.balanceOf(accounts[1]) == 8000
    assert nft.rangesOf(accounts[1]) == ((1, 2000), (4000, 10001))


def test_burn_left(nft):
    """Burn left"""
    nft.mint(accounts[2], 1000, 0, "0x00", {"from": accounts[0]})
    nft.mint(accounts[1], 9000, 0, "0x00", {"from": accounts[0]})
    nft.burn(1001, 5001, {"from": accounts[0]})
    assert nft.totalSupply() == 6000
    assert nft.rangesOf(accounts[1]) == ((5001, 10001),)


def test_burn_right(nft):
    """Burn right"""
    nft.mint(accounts[1], 9000, 0, "0x00", {"from": accounts[0]})
    nft.mint(accounts[2], 1000, 0, "0x00", {"from": accounts[0]})
    nft.burn(5001, 9001)
    assert nft.totalSupply() == 6000
    assert nft.rangesOf(accounts[1]) == ((1, 5001),)


def test_burn_abs_left(nft):
    """Burn absolute left"""
    nft.mint(accounts[1], 10000, 0, "0x00", {"from": accounts[0]})
    nft.burn(1, 5001, {"from": accounts[0]})
    assert nft.totalSupply() == 5000
    assert nft.rangesOf(accounts[1]) == ((5001, 10001),)


def test_burn_abs_right(nft):
    """Burn absolute right"""
    nft.mint(accounts[1], 10000, 0, "0x00", {"from": accounts[0]})
    nft.burn(5001, 10001, {"from": accounts[0]})
    assert nft.totalSupply() == 5000
    assert nft.rangesOf(accounts[1]) == ((1, 5001),)
