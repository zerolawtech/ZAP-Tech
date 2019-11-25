#!/usr/bin/python3

from brownie import accounts


def test_mint_to_org(org, token):
    '''mint to org'''
    token.mint(org, 1000, {'from': accounts[0]})
    assert token.totalSupply() == 1000
    assert token.balanceOf(org) == 1000
    token.mint(org, 2000, {'from': accounts[0]})
    assert token.totalSupply() == 3000
    assert token.balanceOf(org) == 3000


def test_mint_to_investors(id1, id2, token):
    '''mint to investors'''
    token.mint(accounts[1], 1000, {'from': accounts[0]})
    assert token.totalSupply() == 1000
    assert token.balanceOf(accounts[1]) == 1000
    token.mint(accounts[2], 2000, {'from': accounts[0]})
    assert token.totalSupply() == 3000
    assert token.balanceOf(accounts[1]) == 1000
    assert token.balanceOf(accounts[2]) == 2000
    token.mint(accounts[1], 3000, {'from': accounts[0]})
    assert token.totalSupply() == 6000
    assert token.balanceOf(accounts[1]) == 4000
    assert token.balanceOf(accounts[2]) == 2000
    token.mint(accounts[2], 4000, {'from': accounts[0]})
    assert token.totalSupply() == 10000
    assert token.balanceOf(accounts[1]) == 4000
    assert token.balanceOf(accounts[2]) == 6000


def test_burn_from_org(id1, id2, org, token):
    '''burn from org'''
    token.mint(org, 10000, {'from': accounts[0]})
    token.burn(org, 1000, {'from': accounts[0]})
    assert token.totalSupply() == 9000
    assert token.balanceOf(org) == 9000
    token.burn(org, 4000, {'from': accounts[0]})
    assert token.totalSupply() == 5000
    assert token.balanceOf(org) == 5000
    token.burn(org, 5000, {'from': accounts[0]})
    assert token.totalSupply() == 0
    assert token.balanceOf(org) == 0


def test_burn_from_investors(token):
    '''burn from investors'''
    token.mint(accounts[1], 5000, {'from': accounts[0]})
    token.mint(accounts[2], 10000, {'from': accounts[0]})
    token.burn(accounts[1], 2000, {'from': accounts[0]})
    assert token.totalSupply() == 13000
    assert token.balanceOf(accounts[1]) == 3000
    assert token.balanceOf(accounts[2]) == 10000
    token.burn(accounts[2], 3000, {'from': accounts[0]})
    assert token.totalSupply() == 10000
    assert token.balanceOf(accounts[1]) == 3000
    assert token.balanceOf(accounts[2]) == 7000
    token.burn(accounts[1], 3000, {'from': accounts[0]})
    assert token.totalSupply() == 7000
    assert token.balanceOf(accounts[1]) == 0
    assert token.balanceOf(accounts[2]) == 7000
    token.burn(accounts[2], 7000, {'from': accounts[0]})
    assert token.totalSupply() == 0
    assert token.balanceOf(accounts[1]) == 0
    assert token.balanceOf(accounts[2]) == 0
