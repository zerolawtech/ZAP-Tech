#!/usr/bin/python3

import functools
import pytest

from brownie import accounts, rpc


@pytest.fixture(scope="module", autouse=True)
def setup(token, token2, gov, cp, approve_one, cptime):
    token.mint(accounts[1], 10000, {'from': accounts[0]})
    cp.newCheckpoint(token, cptime, {'from': accounts[0]})


@pytest.fixture(scope="module")
def vote(gov, issuer, token, cptime):
    yield functools.partial(_vote, gov, issuer, token, cptime)


def _vote(gov, issuer, token, cptime, approval_abi):
    gov.newProposal(
        "0xffff",
        cptime,
        cptime + 100,
        0,
        "test proposal",
        issuer,
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
    vote(gov.modifyAuthorizedSupply.encode_abi(token, 200000000))
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


def test_add_token_not_approved(SecurityToken, issuer):
    t = accounts[0].deploy(SecurityToken, issuer, "", "", 1000000)
    with pytest.reverts():
        issuer.addToken(t, {'from': accounts[0]})


def test_add_token_approved(SecurityToken, vote, issuer, gov):
    token3 = accounts[0].deploy(SecurityToken, issuer, "", "", 1000000)
    vote(gov.addToken.encode_abi(token3))
    token4 = accounts[0].deploy(SecurityToken, issuer, "", "", 1000000)
    # wrong token
    with pytest.reverts():
        issuer.addToken(token4, {'from': accounts[0]})
    issuer.addToken(token3, {'from': accounts[0]})
