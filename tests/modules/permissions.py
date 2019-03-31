#!/usr/bin/python3

from brownie import *
from scripts.deployment import main 
from eth_abi import encode_abi

module_source = """
pragma solidity 0.4.25;

contract TestModule {{

    address owner;

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
        bytes4[] memory _permissions = new bytes4[](1);
        _permissions[0] = {};
        return (_permissions, hooks, 0);
    }}

    function test(bytes _data) external {{
        require(owner.call(_data));
    }}

}}"""


def setup():
    main(SecurityToken)
    global token, issuer
    token = SecurityToken[0]
    issuer = IssuingEntity[0]

def is_permitted():
    '''check permitted'''
    module = compile_source(module_source.format("0xbb2a8522"))[0].deploy(a[0], token)
    check.false(token.isPermittedModule(module, "0xbb2a8522"))
    check.false(issuer.isPermittedModule(module, "0xbb2a8522"))
    issuer.attachModule(token, module, {'from': a[0]})
    check.true(token.isPermittedModule(module, "0xbb2a8522"))
    check.false(issuer.isPermittedModule(module, "0xbb2a8522"))
    issuer.detachModule(token, module, {'from': a[0]})
    check.false(token.isPermittedModule(module, "0xbb2a8522"))
    check.false(issuer.isPermittedModule(module, "0xbb2a8522"))


def token_detachModule():
    '''detach'''
    module = compile_source(module_source.format("0xbb2a8522"))[0].deploy(a[0], token)
    issuer.attachModule(token, module, {'from': a[0]})
    module.test(token.detachModule.encode_abi(module), {'from': a[0]})