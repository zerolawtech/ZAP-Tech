#!/usr/bin/python3

import functools
import pytest

from brownie import accounts, rpc


@pytest.fixture(scope="module", autouse=True)
def setup(token, token2, gov, cp, id1, cptime):
    token.mint(accounts[1], 10000, {'from': accounts[0]})
    cp.newCheckpoint(token, cptime, {'from': accounts[0]})


@pytest.fixture(scope="module")
def vote(gov, org, token, cptime):
    yield functools.partial(_vote, gov, org, token, cptime)


def _vote(gov, org, token, cptime, approval_abi):
    gov.newProposal(
        "0xffff",
        cptime,
        cptime + 100,
        0,
        "test proposal",
        org,
        approval_abi,
        {'from': accounts[0]}
    )
    gov.newVote("0xffff", 5000, 0, [token], [1], {'from': accounts[0]})
    rpc.sleep(210)
    gov.voteOnProposal("0xffff", 1, {'from': accounts[1]})
    gov.closeProposal("0xffff", {'from': accounts[0]})


def test_modify_authorized_supply_not_approved(token):
    with pytest.reverts():
        token.modifyAuthorizedSupply(200000000, {'from': accounts[0]})


def test_modify_authorized_supply_approved(vote, token, token2, gov):
    vote(gov.modifyAuthorizedSupply.encode_input(token, 200000000))
    # wrong token
    with pytest.reverts():
        token2.modifyAuthorizedSupply(200000000, {'from': accounts[0]})
    # wrong amount
    with pytest.reverts():
        token.modifyAuthorizedSupply(190000000, {'from': accounts[0]})
    token.modifyAuthorizedSupply(200000000, {'from': accounts[0]})
    # call is only approved once
    with pytest.reverts():
        token.modifyAuthorizedSupply(200000000, {'from': accounts[0]})


def test_add_token_not_approved(SecurityToken, org):
    t = accounts[0].deploy(SecurityToken, org, "", "", 1000000)
    with pytest.reverts():
        org.addToken(t, {'from': accounts[0]})


def test_add_token_approved(SecurityToken, vote, org, gov):
    token3 = accounts[0].deploy(SecurityToken, org, "", "", 1000000)
    vote(gov.addToken.encode_input(token3))
    token4 = accounts[0].deploy(SecurityToken, org, "", "", 1000000)
    # wrong token
    with pytest.reverts():
        org.addToken(token4, {'from': accounts[0]})
    org.addToken(token3, {'from': accounts[0]})
