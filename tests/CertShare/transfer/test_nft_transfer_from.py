#!/usr/bin/python3

import pytest

from brownie import accounts


@pytest.fixture(scope="module", autouse=True)
def setup(approve_many, org, nft):
    nft.mint(org, 100000, 0, "0x00", {"from": accounts[0]})
    nft.transfer(accounts[1], 1000, {"from": accounts[0]})


def test_transfer_from(nft):
    """member transferFrom - approved"""
    nft.approve(accounts[3], 500, {"from": accounts[1]})
    assert nft.allowance(accounts[1], accounts[3]) == 500
    nft.transferFrom(accounts[1], accounts[2], 400, {"from": accounts[3]})
    assert nft.allowance(accounts[1], accounts[3]) == 100
    nft.transferFrom(accounts[1], accounts[2], 100, {"from": accounts[3]})
    assert nft.allowance(accounts[1], accounts[3]) == 0


def test_transfer_from_member_no_approval(nft):
    """transferFrom - no approval"""
    with pytest.reverts("Insufficient allowance"):
        nft.transferFrom(accounts[1], accounts[2], 1000, {"from": accounts[3]})


def test_transfer_from_member_insufficient_approval(nft):
    """transferFrom - insufficient approval"""
    nft.approve(accounts[3], 500, {"from": accounts[1]})
    with pytest.reverts("Insufficient allowance"):
        nft.transferFrom(accounts[1], accounts[2], 1000, {"from": accounts[3]})


def test_transfer_from_same_id(kyc, nft):
    """transferFrom - same member ID"""
    kyc.registerAddresses(kyc.getID(accounts[1]), [accounts[-1]], {"from": accounts[0]})
    nft.transferFrom(accounts[1], accounts[2], 500, {"from": accounts[-1]})


def test_transfer_from_org(nft):
    """org transferFrom"""
    nft.transferFrom(accounts[1], accounts[2], 1000, {"from": accounts[0]})


def test_authority_permission(org, nft):
    """authority transferFrom permission"""
    org.addAuthority(
        [accounts[-1]], ["0x23b872dd"], 2000000000, 1, {"from": accounts[0]}
    )
    nft.transferFrom(accounts[1], accounts[2], 500, {"from": accounts[-1]})
    org.setAuthoritySignatures(
        org.getID(accounts[-1]), ["0x23b872dd"], False, {"from": accounts[0]}
    )
    with pytest.reverts("Authority not permitted"):
        nft.transferFrom(accounts[1], accounts[2], 500, {"from": accounts[-1]})
