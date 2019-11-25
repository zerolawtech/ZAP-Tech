#!/usr/bin/python3

from brownie import accounts


def test_mint_to_org(org, share):
    '''mint to org'''
    share.mint(org, 1000, {'from': accounts[0]})
    assert share.totalSupply() == 1000
    assert share.balanceOf(org) == 1000
    share.mint(org, 2000, {'from': accounts[0]})
    assert share.totalSupply() == 3000
    assert share.balanceOf(org) == 3000


def test_mint_to_investors(id1, id2, share):
    '''mint to investors'''
    share.mint(accounts[1], 1000, {'from': accounts[0]})
    assert share.totalSupply() == 1000
    assert share.balanceOf(accounts[1]) == 1000
    share.mint(accounts[2], 2000, {'from': accounts[0]})
    assert share.totalSupply() == 3000
    assert share.balanceOf(accounts[1]) == 1000
    assert share.balanceOf(accounts[2]) == 2000
    share.mint(accounts[1], 3000, {'from': accounts[0]})
    assert share.totalSupply() == 6000
    assert share.balanceOf(accounts[1]) == 4000
    assert share.balanceOf(accounts[2]) == 2000
    share.mint(accounts[2], 4000, {'from': accounts[0]})
    assert share.totalSupply() == 10000
    assert share.balanceOf(accounts[1]) == 4000
    assert share.balanceOf(accounts[2]) == 6000


def test_burn_from_org(id1, id2, org, share):
    '''burn from org'''
    share.mint(org, 10000, {'from': accounts[0]})
    share.burn(org, 1000, {'from': accounts[0]})
    assert share.totalSupply() == 9000
    assert share.balanceOf(org) == 9000
    share.burn(org, 4000, {'from': accounts[0]})
    assert share.totalSupply() == 5000
    assert share.balanceOf(org) == 5000
    share.burn(org, 5000, {'from': accounts[0]})
    assert share.totalSupply() == 0
    assert share.balanceOf(org) == 0


def test_burn_from_investors(share):
    '''burn from investors'''
    share.mint(accounts[1], 5000, {'from': accounts[0]})
    share.mint(accounts[2], 10000, {'from': accounts[0]})
    share.burn(accounts[1], 2000, {'from': accounts[0]})
    assert share.totalSupply() == 13000
    assert share.balanceOf(accounts[1]) == 3000
    assert share.balanceOf(accounts[2]) == 10000
    share.burn(accounts[2], 3000, {'from': accounts[0]})
    assert share.totalSupply() == 10000
    assert share.balanceOf(accounts[1]) == 3000
    assert share.balanceOf(accounts[2]) == 7000
    share.burn(accounts[1], 3000, {'from': accounts[0]})
    assert share.totalSupply() == 7000
    assert share.balanceOf(accounts[1]) == 0
    assert share.balanceOf(accounts[2]) == 7000
    share.burn(accounts[2], 7000, {'from': accounts[0]})
    assert share.totalSupply() == 0
    assert share.balanceOf(accounts[1]) == 0
    assert share.balanceOf(accounts[2]) == 0
