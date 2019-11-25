#!/usr/bin/python3

import pytest

from brownie import accounts, compile_source

module_source = '''pragma solidity 0.4.25;
contract TestGovernance {
    address public org;
    bool result;
    constructor(address _org) public { org = _org; }
    function setResult(bool _result) external { result = _result; }
    function addToken(address) external returns (bool) { return result; }
}'''


@pytest.fixture(scope="module")
def gov(org):
    project = compile_source(module_source)
    gov = project.TestGovernance.deploy(org, {'from': accounts[0]})
    org.setGovernance(gov, {'from': accounts[0]})
    yield gov


@pytest.fixture(scope="module")
def token2(SecurityToken, org, accounts, token):
    t = accounts[0].deploy(SecurityToken, org, "Test Token2", "TS2", 1000000)
    yield t


def test_add_token(org, token2):
    '''add token'''
    org.addToken(token2, {'from': accounts[0]})


def test_add_token_twice(org, token):
    '''add token - already added'''
    with pytest.reverts("dev: already set"):
        org.addToken(token, {'from': accounts[0]})


def test_add_token_wrong_org(org, OrgCode, SecurityToken):
    '''add token - wrong org'''
    org2 = accounts[0].deploy(OrgCode, [accounts[0]], 1)
    token = accounts[0].deploy(SecurityToken, org2, "ABC", "ABC Token", 18)
    with pytest.reverts("dev: wrong owner"):
        org.addToken(token, {'from': accounts[0]})


def test_add_token_governance_true(org, gov, token2):
    '''add token - governance allows'''
    org.setGovernance(gov, {'from': accounts[0]})
    gov.setResult(True, {'from': accounts[0]})
    org.addToken(token2, {'from': accounts[0]})


def test_add_token_governance_false(org, gov, token2):
    '''add token - governance allows'''
    gov.setResult(False, {'from': accounts[0]})
    with pytest.reverts("Action has not been approved"):
        org.addToken(token2, {'from': accounts[0]})


def test_add_token_governance_removed(org, gov, token2):
    '''add token - governance allows'''
    gov.setResult(False, {'from': accounts[0]})
    with pytest.reverts("Action has not been approved"):
        org.addToken(token2, {'from': accounts[0]})
    org.setGovernance("0" * 40, {'from': accounts[0]})
    org.addToken(token2, {'from': accounts[0]})
