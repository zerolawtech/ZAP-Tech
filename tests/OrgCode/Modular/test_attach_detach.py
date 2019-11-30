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
def module_share(TestModule, share):
    module = accounts[0].deploy(TestModule, share)
    yield module


@pytest.fixture(scope="module")
def module_org(TestModule, org):
    module = accounts[0].deploy(TestModule, org)
    yield module


def test_attach_share(org, share, module_share):
    """attach a share module"""
    assert share.isActiveModule(module_share) is False
    org.attachModule(share, module_share, {"from": accounts[0]})
    assert share.isActiveModule(module_share) is True


def test_detach_share(org, share, module_share):
    """detach a share module"""
    org.attachModule(share, module_share, {"from": accounts[0]})
    org.detachModule(share, module_share, {"from": accounts[0]})
    assert share.isActiveModule(module_share) is False


def test_attach_via_share(share, module_share):
    """cannot attach directly via share"""
    with pytest.reverts("dev: only orgCode"):
        share.attachModule(module_share, {"from": accounts[0]})


def test_detach_via_share(org, share, module_share):
    """cannot detach directly via share"""
    org.attachModule(share, module_share, {"from": accounts[0]})
    with pytest.reverts("dev: only orgCode"):
        share.detachModule(module_share, {"from": accounts[0]})


def test_attach_org(org, share, module_org):
    """attach an org module"""
    assert share.isActiveModule(module_org) is False
    org.attachModule(share, module_org, {"from": accounts[0]})
    assert share.isActiveModule(module_org) is True


def test_detach_org(org, share, module_org):
    """detach an org module"""
    org.attachModule(share, module_org, {"from": accounts[0]})
    org.detachModule(share, module_org, {"from": accounts[0]})
    assert share.isActiveModule(module_org) is False


def test_already_active(org, share, module_org, module_share):
    """attach already active module"""
    org.attachModule(share, module_org, {"from": accounts[0]})
    with pytest.reverts("dev: already active"):
        org.attachModule(share, module_org, {"from": accounts[0]})
    org.attachModule(share, module_share, {"from": accounts[0]})
    with pytest.reverts("dev: already active"):
        org.attachModule(share, module_share, {"from": accounts[0]})


def test_share_locked(org, share, module_share):
    """attach and detach - locked share"""
    org.setOrgShareRestriction(share, True, {"from": accounts[0]})
    org.attachModule(share, module_share, {"from": accounts[0]})
    org.detachModule(share, module_share, {"from": accounts[0]})


def test_attach_unknown_target(org, module_share):
    """attach and detach - unknown target"""
    with pytest.reverts("dev: unknown target"):
        org.attachModule(accounts[0], module_share, {"from": accounts[0]})
    with pytest.reverts("dev: unknown target"):
        org.detachModule(accounts[0], module_share, {"from": accounts[0]})
