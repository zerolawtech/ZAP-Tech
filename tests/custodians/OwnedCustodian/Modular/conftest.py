#!/usr/bin/python3

import pytest


@pytest.fixture(scope="module", autouse=True)
def modular_setup(approve_many, token, org, accounts):
    token.mint(org, 100000, {'from': accounts[0]})
    token.transfer(accounts[2], 10000, {'from': accounts[0]})
