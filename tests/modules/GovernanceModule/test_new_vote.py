#!/usr/bin/python3

import pytest

from brownie import accounts


@pytest.fixture(scope="module", autouse=True)
def setup(cp, token, token2, token3, gov, cptime):
    cp.newCheckpoint(token, cptime, {'from': accounts[0]})
    cp.newCheckpoint(token2, cptime, {'from': accounts[0]})
    cp.newCheckpoint(token3, cptime + 50, {'from': accounts[0]})
    gov.newProposal(
        "0x1234",
        cptime,
        cptime + 100,
        cptime + 200,
        "test proposal",
        "0" * 40,
        "0x",
        {'from': accounts[0]}
    )


def test_new_vote(gov, token, token2):
    gov.newVote("0x1234", 5000, 0, [token, token2], [1, 2], {'from': accounts[0]})


def test_new_vote_wrong_state(gov, token, token2):
    with pytest.reverts("dev: wrong state"):
        gov.newVote("0x1111", 5000, 0, [token, token2], [1, 2], {'from': accounts[0]})


def test_new_vote_no_tokens(gov):
    with pytest.reverts("dev: empty token array"):
        gov.newVote("0x1234", 5000, 0, [], [], {'from': accounts[0]})


def test_new_vote_mismatch(gov, token, token2):
    with pytest.reverts("dev: array length mismatch"):
        gov.newVote("0x1234", 5000, 0, [token, token2], [1, 2, 3], {'from': accounts[0]})


def test_new_vote_required_pct(gov, token, token2):
    with pytest.reverts("dev: required pct too high"):
        gov.newVote("0x1234", 11000, 0, [token, token2], [1, 2], {'from': accounts[0]})


def test_new_vote_quorum_pct(gov, token, token2):
    with pytest.reverts("dev: quorum pct too high"):
        gov.newVote("0x1234", 5000, 11000, [token, token2], [1, 2], {'from': accounts[0]})


def test_new_vote_repeat_token(gov, token):
    with pytest.reverts("dev: token repeat"):
        gov.newVote("0x1234", 5000, 0, [token, token], [1, 2], {'from': accounts[0]})


def test_new_vote_no_checkpoint(gov, token, token3):
    with pytest.reverts("dev: no checkpoint"):
        gov.newVote("0x1234", 5000, 0, [token, token3], [1, 2], {'from': accounts[0]})
