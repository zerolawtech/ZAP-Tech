#!/usr/bin/python3

import pytest

from brownie import accounts


@pytest.fixture(scope="module", autouse=True)
def setup(approve_many, org, share):
    share.mint(org, 100000, {'from': accounts[0]})
    org.setInvestorLimits((1, 0, 0, 0, 0, 0, 0, 0), {'from': accounts[0]})
    share.transfer(accounts[1], 1000, {'from': accounts[0]})


@pytest.fixture(scope="module")
def adjust_limits(org):
    org.setInvestorLimits((0, 1, 0, 0, 0, 0, 0, 0), {'from': accounts[0]})


def test_total_investor_limit_blocked_org_investor(share):
    '''total investor limit - blocked, org to investor'''
    with pytest.reverts("Total Investor Limit"):
        share.transfer(accounts[2], 1000, {'from': accounts[0]})


def test_total_investor_limit_blocked_investor_investor(share):
    '''total investor limit - blocked, investor to investor'''
    with pytest.reverts("Total Investor Limit"):
        share.transfer(accounts[2], 500, {'from': accounts[1]})


def test_total_investor_limit_org_investor(share):
    '''total investor limit - org to existing investor'''
    share.transfer(accounts[1], 1000, {'from': accounts[0]})


def test_total_investor_limit_investor_investor(share):
    '''total investor limit - investor to investor, full balance'''
    share.transfer(accounts[2], 1000, {'from': accounts[1]})


def test_total_investor_limit_rating_blocked_org_investor(adjust_limits, share):
    '''total investor limit, rating - blocked, org to investor'''
    with pytest.reverts("Total Investor Limit: Rating"):
        share.transfer(accounts[3], 1000, {'from': accounts[0]})


def test_total_investor_limit_rating_blocked_investor_investor(share):
    '''total investor limit, rating - blocked, investor to investor'''
    with pytest.reverts("Total Investor Limit: Rating"):
        share.transfer(accounts[3], 500, {'from': accounts[1]})


def test_total_investor_limit_rating_org_investor(org, share):
    '''total investor limit, rating - org to existing investor'''
    share.transfer(accounts[1], 1000, {'from': accounts[0]})


def test_total_investor_limit_rating_investor_investor(org, share):
    '''total investor limit, rating - investor to investor, full balance'''
    share.transfer(accounts[2], 1000, {'from': accounts[1]})


def test_total_investor_limit_rating_investor_investor_different_country(share):
    '''total investor limit, rating - investor to investor, different rating'''
    share.transfer(accounts[2], 500, {'from': accounts[1]})
