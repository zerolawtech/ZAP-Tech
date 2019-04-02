#!/usr/bin/python3

from brownie import *
from scripts.deployment import main 

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


def setup():
    main(SecurityToken)
    global token, issuer
    token = SecurityToken[0]
    issuer = IssuingEntity[0]
    token.mint(issuer, 100000, {'from': a[0]})


def token_checkTransfer():
    source = '''checkTransfer(
        address[2] _addr,
        bytes32 _authID,
        bytes32[2] _id,
        uint8[2] _rating,
        uint16[2] _country,
        uint256 _value'''
    _hook(token, token.checkTransfer, (a[0], a[1], 1000), source, "0x70aaf928")


def token_transferTokens():
    source = '''transferTokens(
        address[2] _addr,
        bytes32[2] _id,
        uint8[2] _rating,
        uint16[2] _country,
        uint256 _value'''
    _hook(token, token.transfer, (a[1], 1000), source, "0x35a341da")


def token_transferTokensCustodian(skip=True):
    source = '''transferTokensCustodian(
        address _custodian,
        address[2] _addr,
        bytes32[2] _id,
        uint8[2] _rating,
        uint16[2] _country,
        uint256 _value'''
    _hook(token, x, (), source, "0x8b5f1240")


def token_modifyAuthorizedSupply():
    source = '''modifyAuthorizedSupply(
        address _token,
        uint256 _oldSupply,
        uint256 _newSupply'''
    _hook(token, token.modifyAuthorizedSupply, (100000000,), source, "0xb1a1a455")


def token_totalSupplyChanged():
    source = '''totalSupplyChanged(
        address _addr,
        bytes32 _id,
        uint8 _rating,
        uint16 _country,
        uint256 _old,
        uint256 _new'''
    _hook(token, token.burn, (issuer, 1000), source, "0x741b5078")
    _hook(token, token.mint, (a[2], 1000), source, "0x741b5078")


def issuer_checkTransfer():
    source = '''checkTransfer(
        address _token,
        bytes32 _authID,
        bytes32[2] _id,
        uint8[2] _rating,
        uint16[2] _country'''
    _hook(issuer, token.checkTransfer, (a[0], a[1], 1000), source, "0x9a5150fc")

def issuer_tokenTotalSupplyChanged():
    source = '''tokenTotalSupplyChanged(
        address _token,
        bytes32 _id,
        uint8 _rating,
        uint16 _country,
        uint256 _old,
        uint256 _new'''
    _hook(issuer, token.burn, (issuer, 1000), source, "0xb446f3ca")
    _hook(issuer, token.mint, (a[2], 1000), source, "0xb446f3ca")


def custodian_sentTokens():
    source = '''sentTokens(
        address _token,
        address _to,
        uint256 _value'''
    "0x31b45d35"

def custodian_receivedTokens():
    source = '''receivedTokens(
        address _token,
        address _from,
        uint256 _value'''
    "0xa0e7f751"


def custodian_internalTransfer():
    source = '''internalTransfer(
        address _token,
        address _from,
        address _to,
        uint256 _value'''
    "0x7054b724"

def _hook(contract, fn, args, source, sig):
    args = list(args)+[{'from': a[0]}]
    module = compile_source(module_source.format(sig, source))[0].deploy(a[0], contract)
    fn(*args)
    issuer.attachModule(contract, module, {'from': a[0]})
    fn(*args)
    module.setReturn(False, {'from': a[0]})
    check.reverts(fn, args)
    issuer.detachModule(contract, module, {'from': a[0]})
    fn(*args)