#!/usr/bin/python3

from brownie import accounts


def test_mint_to_issuer(approve_many, issuer, nft):
    '''mint to issuer'''
    nft.mint(issuer, 1000, 0, "0x00", {'from': accounts[0]})
    assert nft.totalSupply() == 1000
    assert nft.balanceOf(issuer), 1000
    nft.mint(issuer, 2000, 0, "0x00", {'from': accounts[0]})
    assert nft.totalSupply() == 3000
    assert nft.balanceOf(issuer) == 3000


def test_mint_to_investors(nft):
    '''mint to investors'''
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


def test_burn_from_issuer(issuer, nft):
    '''burn from issuer'''
    nft.mint(issuer, 10000, 0, "0x00", {'from': accounts[0]})
    nft.burn(1, 1001, {'from': accounts[0]})
    assert nft.totalSupply() == 9000
    assert nft.balanceOf(issuer) == 9000
    nft.burn(1001, 5001, {'from': accounts[0]})
    assert nft.totalSupply() == 5000
    assert nft.balanceOf(issuer) == 5000
    nft.burn(5001, 10001, {'from': accounts[0]})
    assert nft.totalSupply() == 0
    assert nft.balanceOf(issuer) == 0


def test_burn_from_investors(nft):
    '''burn from investors'''
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


def test_mint_zero(issuer, nft):
    '''mint, burn, mint'''
    nft.mint(issuer, 10000, 0, "0x00", {'from': accounts[0]})
    assert nft.totalSupply() == 10000
    nft.burn(1, 10001, {'from': accounts[0]})
    assert nft.totalSupply() == 0
    nft.mint(issuer, 10000, 0, "0x00", {'from': accounts[0]})
    assert nft.totalSupply() == 10000
    assert nft.rangesOf(issuer) == ((10001, 20001,),)
    assert nft.getRange(1)[0] == '0x0000000000000000000000000000000000000000'
