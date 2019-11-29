#!/usr/bin/python3

import functools
import pytest

from brownie import accounts, compile_source

module_source = """
pragma solidity 0.4.25;

contract TestModule {{

    address owner;
    bool hookReturn = true;

    constructor(address _owner) public {{ owner = _owner; }}
    function getOwner() external view returns (address) {{ return owner; }}

    function getPermissions()
        external
        pure
        returns
    (
        bytes4[] permissions,
        bytes4[] hooks,
        uint256 hookBools
    )
    {{
        bytes4[] memory _hooks = new bytes4[](1);
        _hooks[0] = {};
        return (permissions, _hooks, uint256(0)-1);
    }}

    function setReturn(bool _return) external {{
        hookReturn = _return;
    }}

    function {}) external returns (bool) {{
        if (!hookReturn) {{
            revert();
        }}
        return true;
    }}

}}"""


@pytest.fixture(scope="module", autouse=True)
def testhook(approve_many, org, share):
    share.mint(org, 100000, {'from': accounts[0]})
    hook = functools.partial(_hook, org, share)
    yield hook


def test_checkTransfer(testhook, share):
    source = '''checkTransfer(
        address[2] _addr,
        bytes32 _authID,
        bytes32[2] _id,
        uint8[2] _rating,
        uint16[2] _country,
        uint256 _value'''
    testhook(share.checkTransfer, (accounts[0], accounts[1], 1000), source, "0x70aaf928")


def test_transferShares(testhook, share):
    source = '''transferShares(
        address[2] _addr,
        bytes32[2] _id,
        uint8[2] _rating,
        uint16[2] _country,
        uint256 _value'''
    testhook(share.transfer, (accounts[1], 1000), source, "0x0675a5e0")


def test_transferSharesCustodian(testhook, share, cust):
    source = '''transferSharesCustodian(
        address _custodian,
        address[2] _addr,
        bytes32[2] _id,
        uint8[2] _rating,
        uint16[2] _country,
        uint256 _value'''
    share.transfer(accounts[2], 10000, {'from': accounts[0]})
    share.transfer(cust, 5000, {'from': accounts[2]})
    testhook(cust.transferInternal, (share, accounts[2], accounts[3], 100), source, "0xdc9d1da1")


def test_totalSupplyChanged(testhook, org, share, cust):
    source = '''totalSupplyChanged(
        address _addr,
        bytes32 _id,
        uint8 _rating,
        uint16 _country,
        uint256 _old,
        uint256 _new'''
    testhook(share.burn, (org, 1000), source, "0x741b5078")
    testhook(share.mint, (accounts[2], 1000), source, "0x741b5078")


def _hook(org, share, fn, args, source, sig):
    args = list(args) + [{'from': accounts[0]}]
    source = module_source.format(sig, source)
    project = compile_source(source)
    module = project.TestModule.deploy(share, {'from': accounts[0]})
    fn(*args)
    org.attachModule(share, module, {'from': accounts[0]})
    fn(*args)
    module.setReturn(False, {'from': accounts[0]})
    with pytest.reverts():
        fn(*args)
    org.detachModule(share, module, {'from': accounts[0]})
    fn(*args)
