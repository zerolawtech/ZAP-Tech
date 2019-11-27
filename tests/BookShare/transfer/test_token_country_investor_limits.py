#!/usr/bin/python3

import pytest

from brownie import accounts


@pytest.fixture(scope="module", autouse=True)
def setup(approve_many, org, share):
    share.mint(org, 100000, {'from': accounts[0]})
    org.setCountry(1, True, 1, (1, 0, 0, 0, 0, 0, 0, 0), {'from': accounts[0]})
    share.transfer(accounts[1], 1000, {'from': accounts[0]})


def test_country_member_limit_blocked_org_member(share):
    '''country member limit - blocked, org to member'''
    with pytest.reverts("Country Member Limit"):
        share.transfer(accounts[2], 1000, {'from': accounts[0]})


def test_country_member_limit_blocked_member_member(share):
    '''country member limit - blocked, member to member'''
    with pytest.reverts("Country Member Limit"):
        share.transfer(accounts[2], 500, {'from': accounts[1]})


def test_country_member_limit_org_member(share):
    '''country member limit - org to existing member'''
    share.transfer(accounts[1], 1000, {'from': accounts[0]})


def test_country_member_limit_member_member(share):
    '''country member limit - member to member, full balance'''
    share.transfer(accounts[2], 1000, {'from': accounts[1]})


def test_country_member_limit_member_member_different_country(share):
    '''country member limit, member to member, different country'''
    share.transfer(accounts[3], 500, {'from': accounts[1]})


def test_country_member_limit_rating_blocked_org_member(kyc, org, share):
    '''country member limit, rating - blocked, org to member'''
    org.setCountry(1, True, 1, (0, 1, 0, 0, 0, 0, 0, 0), {'from': accounts[0]})
    kyc.updateMember(kyc.getID(accounts[2]), 1, 1, 2000000000, {'from': accounts[0]})
    with pytest.reverts("Country Member Limit: Rating"):
        share.transfer(accounts[2], 1000, {'from': accounts[0]})


def test_country_member_limit_rating_blocked_member_member(kyc, org, share):
    '''country member limit, rating - blocked, member to member'''
    org.setCountry(1, True, 1, (0, 1, 0, 0, 0, 0, 0, 0), {'from': accounts[0]})
    kyc.updateMember(kyc.getID(accounts[2]), 1, 1, 2000000000, {'from': accounts[0]})
    with pytest.reverts("Country Member Limit: Rating"):
        share.transfer(accounts[2], 500, {'from': accounts[1]})


def test_country_member_limit_rating_org_member(org, share):
    '''country member limit, rating - org to existing member'''
    org.setCountry(1, True, 1, (0, 1, 0, 0, 0, 0, 0, 0), {'from': accounts[0]})
    share.transfer(accounts[1], 1000, {'from': accounts[0]})


def test_country_member_limit_rating_member_member(org, share):
    '''country member limit, rating - member to member, full balance'''
    org.setCountry(1, True, 1, (0, 1, 0, 0, 0, 0, 0, 0), {'from': accounts[0]})
    share.transfer(accounts[2], 1000, {'from': accounts[1]})


def test_country_member_limit_rating_member_member_different_country(org, share):
    '''country member limit, rating - member to member, different rating'''
    org.setCountry(1, True, 1, (0, 1, 0, 0, 0, 0, 0, 0), {'from': accounts[0]})
    share.transfer(accounts[2], 500, {'from': accounts[1]})
