#!/usr/bin/python3

import pytest

from brownie import accounts


@pytest.fixture(scope="module", autouse=True)
def setup(approve_many, issuer, nft):
    nft.mint(issuer, 100000, 0, "0x00", {'from': accounts[0]})
    issuer.setCountry(1, True, 1, (1, 0, 0, 0, 0, 0, 0, 0), {'from': accounts[0]})
    nft.transfer(accounts[1], 1000, {'from': accounts[0]})


@pytest.fixture(scope="module")
def setcountry(issuer):
    issuer.setCountry(1, True, 1, (0, 1, 0, 0, 0, 0, 0, 0), {'from': accounts[0]})


@pytest.fixture(scope="module")
def updateinvestor(setcountry, kyc):
    kyc.updateInvestor(kyc.getID(accounts[2]), 1, 1, 2000000000, {'from': accounts[0]})


def test_country_investor_limit_blocked_issuer_investor(nft):
    '''country investor limit - blocked, issuer to investor'''
    with pytest.reverts("Country Investor Limit"):
        nft.transfer(accounts[2], 1000, {'from': accounts[0]})


def test_country_investor_limit_blocked_investor_investor(nft):
    '''country investor limit - blocked, investor to investor'''
    with pytest.reverts("Country Investor Limit"):
        nft.transfer(accounts[2], 500, {'from': accounts[1]})


def test_country_investor_limit_issuer_investor(nft):
    '''country investor limit - issuer to existing investor'''
    nft.transfer(accounts[1], 1000, {'from': accounts[0]})


def test_country_investor_limit_investor_investor(nft):
    '''country investor limit - investor to investor, full balance'''
    nft.transfer(accounts[2], 1000, {'from': accounts[1]})


def test_country_investor_limit_investor_investor_different_country(nft):
    '''country investor limit, investor to investor, different country'''
    nft.transfer(accounts[3], 500, {'from': accounts[1]})


def test_country_investor_limit_rating_issuer_investor(setcountry, nft):
    '''country investor limit, rating - issuer to existing investor'''
    nft.transfer(accounts[1], 1000, {'from': accounts[0]})


def test_country_investor_limit_rating_investor_investor(setcountry, nft):
    '''country investor limit, rating - investor to investor, full balance'''
    nft.transfer(accounts[2], 1000, {'from': accounts[1]})


def test_country_investor_limit_rating_investor_investor_different_country(setcountry, nft):
    '''country investor limit, rating - investor to investor, different rating'''
    nft.transfer(accounts[2], 500, {'from': accounts[1]})


def test_country_investor_limit_rating_blocked_issuer_investor(updateinvestor, nft):
    '''country investor limit, rating - blocked, issuer to investor'''
    with pytest.reverts("Country Investor Limit: Rating"):
        nft.transfer(accounts[2], 1000, {'from': accounts[0]})


def test_country_investor_limit_rating_blocked_investor_investor(updateinvestor, nft):
    '''country investor limit, rating - blocked, investor to investor'''
    with pytest.reverts("Country Investor Limit: Rating"):
        nft.transfer(accounts[2], 500, {'from': accounts[1]})
