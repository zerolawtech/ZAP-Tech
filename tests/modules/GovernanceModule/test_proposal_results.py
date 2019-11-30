#!/usr/bin/python3

import pytest

from brownie import accounts, rpc


@pytest.fixture(scope="module", autouse=True)
def setup(proposal):
    pass


# balances: a[1]    a[2]    a[3]    a[4]    a[5]
# share:    1000    1000    1000    0       0
# share2:   0       0       1000    1000    1000
# share3:   0       0       0       0       1000


def test_single_vote_no_quorum_pass(gov, share):
    gov.newVote("0x1234", 6600, 0, [share], [1], {"from": accounts[0]})
    rpc.sleep(210)
    gov.voteOnProposal("0x1234", 1, {"from": accounts[1]})
    gov.voteOnProposal("0x1234", 1, {"from": accounts[2]})
    gov.voteOnProposal("0x1234", 0, {"from": accounts[3]})
    rpc.sleep(110)
    gov.closeProposal("0x1234", {"from": accounts[0]})
    assert gov.getProposalState("0x1234") == 5
    assert gov.getVotePct("0x1234", 0) == (6666, 0)


def test_single_vote_no_quorum_fail(gov, share):
    gov.newVote("0x1234", 5000, 0, [share], [1], {"from": accounts[0]})
    rpc.sleep(210)
    gov.voteOnProposal("0x1234", 1, {"from": accounts[1]})
    gov.voteOnProposal("0x1234", 0, {"from": accounts[2]})
    gov.voteOnProposal("0x1234", 0, {"from": accounts[3]})
    rpc.sleep(110)
    gov.closeProposal("0x1234", {"from": accounts[0]})
    assert gov.getProposalState("0x1234") == 4
    assert gov.getVotePct("0x1234", 0) == (3333, 0)


def test_single_vote_quorum_pass(gov, share):
    gov.newVote("0x1234", 5000, 6600, [share], [1], {"from": accounts[0]})
    rpc.sleep(210)
    gov.voteOnProposal("0x1234", 1, {"from": accounts[1]})
    gov.voteOnProposal("0x1234", 0, {"from": accounts[2]})
    rpc.sleep(110)
    gov.closeProposal("0x1234", {"from": accounts[0]})
    assert gov.getProposalState("0x1234") == 5
    assert gov.getVotePct("0x1234", 0) == (5000, 6666)


def test_single_vote_quorum_fail(gov, share):
    gov.newVote("0x1234", 5010, 6600, [share], [1], {"from": accounts[0]})
    rpc.sleep(210)
    gov.voteOnProposal("0x1234", 1, {"from": accounts[1]})
    gov.voteOnProposal("0x1234", 0, {"from": accounts[2]})
    rpc.sleep(110)
    gov.closeProposal("0x1234", {"from": accounts[0]})
    assert gov.getProposalState("0x1234") == 4
    assert gov.getVotePct("0x1234", 0) == (5000, 6666)


def test_single_vote_quorum_not_reached(gov, share):
    gov.newVote("0x1234", 5000, 6700, [share], [1], {"from": accounts[0]})
    rpc.sleep(210)
    gov.voteOnProposal("0x1234", 1, {"from": accounts[1]})
    gov.voteOnProposal("0x1234", 0, {"from": accounts[2]})
    rpc.sleep(110)
    gov.closeProposal("0x1234", {"from": accounts[0]})
    assert gov.getProposalState("0x1234") == 3
    assert gov.getVotePct("0x1234", 0) == (5000, 6666)


def test_multi_vote_no_quorum_pass(gov, share, share2):
    gov.newVote("0x1234", 6600, 0, [share], [1], {"from": accounts[0]})
    gov.newVote("0x1234", 6600, 0, [share, share2], [1, 2], {"from": accounts[0]})
    rpc.sleep(210)
    gov.voteOnProposal("0x1234", 0, {"from": accounts[1]})
    gov.voteOnProposal("0x1234", 1, {"from": accounts[2]})
    gov.voteOnProposal("0x1234", 1, {"from": accounts[3]})
    gov.voteOnProposal("0x1234", 1, {"from": accounts[4]})
    gov.voteOnProposal("0x1234", 0, {"from": accounts[5]})
    rpc.sleep(110)
    gov.closeProposal("0x1234", {"from": accounts[0]})
    assert gov.getProposalState("0x1234") == 5
    assert gov.getVotePct("0x1234", 0) == (6666, 0)
    assert gov.getVotePct("0x1234", 1) == (6666, 0)


