#!/usr/bin/python3

import pytest

from brownie import accounts, rpc


@pytest.fixture(scope="module")
def cp(MultiCheckpointModule, org, token):
    cp = accounts[0].deploy(MultiCheckpointModule, org)
    org.attachModule(token, cp, {'from': accounts[0]})
    yield cp


@pytest.fixture
def cptime():
    yield rpc.time() + 100
