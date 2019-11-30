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


@pytest.fixture(scope="module")
def check_hooks(cust):
    yield functools.partial(_hook, cust)


def test_custodian_sentShares(check_hooks, share, cust):
    source = """sentShares(
        address _share,
        address _to,
        uint256 _value"""
    share.transfer(cust, 10000, {"from": accounts[0]})
    check_hooks(cust.transfer, (share, accounts[0], 100), source, "0xa110724f")


def test_custodian_receivedShares(check_hooks, share, cust):
    source = """receivedShares(
        address _share,
        address _from,
        uint256 _value"""
    check_hooks(share.transfer, (cust, 1000), source, "0xa000ff88")


def test_custodian_internalTransfer(check_hooks, share, cust):
    source = """internalTransfer(
        address _share,
        address _from,
        address _to,
        uint256 _value"""
    share.transfer(cust, 10000, {"from": accounts[0]})
    check_hooks(
        cust.transferInternal,
        (share, accounts[0], accounts[2], 100),
        source,
        "0x44a29e2a",
    )


def _hook(cust, fn, args, source, sig):
    args = list(args) + [{"from": accounts[0]}]
    source = module_source.format(sig, source)
    project = compile_source(source)
    module = project.TestModule.deploy(cust, {"from": accounts[0]})
    fn(*args)
    cust.attachModule(module, {"from": accounts[0]})
    fn(*args)
    module.setReturn(False, {"from": accounts[0]})
    with pytest.reverts():
        fn(*args)
    cust.detachModule(module, {"from": accounts[0]})
    fn(*args)
