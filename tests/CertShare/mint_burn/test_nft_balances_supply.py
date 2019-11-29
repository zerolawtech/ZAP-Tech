#!/usr/bin/python3

from brownie import accounts


def test_mint_to_org(approve_many, org, nft):
    '''mint to org'''
    nft.mint(org, 1000, 0, "0x00", {'from': accounts[0]})
    assert nft.totalSupply() == 1000
    assert nft.balanceOf(org), 1000
    nft.mint(org, 2000, 0, "0x00", {'from': accounts[0]})
    assert nft.totalSupply() == 3000
    assert nft.balanceOf(org) == 3000


def test_mint_to_members(nft):
    '''mint to members'''
    nft.mint(accounts[1], 1000, 0, "0x00", {'from': accounts[0]})
    assert nft.totalSupply() == 1000
    assert nft.balanceOf(accounts[1]) == 1000
    nft.mint(accounts[2], 2000, 0, "0x00", {'from': accounts[0]})
    assert nft.totalSupply() == 3000
    assert nft.balanceOf(accounts[1]) == 1000
    assert nft.balanceOf(accounts[2]) == 2000
    nft.mint(accounts[1], 3000, 0, "0x00", {'from': accounts[0]})
    assert nft.totalSupply() == 6000
    assert nft.balanceOf(accounts[1]) == 4000
    assert nft.balanceOf(accounts[2]) == 2000
    nft.mint(accounts[2], 4000, 0, "0x00", {'from': accounts[0]})
    assert nft.totalSupply() == 10000
    assert nft.balanceOf(accounts[1]) == 4000
    assert nft.balanceOf(accounts[2]) == 6000


def test_burn_from_org(org, nft):
    '''burn from org'''
    nft.mint(org, 10000, 0, "0x00", {'from': accounts[0]})
    nft.burn(1, 1001, {'from': accounts[0]})
    assert nft.totalSupply() == 9000
    assert nft.balanceOf(org) == 9000
    nft.burn(1001, 5001, {'from': accounts[0]})
    assert nft.totalSupply() == 5000
    assert nft.balanceOf(org) == 5000
    nft.burn(5001, 10001, {'from': accounts[0]})
    assert nft.totalSupply() == 0
    assert nft.balanceOf(org) == 0


def test_burn_from_members(nft):
    '''burn from members'''
    nft.mint(accounts[1], 5000, 0, "0x00", {'from': accounts[0]})
    nft.mint(accounts[2], 10000, 0, "0x00", {'from': accounts[0]})
    nft.burn(3001, 5001, {'from': accounts[0]})
    assert nft.totalSupply() == 13000
    assert nft.balanceOf(accounts[1]) == 3000
    assert nft.balanceOf(accounts[2]) == 10000
    nft.burn(5001, 8001, {'from': accounts[0]})
    assert nft.totalSupply() == 10000
    assert nft.balanceOf(accounts[1]) == 3000
    assert nft.balanceOf(accounts[2]) == 7000
    nft.burn(1, 3001, {'from': accounts[0]})
    assert nft.totalSupply() == 7000
    assert nft.balanceOf(accounts[1]) == 0
    assert nft.balanceOf(accounts[2]) == 7000
    nft.burn(8001, 15001, {'from': accounts[0]})
    assert nft.totalSupply() == 0
    assert nft.balanceOf(accounts[1]) == 0
    assert nft.balanceOf(accounts[2]) == 0


def test_authorized_supply(nft):
    '''modify authorized supply'''
    nft.modifyAuthorizedSupply(10000, {'from': accounts[0]})
    assert nft.authorizedSupply() == 10000
    assert nft.totalSupply() == 0
    nft.modifyAuthorizedSupply(0, {'from': accounts[0]})
    assert nft.authorizedSupply() == 0
    assert nft.totalSupply() == 0
    nft.modifyAuthorizedSupply(1234567, {'from': accounts[0]})
    assert nft.authorizedSupply() == 1234567
    assert nft.totalSupply() == 0
    nft.modifyAuthorizedSupply(2400000000, {'from': accounts[0]})
    assert nft.authorizedSupply() == 2400000000
    assert nft.totalSupply() == 0


def test_mint_zero(org, nft):
    '''mint, burn, mint'''
    nft.mint(org, 10000, 0, "0x00", {'from': accounts[0]})
    assert nft.totalSupply() == 10000
    nft.burn(1, 10001, {'from': accounts[0]})
    assert nft.totalSupply() == 0
    nft.mint(org, 10000, 0, "0x00", {'from': accounts[0]})
    assert nft.totalSupply() == 10000
    assert nft.rangesOf(org) == ((10001, 20001,),)
    assert nft.getRange(1)[0] == '0x0000000000000000000000000000000000000000'
