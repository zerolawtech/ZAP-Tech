#!/usr/bin/python3

import pytest

from brownie import accounts


@pytest.fixture(scope="module", autouse=True)
def setup(approve_many, org, share):
    share.mint(org, 100000, {'from': accounts[0]})
    share.transfer(accounts[1], 1000, {'from': accounts[0]})


def test_transfer_from(share):
    '''investor transferFrom - approved'''
    share.approve(accounts[3], 500, {'from': accounts[1]})
    assert share.allowance(accounts[1], accounts[3]) == 500
    share.transferFrom(accounts[1], accounts[2], 400, {'from': accounts[3]})
    assert share.allowance(accounts[1], accounts[3]) == 100
    share.transferFrom(accounts[1], accounts[2], 100, {'from': accounts[3]})
    assert share.allowance(accounts[1], accounts[3]) == 0


def test_transfer_from_investor_no_approval(share):
    '''transferFrom - no approval'''
    with pytest.reverts("Insufficient allowance"):
        share.transferFrom(accounts[1], accounts[2], 1000, {'from': accounts[3]})


def test_transfer_from_investor_insufficient_approval(share):
    '''transferFrom - insufficient approval'''
    share.approve(accounts[3], 500, {'from': accounts[1]})
    with pytest.reverts("Insufficient allowance"):
        share.transferFrom(accounts[1], accounts[2], 1000, {'from': accounts[3]})


def test_transfer_from_same_id(kyc, share):
    '''transferFrom - same investor ID'''
    kyc.registerAddresses(kyc.getID(accounts[1]), [accounts[-1]], {'from': accounts[0]})
    share.transferFrom(accounts[1], accounts[2], 500, {'from': accounts[-1]})


def test_transfer_from_org(share):
    '''org transferFrom'''
    share.transferFrom(accounts[1], accounts[2], 1000, {'from': accounts[0]})


def test_authority_permission(org, share):
    '''authority transferFrom permission'''
    org.addAuthority([accounts[-1]], ["0x23b872dd"], 2000000000, 1, {'from': accounts[0]})
    share.transferFrom(accounts[1], accounts[2], 500, {'from': accounts[-1]})
    org.setAuthoritySignatures(
        org.getID(accounts[-1]),
        ["0x23b872dd"],
        False,
        {'from': accounts[0]}
    )
    with pytest.reverts("Authority not permitted"):
        share.transferFrom(accounts[1], accounts[2], 500, {'from': accounts[-1]})
