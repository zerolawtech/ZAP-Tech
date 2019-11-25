#!/usr/bin/python3

import pytest

from brownie import accounts, rpc

optmonths = [0, 100, 100, 100, 100, 100, 0, 0, 0, 0, 0]


@pytest.fixture(scope="module")
def options(VestedOptions, org, token):
    options = accounts[0].deploy(VestedOptions, token, org, 1, 10, 6, accounts[0])
    org.attachModule(token, options, {'from': accounts[0]})
    yield options


def test_get_options_at(options, id1, issueoptions, sleep):
    issueoptions(id1, 10)
    assert options.getOptionsAt(id1, 10, 0) == (0, 500, False, _months(11), optmonths)
    sleep(2)
    assert options.getOptionsAt(id1, 10, 0) == (
        100, 400, False, _months(9), optmonths[2:]
    )
    sleep(8)
    assert options.getOptionsAt(id1, 10, 0) == (500, 0, False, _months(1), [0])
    sleep(1)
    with pytest.reverts():
        options.getOptionsAt(id1, 10, 0)


def test_expire_and_recreate(options, id1, issueoptions, sleep):
    issueoptions(id1, 10)
    sleep(12)
    with pytest.reverts():
        options.getOptionsAt(id1, 10, 0)
    issueoptions(id1, 10)
    options.getOptionsAt(id1, 10, 0)
    with pytest.reverts():
        options.getOptionsAt(id1, 10, 1)
    issueoptions(id1, 10)
    options.getOptionsAt(id1, 10, 0)
    with pytest.reverts():
        options.getOptionsAt(id1, 10, 1)
    sleep(12)
    with pytest.reverts():
        options.getOptionsAt(id1, 10, 0)


def test_multiple(options, id1, issueoptions, sleep):
    issueoptions(id1, 10)
    sleep(6)
    issueoptions(id1, 10)
    assert options.getOptionsAt(id1, 10, 0) == (500, 0, False, _months(5), [0, 0, 0, 0, 0])
    assert options.getOptionsAt(id1, 10, 1) == (0, 500, False, _months(11), optmonths)
    sleep(5)
    assert options.getOptionsAt(id1, 10, 0) == (400, 100, False, _months(6), optmonths[5:])
    with pytest.reverts():
        options.getOptionsAt(id1, 10, 1)


def _months(months):
    return int(rpc.time() // 2592000 + 1) * 2592000 + months * 2592000
