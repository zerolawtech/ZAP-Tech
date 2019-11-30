#!/usr/bin/python3

import functools
import pytest

from brownie import accounts, rpc


@pytest.fixture(scope="module")
def options(VestedOptions, org, share):
    o = accounts[0].deploy(VestedOptions, share, org, 1, 100, 6, accounts[0])
    org.attachModule(share, o, {"from": accounts[0]})
    yield o


@pytest.fixture(scope="module")
def issueoptions(options):
    yield functools.partial(_issue, options)


@pytest.fixture
def sleep():
    yield _sleep


def _issue(options, id_, price):
    options.issueOptions(
        id_,
        price,
        False,
        [100, 100, 100, 100, 100],
        [1, 2, 3, 4, 5],
        {"from": accounts[0]},
    )


def _sleep(months):
    now = int(rpc.time() // 2592000 + 1) * 2592000
    rpc.sleep(now - rpc.time() + 1 + 2592000 * (months - 1))
    rpc.mine()
