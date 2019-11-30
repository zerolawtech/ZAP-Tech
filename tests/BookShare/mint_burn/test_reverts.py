#!/usr/bin/python3

import pytest

from brownie import accounts


def test_mint_zero(org, share):
    """mint 0 shares"""
    with pytest.reverts("dev: mint 0"):
        share.mint(org, 0, {"from": accounts[0]})
    share.mint(org, 10000, {"from": accounts[0]})
    with pytest.reverts("dev: mint 0"):
        share.mint(org, 0, {"from": accounts[0]})


def test_burn_zero(org, share):
    """burn 0 shares"""
    with pytest.reverts("dev: burn 0"):
        share.burn(org, 0, {"from": accounts[0]})
    share.mint(org, 10000, {"from": accounts[0]})
    with pytest.reverts("dev: burn 0"):
        share.burn(org, 0, {"from": accounts[0]})


def test_authorized_below_total(org, share):
    """authorized supply below total supply"""
    share.mint(org, 100000, {"from": accounts[0]})
    with pytest.reverts("dev: auth below total"):
        share.modifyAuthorizedSupply(10000, {"from": accounts[0]})


def test_total_above_authorized(org, share):
    """total supply above authorized"""
    share.modifyAuthorizedSupply(10000, {"from": accounts[0]})
    with pytest.reverts("dev: exceed auth"):
        share.mint(org, 20000, {"from": accounts[0]})
    share.mint(org, 6000, {"from": accounts[0]})
    with pytest.reverts("dev: exceed auth"):
        share.mint(org, 6000, {"from": accounts[0]})
    share.mint(org, 4000, {"from": accounts[0]})
    with pytest.reverts("dev: exceed auth"):
        share.mint(org, 1, {"from": accounts[0]})
    with pytest.reverts("dev: mint 0"):
        share.mint(org, 0, {"from": accounts[0]})


def test_burn_exceeds_balance(org, share):
    """burn exceeds balance"""
    with pytest.reverts():
        share.burn(org, 100, {"from": accounts[0]})
    share.mint(org, 4000, {"from": accounts[0]})
    with pytest.reverts():
        share.burn(org, 5000, {"from": accounts[0]})
    share.burn(org, 3000, {"from": accounts[0]})
    with pytest.reverts():
        share.burn(org, 1001, {"from": accounts[0]})
    share.burn(org, 1000, {"from": accounts[0]})
    with pytest.reverts():
        share.burn(org, 100, {"from": accounts[0]})


def test_mint_to_custodian(org, share, cust):
    """mint to custodian"""
    with pytest.reverts("dev: custodian"):
        share.mint(cust, 6000, {"from": accounts[0]})


def test_burn_from_custodian(org, share, cust):
    """burn from custodian"""
    share.mint(org, 10000, {"from": accounts[0]})
    share.transfer(cust, 10000, {"from": accounts[0]})
    with pytest.reverts("dev: custodian"):
        share.burn(cust, 5000, {"from": accounts[0]})


def test_global_lock(org, share, id1):
    """mint - share lock"""
    org.setOrgShareRestriction(share, True, {"from": accounts[0]})
    with pytest.reverts("dev: share locked"):
        share.mint(accounts[1], 1, {"from": accounts[0]})
