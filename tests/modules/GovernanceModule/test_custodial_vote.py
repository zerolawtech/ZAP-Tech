#!/usr/bin/python3

import pytest

from brownie import accounts, rpc


@pytest.fixture(scope="module", autouse=True)
def setup(proposal, gov, share, share2, cust):
    gov.newVote("0x1234", 5000, 0, [share], [1], {'from': accounts[0]})
    gov.newVote("0x1234", 5000, 0, [share, share2], [1, 2], {'from': accounts[0]})
    for i in range(1, 4):
        share.transfer(cust, 500, {'from': accounts[i]})


def test_vote(gov, cust):
    rpc.sleep(210)
    gov.voteOnProposal("0x1234", 1, {'from': accounts[1]})
    gov.custodialVoteOnProposal("0x1234", cust, {'from': accounts[1]})
    gov.voteOnProposal("0x1234", 1, {'from': accounts[4]})
    gov.custodialVoteOnProposal("0x1234", cust, {'from': accounts[4]})
    gov.voteOnProposal("0x1234", 1, {'from': accounts[8]})
    gov.custodialVoteOnProposal("0x1234", cust, {'from': accounts[8]})


def test_vote_invalid(gov, cust):
    with pytest.reverts("dev: proposal not active"):
        gov.custodialVoteOnProposal("0x1111", cust, {'from': accounts[1]})


def test_vote_ended(gov, cust):
    rpc.sleep(210)
    gov.voteOnProposal("0x1234", 1, {'from': accounts[1]})
    rpc.sleep(110)
    with pytest.reverts("dev: voting has finished"):
        gov.custodialVoteOnProposal("0x1234", cust, {'from': accounts[1]})


def test_custodial_has_not_voted(gov, cust):
    rpc.sleep(210)
    gov.voteOnProposal("0x1234", 1, {'from': accounts[2]})
    with pytest.reverts("dev: has not voted"):
        gov.custodialVoteOnProposal("0x1234", cust, {'from': accounts[1]})


def test_custodial_already_voted(gov, cust):
    rpc.sleep(210)
    gov.voteOnProposal("0x1234", 1, {'from': accounts[1]})
    gov.custodialVoteOnProposal("0x1234", cust, {'from': accounts[1]})
    with pytest.reverts("dev: has voted with custodian"):
        gov.custodialVoteOnProposal("0x1234", cust, {'from': accounts[1]})
