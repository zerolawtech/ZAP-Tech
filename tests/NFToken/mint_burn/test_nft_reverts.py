#!/usr/bin/python3

import pytest

from brownie import accounts


def test_mint_zero(issuer, nft):
    '''mint 0 tokens'''
    with pytest.reverts("dev: mint 0"):
        nft.mint(issuer, 0, 0, "0x00", {'from': accounts[0]})
    nft.mint(issuer, 10000, 0, "0x00", {'from': accounts[0]})
    with pytest.reverts("dev: mint 0"):
        nft.mint(issuer, 0, 0, "0x00", {'from': accounts[0]})


def test_mint_time(issuer, nft):
    '''mint - lock time < now'''
    with pytest.reverts("dev: time"):
        nft.mint(issuer, 1000, 1, "0x00", {'from': accounts[0]})


def test_mint_overflow(issuer, nft):
    '''mint - overflows'''
    nft.modifyAuthorizedSupply(2**49, {'from': accounts[0]})
    nft.mint(issuer, (2**48) - 10, 0, "0x00", {'from': accounts[0]})
    with pytest.reverts("dev: overflow"):
        nft.mint(issuer, 1000, 1, "0x00", {'from': accounts[0]})
    with pytest.reverts("dev: upper bound"):
        nft.mint(issuer, 9, 1, "0x00", {'from': accounts[0]})


def test_burn_zero(issuer, nft):
    '''burn 0 nfts'''
    with pytest.reverts("dev: burn 0"):
        nft.burn(1, 1, {'from': accounts[0]})
    nft.mint(issuer, 10000, 0, "0x00", {'from': accounts[0]})
    with pytest.reverts("dev: burn 0"):
        nft.burn(1, 1, {'from': accounts[0]})


def test_burn_exceeds_balance(issuer, nft):
    '''burn exceeds balance'''
    with pytest.reverts("dev: exceeds upper bound"):
        nft.burn(1, 101, {'from': accounts[0]})
    nft.mint(issuer, 4000, 0, "0x00", {'from': accounts[0]})
    with pytest.reverts("dev: exceeds upper bound"):
        nft.burn(1, 5001, {'from': accounts[0]})
    nft.burn(1, 3001, {'from': accounts[0]})
    with pytest.reverts("dev: exceeds upper bound"):
        nft.burn(3001, 4002, {'from': accounts[0]})
    nft.burn(3001, 4001, {'from': accounts[0]})
    with pytest.reverts("dev: exceeds upper bound"):
        nft.burn(4001, 4101, {'from': accounts[0]})


def test_burn_multiple_ranges(issuer, nft):
    '''burn multiple ranges'''
    nft.mint(issuer, 1000, 0, "0x00", {'from': accounts[0]})
    nft.mint(issuer, 1000, 0, "0x01", {'from': accounts[0]})
    with pytest.reverts("dev: multiple ranges"):
        nft.burn(500, 1500, {'from': accounts[0]})


def test_reburn(issuer, nft):
    '''burn already burnt nfts'''
    nft.mint(issuer, 1000, "0x00", 0, {'from': accounts[0]})
    nft.burn(100, 200, {'from': accounts[0]})
    with pytest.reverts("dev: already burnt"):
        nft.burn(100, 200, {'from': accounts[0]})


def test_authorized_below_total(issuer, nft):
    '''authorized supply below total supply'''
    nft.mint(issuer, 100000, "0x00", 0, {'from': accounts[0]})
    with pytest.reverts("dev: auth below total"):
        nft.modifyAuthorizedSupply(10000, {'from': accounts[0]})


def test_total_above_authorized(issuer, nft):
    '''total supply above authorized'''
    nft.modifyAuthorizedSupply(10000, {'from': accounts[0]})
    with pytest.reverts("dev: exceed auth"):
        nft.mint(issuer, 20000, 0, "0x00", {'from': accounts[0]})
    nft.mint(issuer, 6000, 0, "0x00", {'from': accounts[0]})
    with pytest.reverts("dev: exceed auth"):
        nft.mint(issuer, 6000, 0, "0x00", {'from': accounts[0]})
    nft.mint(issuer, 4000, 0, "0x00", {'from': accounts[0]})
    with pytest.reverts("dev: exceed auth"):
        nft.mint(issuer, 1, 0, "0x00", {'from': accounts[0]})
    with pytest.reverts("dev: mint 0"):
        nft.mint(issuer, 0, 0, "0x00", {'from': accounts[0]})


def test_mint_to_custodian(nft, cust):
    '''mint to custodian'''
    with pytest.reverts("dev: custodian"):
        nft.mint(cust, 6000, 0, "0x00", {'from': accounts[0]})


def test_burn_from_custodian(issuer, nft, cust):
    '''burn from custodian'''
    nft.mint(issuer, 10000, 0, "0x00", {'from': accounts[0]})
    nft.transfer(cust, 10000, {'from': accounts[0]})
    with pytest.reverts("dev: custodian"):
        nft.burn(1, 5000, {'from': accounts[0]})
