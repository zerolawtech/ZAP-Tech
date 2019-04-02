#!/usr/bin/python3

from brownie import *
from scripts.deployment import main 

module_source = """
pragma solidity 0.4.25;

contract TestModule {{

    address owner;
    bool hookReturn;

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


def setup():
    main(SecurityToken)
    global token, issuer, nft
    token = SecurityToken[0]
    issuer = IssuingEntity[0]
    token.mint(issuer, 100000, {'from': a[0]})
    nft = NFToken.deploy(a[0], issuer, "NFToken", "TST", 1000000)
    issuer.addToken(nft, {'from': a[0]})
    nft.mint(issuer, 100000, 0, "0x00", {'from': a[0]})

def token_checkTransfer():
    fn = '''checkTransfer(
		address[2] _addr,
		bytes32 _authID,
		bytes32[2] _id,
		uint8[2] _rating,
		uint16[2] _country,
		uint256 _value'''
    module = compile_source(module_source.format("0x70aaf928",fn))[0].deploy(a[0], token)
    check.true(token.checkTransfer(a[0], a[1], 1000))
    issuer.attachModule(token, module, {'from': a[0]})
    check.reverts(token.checkTransfer, (a[0], a[1], 1000))
    module.setReturn(True, {'from': a[0]})
    check.true(token.checkTransfer(a[0], a[1], 1000))
    

def token_transferTokens():
    fn = '''transferTokens(
		address[2] _addr,
		bytes32[2] _id,
		uint8[2] _rating,
		uint16[2] _country,
		uint256 _value'''
    module = compile_source(module_source.format("0x35a341da",fn))[0].deploy(a[0], token)
    token.transfer(a[1], 1000, {'from': a[0]})
    issuer.attachModule(token, module, {'from': a[0]})
    check.reverts(token.transfer, (a[1], 1000, {'from': a[0]}))
    module.setReturn(True, {'from': a[0]})
    token.transfer(a[1], 1000, {'from': a[0]})