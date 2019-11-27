#!/usr/bin/python3

import pytest

from brownie import accounts


@pytest.fixture(scope="module", autouse=True)
def setup(approve_many, org, share):
    share.mint(org, 100000, {'from': accounts[0]})
    org.setMemberLimits((1, 0, 0, 0, 0, 0, 0, 0), {'from': accounts[0]})
    share.transfer(accounts[1], 1000, {'from': accounts[0]})


@pytest.fixture(scope="module")
def adjust_limits(org):
    org.setMemberLimits((0, 1, 0, 0, 0, 0, 0, 0), {'from': accounts[0]})


def test_total_member_limit_blocked_org_member(share):
    '''total member limit - blocked, org to member'''
    with pytest.reverts("Total Member Limit"):
        share.transfer(accounts[2], 1000, {'from': accounts[0]})


def test_total_member_limit_blocked_member_member(share):
    '''total member limit - blocked, member to member'''
    with pytest.reverts("Total Member Limit"):
        share.transfer(accounts[2], 500, {'from': accounts[1]})


def test_total_member_limit_org_member(share):
    '''total member limit - org to existing member'''
    share.transfer(accounts[1], 1000, {'from': accounts[0]})


def test_total_member_limit_member_member(share):
    '''total member limit - member to member, full balance'''
    share.transfer(accounts[2], 1000, {'from': accounts[1]})


def test_total_member_limit_rating_blocked_org_member(adjust_limits, share):
    '''total member limit, rating - blocked, org to member'''
    with pytest.reverts("Total Member Limit: Rating"):
        share.transfer(accounts[3], 1000, {'from': accounts[0]})


def test_total_member_limit_rating_blocked_member_member(share):
    '''total member limit, rating - blocked, member to member'''
    with pytest.reverts("Total Member Limit: Rating"):
        share.transfer(accounts[3], 500, {'from': accounts[1]})


def test_total_member_limit_rating_org_member(org, share):
    '''total member limit, rating - org to existing member'''
    share.transfer(accounts[1], 1000, {'from': accounts[0]})


def test_total_member_limit_rating_member_member(org, share):
    '''total member limit, rating - member to member, full balance'''
    share.transfer(accounts[2], 1000, {'from': accounts[1]})


def test_total_member_limit_rating_member_member_different_country(share):
    '''total member limit, rating - member to member, different rating'''
    share.transfer(accounts[2], 500, {'from': accounts[1]})
