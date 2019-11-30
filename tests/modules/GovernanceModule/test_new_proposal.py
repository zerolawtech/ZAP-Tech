#!/usr/bin/python3

import pytest

from brownie import accounts

proposal_inputs = [
    "0x1234",
    1500000000,
    2000000000,
    2100000000,
    "test proposal",
    "0" * 40,
    "0x",
]


@pytest.fixture()
def pinputs():
    yield proposal_inputs.copy() + [{"from": accounts[0]}]


def test_new_proposal(gov, pinputs):
    gov.newProposal(*pinputs)


def test_new_proposal_no_end(gov, pinputs):
    pinputs[3] = 0
    gov.newProposal(*pinputs)


def test_new_proposal_exists(gov, pinputs):
    gov.newProposal(*pinputs)
    with pytest.reverts("dev: proposal already exists"):
        gov.newProposal(*pinputs)


def test_new_proposal_start_before_now(gov, pinputs):
    pinputs[2] = 151000000
    with pytest.reverts("dev: start < now"):
        gov.newProposal(*pinputs)


def test_new_proposal_start_before_cp(gov, pinputs):
    pinputs[1] = 2100000000
    with pytest.reverts("dev: start < checkpoint"):
        gov.newProposal(*pinputs)


def test_new_proposal_end_before_start(gov, pinputs):
    pinputs[3] = 190000000
    with pytest.reverts("dev: end < start"):
        gov.newProposal(*pinputs)
