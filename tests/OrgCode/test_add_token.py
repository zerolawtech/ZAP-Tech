#!/usr/bin/python3

import pytest

from brownie import accounts, compile_source

module_source = """pragma solidity 0.4.25;
contract TestGovernance {
    address public orgCode;
    bool result;
    constructor(address _org) public { orgCode = _org; }
    function setResult(bool _result) external { result = _result; }
    function addOrgShare(address) external returns (bool) { return result; }
}"""


@pytest.fixture(scope="module")
def gov(org):
    project = compile_source(module_source)
    gov = project.TestGovernance.deploy(org, {"from": accounts[0]})
    org.setGovernance(gov, {"from": accounts[0]})
    yield gov


@pytest.fixture(scope="module")
def share2(BookShare, org, accounts, share):
    t = accounts[0].deploy(BookShare, org, "Test Share2", "TS2", 1000000)
    yield t


def test_add_share(org, share2):
    """add share"""
    org.addOrgShare(share2, {"from": accounts[0]})


def test_add_share_twice(org, share):
    """add share - already added"""
    with pytest.reverts("dev: already set"):
        org.addOrgShare(share, {"from": accounts[0]})


def test_add_share_wrong_org(org, OrgCode, BookShare):
    """add share - wrong org"""
    org2 = accounts[0].deploy(OrgCode, [accounts[0]], 1)
    share = accounts[0].deploy(BookShare, org2, "ABC", "ABC Share", 18)
    with pytest.reverts("dev: wrong owner"):
        org.addOrgShare(share, {"from": accounts[0]})


def test_add_share_governance_true(org, gov, share2):
    """add share - governance allows"""
    org.setGovernance(gov, {"from": accounts[0]})
    gov.setResult(True, {"from": accounts[0]})
    org.addOrgShare(share2, {"from": accounts[0]})


def test_add_share_governance_false(org, gov, share2):
    """add share - governance allows"""
    gov.setResult(False, {"from": accounts[0]})
    with pytest.reverts("Action has not been approved"):
        org.addOrgShare(share2, {"from": accounts[0]})


def test_add_share_governance_removed(org, gov, share2):
    """add share - governance allows"""
    gov.setResult(False, {"from": accounts[0]})
    with pytest.reverts("Action has not been approved"):
        org.addOrgShare(share2, {"from": accounts[0]})
    org.setGovernance("0" * 40, {"from": accounts[0]})
    org.addOrgShare(share2, {"from": accounts[0]})
