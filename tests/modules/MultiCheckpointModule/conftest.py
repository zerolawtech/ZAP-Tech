#!/usr/bin/python3

import pytest

from brownie import accounts, rpc


@pytest.fixture(scope="module")
def cp(MultiCheckpointModule, issuer, token):
    cp = accounts[0].deploy(MultiCheckpointModule, issuer)
    issuer.attachModule(token, cp, {'from': accounts[0]})
    yield cp


@pytest.fixture
def cptime():
    yield rpc.time() + 100
