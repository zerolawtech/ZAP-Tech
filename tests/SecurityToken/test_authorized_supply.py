#!/usr/bin/python3

import pytest

from brownie import accounts, compile_source

module_source = '''pragma solidity 0.4.25;
contract TestGovernance {
    address public orgCode;
    bool result;
    constructor(address _org) public { orgCode = _org; }
    function setResult(bool _result) external { result = _result; }
    function modifyAuthorizedSupply(address, uint256) external returns (bool) { return result; }
}'''


@pytest.fixture(scope="module")
def gov(org):
    project = compile_source(module_source)
    g = project.TestGovernance.deploy(org, {'from': accounts[0]})
    org.setGovernance(g, {'from': accounts[0]})
    yield g


def test_authorized_supply(share):
    '''modify authorized supply'''
    share.modifyAuthorizedSupply(10000, {'from': accounts[0]})
    assert share.authorizedSupply() == 10000
    assert share.totalSupply() == 0
    share.modifyAuthorizedSupply(0, {'from': accounts[0]})
    assert share.authorizedSupply() == 0
    assert share.totalSupply() == 0
    share.modifyAuthorizedSupply(1234567, {'from': accounts[0]})
    assert share.authorizedSupply(), 1234567
    assert share.totalSupply() == 0
    share.modifyAuthorizedSupply(2400000000, {'from': accounts[0]})
    assert share.authorizedSupply(), 2400000000
    assert share.totalSupply() == 0


def test_authorized_supply_governance_false(share, gov):
    '''modify authorized supply - blocked by governance module'''
    gov.setResult(False, {'from': accounts[0]})
    with pytest.reverts("Action has not been approved"):
        share.modifyAuthorizedSupply(10000, {'from': accounts[0]})


def test_authorized_supply_governance_true(share, gov):
    '''modify authorized supply - allowed by governance module'''
    gov.setResult(True, {'from': accounts[0]})
    share.modifyAuthorizedSupply(10000, {'from': accounts[0]})


def test_authorized_supply_governance_removed(org, share, gov):
    '''modify authorized supply - removed governance module'''
    gov.setResult(False, {'from': accounts[0]})
    with pytest.reverts("Action has not been approved"):
        share.modifyAuthorizedSupply(10000, {'from': accounts[0]})
    org.setGovernance("0" * 40, {'from': accounts[0]})
    share.modifyAuthorizedSupply(10000, {'from': accounts[0]})
