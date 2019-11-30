#!/usr/bin/python3

import functools
import pytest

from brownie import accounts, rpc


@pytest.fixture(scope="module", autouse=True)
def setup(share, share2, gov, cp, id1, cptime):
    share.mint(accounts[1], 10000, {"from": accounts[0]})
    cp.newCheckpoint(share, cptime, {"from": accounts[0]})


@pytest.fixture(scope="module")
def vote(gov, org, share, cptime):
    yield functools.partial(_vote, gov, org, share, cptime)


def _vote(gov, org, share, cptime, approval_abi):
    gov.newProposal(
        "0xffff",
        cptime,
        cptime + 100,
        0,
        "test proposal",
        org,
        approval_abi,
        {"from": accounts[0]},
    )
    gov.newVote("0xffff", 5000, 0, [share], [1], {"from": accounts[0]})
    rpc.sleep(210)
    gov.voteOnProposal("0xffff", 1, {"from": accounts[1]})
    gov.closeProposal("0xffff", {"from": accounts[0]})


def test_modify_authorized_supply_not_approved(share):
    with pytest.reverts():
        share.modifyAuthorizedSupply(200000000, {"from": accounts[0]})


def test_modify_authorized_supply_approved(vote, share, share2, gov):
    vote(gov.modifyAuthorizedSupply.encode_input(share, 200000000))
    # wrong share
    with pytest.reverts():
        share2.modifyAuthorizedSupply(200000000, {"from": accounts[0]})
    # wrong amount
    with pytest.reverts():
        share.modifyAuthorizedSupply(190000000, {"from": accounts[0]})
    share.modifyAuthorizedSupply(200000000, {"from": accounts[0]})
    # call is only approved once
    with pytest.reverts():
        share.modifyAuthorizedSupply(200000000, {"from": accounts[0]})


def test_add_share_not_approved(BookShare, org):
    t = accounts[0].deploy(BookShare, org, "", "", 1000000)
    with pytest.reverts():
        org.addOrgShare(t, {"from": accounts[0]})


def test_add_share_approved(BookShare, vote, org, gov):
    share3 = accounts[0].deploy(BookShare, org, "", "", 1000000)
    vote(gov.addOrgShare.encode_input(share3))
    share4 = accounts[0].deploy(BookShare, org, "", "", 1000000)
    # wrong share
    with pytest.reverts():
        org.addOrgShare(share4, {"from": accounts[0]})
    org.addOrgShare(share3, {"from": accounts[0]})
