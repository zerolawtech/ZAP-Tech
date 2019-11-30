#!/usr/bin/python3

import pytest

from brownie import accounts


@pytest.fixture(scope="module", autouse=True)
def setup(cp, share, share2, share3, gov, cptime):
    cp.newCheckpoint(share, cptime, {"from": accounts[0]})
    cp.newCheckpoint(share2, cptime, {"from": accounts[0]})
    cp.newCheckpoint(share3, cptime + 50, {"from": accounts[0]})
    gov.newProposal(
        "0x1234",
        cptime,
        cptime + 100,
        cptime + 200,
        "test proposal",
        "0" * 40,
        "0x",
        {"from": accounts[0]},
    )


def test_new_vote(gov, share, share2):
    gov.newVote("0x1234", 5000, 0, [share, share2], [1, 2], {"from": accounts[0]})


def test_new_vote_wrong_state(gov, share, share2):
    with pytest.reverts("dev: wrong state"):
        gov.newVote("0x1111", 5000, 0, [share, share2], [1, 2], {"from": accounts[0]})


def test_new_vote_no_shares(gov):
    with pytest.reverts("dev: empty share array"):
        gov.newVote("0x1234", 5000, 0, [], [], {"from": accounts[0]})


def test_new_vote_mismatch(gov, share, share2):
    with pytest.reverts("dev: array length mismatch"):
        gov.newVote(
            "0x1234", 5000, 0, [share, share2], [1, 2, 3], {"from": accounts[0]}
        )


def test_new_vote_required_pct(gov, share, share2):
    with pytest.reverts("dev: required pct too high"):
        gov.newVote("0x1234", 11000, 0, [share, share2], [1, 2], {"from": accounts[0]})


def test_new_vote_quorum_pct(gov, share, share2):
    with pytest.reverts("dev: quorum pct too high"):
        gov.newVote(
            "0x1234", 5000, 11000, [share, share2], [1, 2], {"from": accounts[0]}
        )


def test_new_vote_repeat_share(gov, share):
    with pytest.reverts("dev: share repeat"):
        gov.newVote("0x1234", 5000, 0, [share, share], [1, 2], {"from": accounts[0]})


def test_new_vote_no_checkpoint(gov, share, share3):
    with pytest.reverts("dev: no checkpoint"):
        gov.newVote("0x1234", 5000, 0, [share, share3], [1, 2], {"from": accounts[0]})
