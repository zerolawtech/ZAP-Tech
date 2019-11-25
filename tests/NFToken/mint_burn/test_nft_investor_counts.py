#!/usr/bin/python3

from brownie import accounts


def test_mint_org(check_counts, approve_many, org, nft):
    '''mint to org'''
    nft.mint(org, 1000, 0, "0x00", {'from': accounts[0]})
    check_counts()
    nft.mint(org, 9000, 0, "0x00", {'from': accounts[0]})
    check_counts()


def test_burn_org(check_counts, org, nft):
    '''burn from org'''
    nft.mint(org, 10000, 0, "0x00", {'from': accounts[0]})
    nft.burn(1, 2001, {'from': accounts[0]})
    check_counts()
    nft.burn(2001, 10001, {'from': accounts[0]})
    check_counts()


def test_mint_investors(check_counts, nft):
    '''mint to investors'''
    check_counts()
    nft.mint(accounts[1], 1000, 0, "0x00", {'from': accounts[0]})
    check_counts(one=(1, 1, 0))
    nft.mint(accounts[1], 1000, 0, "0x00", {'from': accounts[0]})
    nft.mint(accounts[2], 1000, 0, "0x00", {'from': accounts[0]})
    nft.mint(accounts[3], 1000, 0, "0x00", {'from': accounts[0]})
    check_counts(one=(2, 1, 1), two=(1, 1, 0))
    nft.mint(accounts[1], 996000, 0, "0x00", {'from': accounts[0]})
    check_counts(one=(2, 1, 1), two=(1, 1, 0))


def test_burn_investors(check_counts, nft):
    '''burn from investors'''
    nft.mint(accounts[1], 5000, 0, "0x00", {'from': accounts[0]})
    nft.mint(accounts[2], 3000, 0, "0x00", {'from': accounts[0]})
    nft.mint(accounts[3], 2000, 0, "0x00", {'from': accounts[0]})
    nft.burn(1, 1001, {'from': accounts[0]})
    check_counts(one=(2, 1, 1), two=(1, 1, 0))
    nft.burn(1001, 5001, {'from': accounts[0]})
    check_counts(one=(1, 0, 1), two=(1, 1, 0))
    nft.burn(5001, 8001, {'from': accounts[0]})
    nft.burn(8001, 10001, {'from': accounts[0]})
    check_counts()
