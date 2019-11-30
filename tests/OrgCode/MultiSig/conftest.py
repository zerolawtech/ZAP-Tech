#!/usr/bin/python3

import functools
import pytest

from brownie import accounts, rpc


@pytest.fixture(scope="module")
def multisig(org):
    fn = functools.partial(_multisig, org)
    yield fn


def _multisig(org, fn, *args):
    id1 = org.getID(accounts[-6])
    args = list(args) + [{"from": accounts[-6]}]
    # check for failed call, no permission
    with pytest.reverts("dev: not permitted"):
        fn(*args)
    # give permission and check for successful call
    org.setAuthoritySignatures(id1, [fn.signature], True, {"from": accounts[0]})
    assert "MultiSigCallApproved" in fn(*args).events
    rpc.revert()
    # give permission, threhold to 3, check for success and fails
    org.setAuthoritySignatures(id1, [fn.signature], True, {"from": accounts[0]})
    org.setAuthorityThreshold(id1, 3, {"from": accounts[0]})
    args[-1]["from"] = accounts[-6]
    assert "MultiSigCallApproved" not in fn(*args).events
    with pytest.reverts("dev: repeat caller"):
        fn(*args)
    args[-1]["from"] = accounts[-5]
    assert "MultiSigCallApproved" not in fn(*args).events
    with pytest.reverts("dev: repeat caller"):
        fn(*args)
    args[-1]["from"] = accounts[-4]
    assert "MultiSigCallApproved" in fn(*args).events
