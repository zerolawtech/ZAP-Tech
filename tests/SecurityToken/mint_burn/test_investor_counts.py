#!/usr/bin/python3

import pytest

from brownie import accounts



def test_mint_org(check_counts, org, token):
    '''mint to org'''
    token.mint(org, 1000, {'from': accounts[0]})
    check_counts()
    token.mint(org, 9000, {'from': accounts[0]})
    check_counts()


def test_burn_org(check_counts, org, token):
    '''burn from org'''
    token.mint(org, 10000, {'from': accounts[0]})
    token.burn(org, 2000, {'from': accounts[0]})
    check_counts()
    token.burn(org, 8000, {'from': accounts[0]})
    check_counts()


def test_mint_investors(check_counts, token):
    '''mint to investors'''
    check_counts()
    token.mint(accounts[1], 1000, {'from': accounts[0]})
    check_counts(one=(1, 1, 0))
    token.mint(accounts[1], 1000, {'from': accounts[0]})
    token.mint(accounts[2], 1000, {'from': accounts[0]})
    token.mint(accounts[3], 1000, {'from': accounts[0]})
    check_counts(one=(2, 1, 1), two=(1, 1, 0))
    token.mint(accounts[1], 996000, {'from': accounts[0]})
    check_counts(one=(2, 1, 1), two=(1, 1, 0))


def test_burn_investors(check_counts, token):
    '''burn from investors'''
    token.mint(accounts[1], 5000, {'from': accounts[0]})
    token.mint(accounts[2], 3000, {'from': accounts[0]})
    token.mint(accounts[3], 2000, {'from': accounts[0]})
    token.burn(accounts[1], 1000, {'from': accounts[0]})
    check_counts(one=(2, 1, 1), two=(1, 1, 0))
    token.burn(accounts[1], 4000, {'from': accounts[0]})
    check_counts(one=(1, 0, 1), two=(1, 1, 0))
    token.burn(accounts[2], 3000, {'from': accounts[0]})
    token.burn(accounts[3], 2000, {'from': accounts[0]})
    check_counts()