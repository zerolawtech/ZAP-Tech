#!/usr/bin/python3

import pytest

from brownie import accounts


@pytest.fixture(scope="module", autouse=True)
def setup(id1, id2, org, share):
    share.mint(org, 100000, {'from': accounts[0]})


def test_global_lock(org, share):
    '''global lock - member / member'''
    share.transfer(accounts[1], 1000, {'from': accounts[0]})
    org.setGlobalRestriction(True, {'from': accounts[0]})
    with pytest.reverts("Transfers locked: Org"):
        share.transfer(accounts[2], 1000, {'from': accounts[1]})
    org.setGlobalRestriction(False, {'from': accounts[0]})
    share.transfer(accounts[2], 1000, {'from': accounts[1]})


def test_global_lock_org(org, share):
    '''global lock - org / member'''
    org.setGlobalRestriction(True, {'from': accounts[0]})
    share.transfer(accounts[1], 1000, {'from': accounts[0]})
    with pytest.reverts("Transfers locked: Org"):
        share.transfer(accounts[0], 1000, {'from': accounts[1]})
    org.setGlobalRestriction(False, {'from': accounts[0]})
    share.transfer(accounts[0], 1000, {'from': accounts[1]})


def test_share_lock(org, share):
    '''share lock - member / member'''
    share.transfer(accounts[1], 1000, {'from': accounts[0]})
    org.setOrgShareRestriction(share, True, {'from': accounts[0]})
    with pytest.reverts("Transfers locked: Share"):
        share.transfer(accounts[2], 1000, {'from': accounts[1]})
    org.setOrgShareRestriction(share, False, {'from': accounts[0]})
    share.transfer(accounts[2], 1000, {'from': accounts[1]})


def test_share_lock_org(org, share):
    '''share lock - org / member'''
    org.setOrgShareRestriction(share, True, {'from': accounts[0]})
    share.transfer(accounts[1], 1000, {'from': accounts[0]})
    with pytest.reverts("Transfers locked: Share"):
        share.transfer(accounts[0], 1000, {'from': accounts[1]})
    org.setOrgShareRestriction(share, False, {'from': accounts[0]})
    share.transfer(accounts[0], 1000, {'from': accounts[1]})
