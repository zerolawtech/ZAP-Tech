#!/usr/bin/python3

import pytest

from brownie import accounts, rpc


@pytest.fixture(scope="module", autouse=True)
def setup(proposal, gov, token, token2):
    gov.newVote("0x1234", 5000, 0, [token], [1], {'from': accounts[0]})
    gov.newVote("0x1234", 5000, 0, [token, token2], [1, 2], {'from': accounts[0]})


def test_vote(gov):
    rpc.sleep(210)
    gov.voteOnProposal("0x1234", 1, {'from': accounts[1]})
    gov.voteOnProposal("0x1234", 0, {'from': accounts[3]})
    gov.voteOnProposal("0x1234", 1, {'from': accounts[5]})
    gov.voteOnProposal("0x1234", 1, {'from': accounts[8]})


def test_vote_invalid(gov):
    with pytest.reverts("dev: invalid vote"):
        gov.voteOnProposal("0x1234", 2, {'from': accounts[1]})


def test_vote_invalid_id(gov):
    rpc.sleep(210)
    with pytest.reverts("dev: invalid id"):
        gov.voteOnProposal("0x1111", 1, {'from': accounts[1]})


def test_vote_proposal_closed(gov):
    rpc.sleep(310)
    gov.closeProposal("0x1234", {'from': accounts[0]})
    with pytest.reverts("dev: proposal has closed"):
        gov.voteOnProposal("0x1234", 1, {'from': accounts[1]})


def test_vote_ended(gov):
    rpc.sleep(310)
    with pytest.reverts("dev: voting has finished"):
        gov.voteOnProposal("0x1234", 1, {'from': accounts[1]})


def test_vote_already_voted(gov):
    rpc.sleep(210)
    gov.voteOnProposal("0x1234", 1, {'from': accounts[1]})
    with pytest.reverts("dev: already voted"):
        gov.voteOnProposal("0x1234", 1, {'from': accounts[1]})


def test_vote_not_started(gov):
    with pytest.reverts("dev: vote has not started"):
        gov.voteOnProposal("0x1234", 1, {'from': accounts[1]})
