#!/usr/bin/python3

from brownie import *
from scripts.deployment import main 

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


def setup():
    main(SecurityToken)
    global token, issuer, TestModule, module
    token = SecurityToken[0]
    issuer = IssuingEntity[0]
    TestModule = compile_source(module_source)[0]
    module = TestModule.deploy(a[0], token)

def attach():
    '''attach a module'''
    module = TestModule.deploy(a[0], token)
    check.false(token.isActiveModule(module))
    check.false(issuer.isActiveModule(module))
    issuer.attachModule(token, module, {'from': a[0]})
    check.true(token.isActiveModule(module))
    check.false(issuer.isActiveModule(module))

def detach():
    '''attach a module'''
    module = TestModule.deploy(a[0], token)
    issuer.attachModule(token, module, {'from': a[0]})
    issuer.detachModule(token, module, {'from': a[0]})
    check.false(token.isActiveModule(module))
    check.false(issuer.isActiveModule(module))