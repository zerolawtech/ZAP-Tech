#!/usr/bin/python3

import pytest

from brownie import accounts


def test_mint_zero(org, nft):
    '''mint 0 shares'''
    with pytest.reverts("dev: mint 0"):
        nft.mint(org, 0, 0, "0x00", {'from': accounts[0]})
    nft.mint(org, 10000, 0, "0x00", {'from': accounts[0]})
    with pytest.reverts("dev: mint 0"):
        nft.mint(org, 0, 0, "0x00", {'from': accounts[0]})


def test_mint_time(org, nft):
    '''mint - lock time < now'''
    with pytest.reverts("dev: time"):
        nft.mint(org, 1000, 1, "0x00", {'from': accounts[0]})


def test_mint_overflow(org, nft):
    '''mint - overflows'''
    nft.modifyAuthorizedSupply(2**49, {'from': accounts[0]})
    nft.mint(org, (2**48) - 10, 0, "0x00", {'from': accounts[0]})
    with pytest.reverts("dev: overflow"):
        nft.mint(org, 1000, 1, "0x00", {'from': accounts[0]})
    with pytest.reverts("dev: upper bound"):
        nft.mint(org, 9, 1, "0x00", {'from': accounts[0]})


def test_burn_zero(org, nft):
    '''burn 0 nfts'''
    with pytest.reverts("dev: burn 0"):
        nft.burn(1, 1, {'from': accounts[0]})
    nft.mint(org, 10000, 0, "0x00", {'from': accounts[0]})
    with pytest.reverts("dev: burn 0"):
        nft.burn(1, 1, {'from': accounts[0]})


def test_burn_exceeds_balance(org, nft):
    '''burn exceeds balance'''
    with pytest.reverts("dev: exceeds upper bound"):
        nft.burn(1, 101, {'from': accounts[0]})
    nft.mint(org, 4000, 0, "0x00", {'from': accounts[0]})
    with pytest.reverts("dev: exceeds upper bound"):
        nft.burn(1, 5001, {'from': accounts[0]})
    nft.burn(1, 3001, {'from': accounts[0]})
    with pytest.reverts("dev: exceeds upper bound"):
        nft.burn(3001, 4002, {'from': accounts[0]})
    nft.burn(3001, 4001, {'from': accounts[0]})
    with pytest.reverts("dev: exceeds upper bound"):
        nft.burn(4001, 4101, {'from': accounts[0]})


def test_burn_multiple_ranges(org, nft):
    '''burn multiple ranges'''
    nft.mint(org, 1000, 0, "0x00", {'from': accounts[0]})
    nft.mint(org, 1000, 0, "0x01", {'from': accounts[0]})
    with pytest.reverts("dev: multiple ranges"):
        nft.burn(500, 1500, {'from': accounts[0]})


def test_reburn(org, nft):
    '''burn already burnt nfts'''
    nft.mint(org, 1000, "0x00", 0, {'from': accounts[0]})
    nft.burn(100, 200, {'from': accounts[0]})
    with pytest.reverts("dev: already burnt"):
        nft.burn(100, 200, {'from': accounts[0]})


def test_authorized_below_total(org, nft):
    '''authorized supply below total supply'''
    nft.mint(org, 100000, "0x00", 0, {'from': accounts[0]})
    with pytest.reverts("dev: auth below total"):
        nft.modifyAuthorizedSupply(10000, {'from': accounts[0]})


def test_total_above_authorized(org, nft):
    '''total supply above authorized'''
    nft.modifyAuthorizedSupply(10000, {'from': accounts[0]})
    with pytest.reverts("dev: exceed auth"):
        nft.mint(org, 20000, 0, "0x00", {'from': accounts[0]})
    nft.mint(org, 6000, 0, "0x00", {'from': accounts[0]})
    with pytest.reverts("dev: exceed auth"):
        nft.mint(org, 6000, 0, "0x00", {'from': accounts[0]})
    nft.mint(org, 4000, 0, "0x00", {'from': accounts[0]})
    with pytest.reverts("dev: exceed auth"):
        nft.mint(org, 1, 0, "0x00", {'from': accounts[0]})
    with pytest.reverts("dev: mint 0"):
        nft.mint(org, 0, 0, "0x00", {'from': accounts[0]})


def test_mint_to_custodian(nft, cust):
    '''mint to custodian'''
    with pytest.reverts("dev: custodian"):
        nft.mint(cust, 6000, 0, "0x00", {'from': accounts[0]})


def test_burn_from_custodian(org, nft, cust):
    '''burn from custodian'''
    nft.mint(org, 10000, 0, "0x00", {'from': accounts[0]})
    nft.transfer(cust, 10000, {'from': accounts[0]})
    with pytest.reverts("dev: custodian"):
        nft.burn(1, 5000, {'from': accounts[0]})
