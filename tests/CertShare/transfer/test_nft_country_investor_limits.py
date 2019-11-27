#!/usr/bin/python3

import pytest

from brownie import accounts


@pytest.fixture(scope="module", autouse=True)
def setup(approve_many, org, nft):
    nft.mint(org, 100000, 0, "0x00", {'from': accounts[0]})
    org.setCountry(1, True, 1, (1, 0, 0, 0, 0, 0, 0, 0), {'from': accounts[0]})
    nft.transfer(accounts[1], 1000, {'from': accounts[0]})


@pytest.fixture(scope="module")
def setcountry(org):
    org.setCountry(1, True, 1, (0, 1, 0, 0, 0, 0, 0, 0), {'from': accounts[0]})


@pytest.fixture(scope="module")
def updatemember(setcountry, kyc):
    kyc.updateMember(kyc.getID(accounts[2]), 1, 1, 2000000000, {'from': accounts[0]})


def test_country_member_limit_blocked_org_member(nft):
    '''country member limit - blocked, org to member'''
    with pytest.reverts("Country Member Limit"):
        nft.transfer(accounts[2], 1000, {'from': accounts[0]})


def test_country_member_limit_blocked_member_member(nft):
    '''country member limit - blocked, member to member'''
    with pytest.reverts("Country Member Limit"):
        nft.transfer(accounts[2], 500, {'from': accounts[1]})


def test_country_member_limit_org_member(nft):
    '''country member limit - org to existing member'''
    nft.transfer(accounts[1], 1000, {'from': accounts[0]})


def test_country_member_limit_member_member(nft):
    '''country member limit - member to member, full balance'''
    nft.transfer(accounts[2], 1000, {'from': accounts[1]})


def test_country_member_limit_member_member_different_country(nft):
    '''country member limit, member to member, different country'''
    nft.transfer(accounts[3], 500, {'from': accounts[1]})


def test_country_member_limit_rating_org_member(setcountry, nft):
    '''country member limit, rating - org to existing member'''
    nft.transfer(accounts[1], 1000, {'from': accounts[0]})


def test_country_member_limit_rating_member_member(setcountry, nft):
    '''country member limit, rating - member to member, full balance'''
    nft.transfer(accounts[2], 1000, {'from': accounts[1]})


def test_country_member_limit_rating_member_member_different_country(setcountry, nft):
    '''country member limit, rating - member to member, different rating'''
    nft.transfer(accounts[2], 500, {'from': accounts[1]})


def test_country_member_limit_rating_blocked_org_member(updatemember, nft):
    '''country member limit, rating - blocked, org to member'''
    with pytest.reverts("Country Member Limit: Rating"):
        nft.transfer(accounts[2], 1000, {'from': accounts[0]})


def test_country_member_limit_rating_blocked_member_member(updatemember, nft):
    '''country member limit, rating - blocked, member to member'''
    with pytest.reverts("Country Member Limit: Rating"):
        nft.transfer(accounts[2], 500, {'from': accounts[1]})
