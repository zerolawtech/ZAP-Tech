#!/usr/bin/python3

import pytest

from brownie import accounts



def test_mint_org(check_counts, org, share):
    '''mint to org'''
    share.mint(org, 1000, {'from': accounts[0]})
    check_counts()
    share.mint(org, 9000, {'from': accounts[0]})
    check_counts()


def test_burn_org(check_counts, org, share):
    '''burn from org'''
    share.mint(org, 10000, {'from': accounts[0]})
    share.burn(org, 2000, {'from': accounts[0]})
    check_counts()
    share.burn(org, 8000, {'from': accounts[0]})
    check_counts()


def test_mint_investors(check_counts, share):
    '''mint to investors'''
    check_counts()
    share.mint(accounts[1], 1000, {'from': accounts[0]})
    check_counts(one=(1, 1, 0))
    share.mint(accounts[1], 1000, {'from': accounts[0]})
    share.mint(accounts[2], 1000, {'from': accounts[0]})
    share.mint(accounts[3], 1000, {'from': accounts[0]})
    check_counts(one=(2, 1, 1), two=(1, 1, 0))
    share.mint(accounts[1], 996000, {'from': accounts[0]})
    check_counts(one=(2, 1, 1), two=(1, 1, 0))


def test_burn_investors(check_counts, share):
    '''burn from investors'''
    share.mint(accounts[1], 5000, {'from': accounts[0]})
    share.mint(accounts[2], 3000, {'from': accounts[0]})
    share.mint(accounts[3], 2000, {'from': accounts[0]})
    share.burn(accounts[1], 1000, {'from': accounts[0]})
    check_counts(one=(2, 1, 1), two=(1, 1, 0))
    share.burn(accounts[1], 4000, {'from': accounts[0]})
    check_counts(one=(1, 0, 1), two=(1, 1, 0))
    share.burn(accounts[2], 3000, {'from': accounts[0]})
    share.burn(accounts[3], 2000, {'from': accounts[0]})
    check_counts()