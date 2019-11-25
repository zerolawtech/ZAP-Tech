#!/usr/bin/python3

import pytest

from brownie import accounts, compile_source

module_source = """
pragma solidity 0.4.25;

contract TestModule {

    address owner;

    constructor(address _owner) public { owner = _owner; }
    function getOwner() external view returns (address) { return owner; }

    function getPermissions()
        external
        pure
        returns
    (
        bytes4[] permissions,
        bytes4[] hooks,
        uint256 hookBools
    )
    {
        return (permissions, hooks, 0);
    }

}"""


@pytest.fixture(scope="module")
def TestModule():
    yield compile_source(module_source).TestModule


@pytest.fixture(scope="module")
def module_token(TestModule, token):
    module = accounts[0].deploy(TestModule, token)
    yield module


@pytest.fixture(scope="module")
def module_org(TestModule, org):
    module = accounts[0].deploy(TestModule, org)
    yield module


def test_attach_token(org, token, module_token):
    '''attach a token module'''
    assert token.isActiveModule(module_token) is False
    org.attachModule(token, module_token, {'from': accounts[0]})
    assert token.isActiveModule(module_token) is True


def test_detach_token(org, token, module_token):
    '''detach a token module'''
    org.attachModule(token, module_token, {'from': accounts[0]})
    org.detachModule(token, module_token, {'from': accounts[0]})
    assert token.isActiveModule(module_token) is False


def test_attach_via_token(token, module_token):
    '''cannot attach directly via token'''
    with pytest.reverts("dev: only org"):
        token.attachModule(module_token, {'from': accounts[0]})


def test_detach_via_token(org, token, module_token):
    '''cannot detach directly via token'''
    org.attachModule(token, module_token, {'from': accounts[0]})
    with pytest.reverts("dev: only org"):
        token.detachModule(module_token, {'from': accounts[0]})


def test_attach_org(org, token, module_org):
    '''attach an org module'''
    assert token.isActiveModule(module_org) is False
    org.attachModule(token, module_org, {'from': accounts[0]})
    assert token.isActiveModule(module_org) is True


def test_detach_org(org, token, module_org):
    '''detach an org module'''
    org.attachModule(token, module_org, {'from': accounts[0]})
    org.detachModule(token, module_org, {'from': accounts[0]})
    assert token.isActiveModule(module_org) is False


def test_already_active(org, token, module_org, module_token):
    '''attach already active module'''
    org.attachModule(token, module_org, {'from': accounts[0]})
    with pytest.reverts("dev: already active"):
        org.attachModule(token, module_org, {'from': accounts[0]})
    org.attachModule(token, module_token, {'from': accounts[0]})
    with pytest.reverts("dev: already active"):
        org.attachModule(token, module_token, {'from': accounts[0]})


def test_token_locked(org, token, module_token):
    '''attach and detach - locked token'''
    org.setTokenRestriction(token, True, {'from': accounts[0]})
    org.attachModule(token, module_token, {'from': accounts[0]})
    org.detachModule(token, module_token, {'from': accounts[0]})


def test_attach_unknown_target(org, module_token):
    '''attach and detach - unknown target'''
    with pytest.reverts("dev: unknown target"):
        org.attachModule(accounts[0], module_token, {'from': accounts[0]})
    with pytest.reverts("dev: unknown target"):
        org.detachModule(accounts[0], module_token, {'from': accounts[0]})
