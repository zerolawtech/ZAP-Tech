#!/usr/bin/python3

import pytest

from brownie import accounts, rpc

@pytest.fixture(scope="module", autouse=True)
def setup(proposal, gov, token, token2):
    gov.newVote("0x1234", 5000, 0, [token], [1], {'from': accounts[0]})
    gov.newVote("0x1234", 5000, 0, [token, token2], [1, 2], {'from': accounts[0]})


def test_close_proposal(gov):
    rpc.sleep(210)
    gov.voteOnProposal("0x1234", 1, {'from': accounts[1]})
    rpc.sleep(110)
    gov.closeProposal("0x1234", {'from': accounts[0]})


def test_close_proposal_no_votes(gov):
    rpc.sleep(310)
    gov.closeProposal("0x1234", {'from': accounts[0]})


def test_close_proposal_not_ended(gov):
    with pytest.reverts("dev: voting has not finished"):
        gov.closeProposal("0x1234", {'from': accounts[0]})


def test_close_proposal_invalid_id(gov):
    with pytest.reverts("dev: proposal not active"):
        gov.closeProposal("0x1111", {'from': accounts[0]})


def test_close_proposal_already_closed(gov):
    rpc.sleep(310)
    gov.closeProposal("0x1234", {'from': accounts[0]})
    with pytest.reverts("dev: proposal not active"):
        gov.closeProposal("0x1234", {'from': accounts[0]})


def test_close_proposal_no_end_not_passing(gov, cptime, token3):
    gov.newProposal(
        "0xffff",
        cptime,
        cptime + 100,
        0,
        "test proposal",
        "0" * 40,
        "0x",
        {'from': accounts[0]}
    )
    gov.newVote("0xffff", 5000, 0, [token3], [1], {'from': accounts[0]})
    rpc.sleep(210)
    with pytest.reverts("dev: proposal has not passed"):
        gov.closeProposal("0xffff", {'from': accounts[0]})


def test_close_proposal_no_end_passing(gov, token3, cptime):
    gov.newProposal(
        "0xffff",
        cptime,
        cptime + 100,
        0,
        "test proposal",
        "0" * 40,
        "0x",
        {'from': accounts[0]}
    )
    gov.newVote("0xffff", 5000, 0, [token3], [1], {'from': accounts[0]})
    rpc.sleep(210)
    gov.voteOnProposal("0xffff", 1, {'from': accounts[5]})
    gov.closeProposal("0xffff", {'from': accounts[0]})
