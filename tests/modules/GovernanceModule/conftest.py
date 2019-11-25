#!/usr/bin/python3

import pytest
import time

from brownie import accounts


@pytest.fixture(scope="module")
def cp(MultiCheckpointModule, org, token):
    cp = accounts[0].deploy(MultiCheckpointModule, org)
    org.attachModule(token, cp, {'from': accounts[0]})
    yield cp


@pytest.fixture(scope="module")
def gov(GovernanceModule, org, cp):
    gov = accounts[0].deploy(GovernanceModule, org, cp)
    org.setGovernance(gov, {'from': accounts[0]})
    yield gov


@pytest.fixture(scope="module")
def token2(SecurityToken, org, cp):
    t = accounts[0].deploy(SecurityToken, org, "", "", 1000000)
    org.addToken(t, {'from': accounts[0]})
    org.attachModule(t, cp, {'from': accounts[0]})
    yield t


@pytest.fixture(scope="module")
def token3(SecurityToken, org, cp):
    t = accounts[0].deploy(SecurityToken, org, "", "", 1000000)
    org.addToken(t, {'from': accounts[0]})
    org.attachModule(t, cp, {'from': accounts[0]})
    yield t


@pytest.fixture(scope="module")
def cptime():
    yield int(time.time() + 100)


@pytest.fixture(scope="module")
def proposal(approve_many, cp, token, token2, token3, gov, cptime):
    for i in range(1, 4):
        token.mint(accounts[i], 1000, {'from': accounts[0]})
    for i in range(3, 6):
        token2.mint(accounts[i], 1000, {'from': accounts[0]})
    token3.mint(accounts[5], 1000, {'from': accounts[0]})
    cp.newCheckpoint(token, cptime, {'from': accounts[0]})
    cp.newCheckpoint(token2, cptime, {'from': accounts[0]})
    cp.newCheckpoint(token3, cptime, {'from': accounts[0]})
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
