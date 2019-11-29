#!/usr/bin/python3

from brownie import accounts

zero = "0x0000000000000000000000000000000000000000"


def test_add_tags_via_mint(approve_many, nft):
    '''Add tags through minting'''
    nft.mint(accounts[1], 1000, 0, "0x0100", {'from': accounts[0]})
    nft.mint(accounts[2], 1000, 0, "0x0002", {'from': accounts[0]})
    nft.mint(accounts[3], 1000, 0, "0xff33", {'from': accounts[0]})
    nft.mint(accounts[4], 1000, 0, "0x0123", {'from': accounts[0]})
    assert nft.getRange(1) == (accounts[1], 1, 1001, 0, "0x0100", zero)
    assert nft.getRange(1001) == (accounts[2], 1001, 2001, 0, "0x0002", zero)
    assert nft.getRange(2001) == (accounts[3], 2001, 3001, 0, "0xff33", zero)
    assert nft.getRange(3001) == (accounts[4], 3001, 4001, 0, "0x0123", zero)