def test_multi_vote_no_quorum_fail(gov, share, share2):
    gov.newVote("0x1234", 6600, 0, [share], [1], {"from": accounts[0]})
    gov.newVote("0x1234", 6700, 0, [share, share2], [1, 2], {"from": accounts[0]})
    rpc.sleep(210)
    gov.voteOnProposal("0x1234", 0, {"from": accounts[1]})
    gov.voteOnProposal("0x1234", 1, {"from": accounts[2]})
    gov.voteOnProposal("0x1234", 1, {"from": accounts[3]})
    gov.voteOnProposal("0x1234", 1, {"from": accounts[4]})
    gov.voteOnProposal("0x1234", 0, {"from": accounts[5]})
    rpc.sleep(110)
    gov.closeProposal("0x1234", {"from": accounts[0]})
    assert gov.getProposalState("0x1234") == 4
    assert gov.getVoteResult("0x1234", 0) == 5
    assert gov.getVotePct("0x1234", 0) == (6666, 0)
    assert gov.getVoteResult("0x1234", 1) == 4
    assert gov.getVotePct("0x1234", 1) == (6666, 0)


def test_multi_vote_quorum_pass(gov, share, share2):
    gov.newVote("0x1234", 5000, 6600, [share], [1], {"from": accounts[0]})
    gov.newVote("0x1234", 5000, 6600, [share, share2], [1, 2], {"from": accounts[0]})
    rpc.sleep(210)
    gov.voteOnProposal("0x1234", 0, {"from": accounts[2]})
    gov.voteOnProposal("0x1234", 1, {"from": accounts[3]})
    gov.voteOnProposal("0x1234", 0, {"from": accounts[4]})
    rpc.sleep(110)
    gov.closeProposal("0x1234", {"from": accounts[0]})
    assert gov.getProposalState("0x1234") == 5
    assert gov.getVotePct("0x1234", 0) == (5000, 6666)
    assert gov.getVotePct("0x1234", 1) == (5000, 6666)


def test_multi_vote_quorum_fail(gov, share, share2):
    gov.newVote("0x1234", 5010, 6600, [share], [1], {"from": accounts[0]})
    gov.newVote("0x1234", 5000, 6600, [share, share2], [1, 2], {"from": accounts[0]})
    rpc.sleep(210)
    gov.voteOnProposal("0x1234", 0, {"from": accounts[2]})
    gov.voteOnProposal("0x1234", 1, {"from": accounts[3]})
    gov.voteOnProposal("0x1234", 0, {"from": accounts[4]})
    rpc.sleep(110)
    gov.closeProposal("0x1234", {"from": accounts[0]})
    assert gov.getProposalState("0x1234") == 4
    assert gov.getVoteResult("0x1234", 0) == 4
    assert gov.getVoteResult("0x1234", 1) == 5
    assert gov.getVotePct("0x1234", 0) == (5000, 6666)
    assert gov.getVotePct("0x1234", 1) == (5000, 6666)


def test_multi_vote_quorum_not_reached(gov, share, share2):
    gov.newVote("0x1234", 5000, 6600, [share], [1], {"from": accounts[0]})
    gov.newVote("0x1234", 5000, 6700, [share, share2], [1, 2], {"from": accounts[0]})
    rpc.sleep(210)
    gov.voteOnProposal("0x1234", 0, {"from": accounts[2]})
    gov.voteOnProposal("0x1234", 1, {"from": accounts[3]})
    gov.voteOnProposal("0x1234", 0, {"from": accounts[4]})
    rpc.sleep(110)
    gov.closeProposal("0x1234", {"from": accounts[0]})
    assert gov.getProposalState("0x1234") == 3
    assert gov.getVoteResult("0x1234", 0) == 5
    assert gov.getVoteResult("0x1234", 1) == 3
    assert gov.getVotePct("0x1234", 0) == (5000, 6666)
    assert gov.getVotePct("0x1234", 1) == (5000, 6666)
