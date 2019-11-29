#!/usr/bin/python3

import pytest
import time

from brownie import accounts


@pytest.fixture(scope="module")
def cp(MultiCheckpointModule, org, share):
    cp = accounts[0].deploy(MultiCheckpointModule, org)
    org.attachModule(share, cp, {'from': accounts[0]})
    yield cp


@pytest.fixture(scope="module")
def gov(GovernanceModule, org, cp):
    gov = accounts[0].deploy(GovernanceModule, org, cp)
    org.setGovernance(gov, {'from': accounts[0]})
    yield gov


@pytest.fixture(scope="module")
def share2(BookShare, org, cp):
    t = accounts[0].deploy(BookShare, org, "", "", 1000000)
    org.addOrgShare(t, {'from': accounts[0]})
    org.attachModule(t, cp, {'from': accounts[0]})
    yield t


@pytest.fixture(scope="module")
def share3(BookShare, org, cp):
    t = accounts[0].deploy(BookShare, org, "", "", 1000000)
    org.addOrgShare(t, {'from': accounts[0]})
    org.attachModule(t, cp, {'from': accounts[0]})
    yield t


@pytest.fixture(scope="module")
def cptime():
    yield int(time.time() + 100)


@pytest.fixture(scope="module")
def proposal(approve_many, cp, share, share2, share3, gov, cptime):
    for i in range(1, 4):
        share.mint(accounts[i], 1000, {'from': accounts[0]})
    for i in range(3, 6):
        share2.mint(accounts[i], 1000, {'from': accounts[0]})
    share3.mint(accounts[5], 1000, {'from': accounts[0]})
    cp.newCheckpoint(share, cptime, {'from': accounts[0]})
    cp.newCheckpoint(share2, cptime, {'from': accounts[0]})
    cp.newCheckpoint(share3, cptime, {'from': accounts[0]})
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
