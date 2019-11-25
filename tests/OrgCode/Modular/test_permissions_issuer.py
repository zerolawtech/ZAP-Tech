#!/usr/bin/python3

import pytest

from brownie import accounts, compile_source

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


@pytest.fixture(scope="module", autouse=True)
def setup(approve_many, org, nft, share):
    share.mint(org, 100000, {'from': accounts[0]})
    nft.mint(org, 100000, 0, "0x00", {'from': accounts[0]})


def test_is_permitted(org, share):
    '''check permitted'''
    source = module_source.format('0xbb2a8522')
    project = compile_source(source)
    module = project.TestModule.deploy(share, {'from': accounts[0]})
    assert not share.isPermittedModule(module, "0xbb2a8522")
    org.attachModule(share, module, {'from': accounts[0]})
    assert share.isPermittedModule(module, "0xbb2a8522")
    org.detachModule(share, module, {'from': accounts[0]})
    assert not share.isPermittedModule(module, "0xbb2a8522")


def test_share_detachModule(org, share):
    '''detach module'''
    source = module_source.format('0xbb2a8522')
    project = compile_source(source)
    module = project.TestModule.deploy(share, {'from': accounts[0]})
    with pytest.reverts():
        module.test(share.detachModule.encode_input(module), {'from': accounts[0]})
    org.attachModule(share, module, {'from': accounts[0]})
    module.test(share.detachModule.encode_input(module), {'from': accounts[0]})
    with pytest.reverts():
        module.test(share.detachModule.encode_input(module), {'from': accounts[0]})


def test_share_transferFrom(org, share):
    '''share transferFrom'''
    share.transfer(accounts[2], 5000, {'from': accounts[0]})
    _check_permission(
        org,
        share,
        '0x23b872dd',
        share.transferFrom.encode_input(accounts[2], accounts[3], 3000)
    )
    assert share.balanceOf(accounts[2]) == 2000
    assert share.balanceOf(accounts[3]) == 3000


def test_share_modifyAuthorizedSupply(org, share):
    '''share modifyAuthorizedSupply'''
    _check_permission(
        org,
        share,
        '0xc39f42ed',
        share.modifyAuthorizedSupply.encode_input("10 ether")
    )
    assert share.authorizedSupply() == "10 ether"


def test_share_mint(org, share):
    '''share mint'''
    _check_permission(
        org,
        share,
        '0x40c10f19',
        share.mint.encode_input(accounts[3], 10000)
    )
    assert share.balanceOf(accounts[3]) == 10000


def test_share_burn(org, share):
    '''share burn'''
    share.transfer(accounts[2], 5000, {'from': accounts[0]})
    _check_permission(
        org,
        share,
        '0x9dc29fac',
        share.burn.encode_input(accounts[2], 3000)
    )
    assert share.balanceOf(accounts[2]) == 2000


def test_nft_mint(org, nft):
    '''nft mint'''
    _check_permission(
        org,
        nft,
        "0x15077ec8",
        nft.mint.encode_input(accounts[2], 10000, 0, "0xff11")
    )
    assert nft.balanceOf(accounts[2]) == 10000


def test_nft_burn(org, nft):
    '''nft burn'''
    _check_permission(
        org,
        nft,
        "0x9a0d378b",
        nft.burn.encode_input(1337, 31337)
    )
    assert nft.balanceOf(org) == 70000


def test_nft_modifyRange(org, nft):
    '''nft modifyRange'''
    _check_permission(
        org,
        nft,
        "0x712a516a",
        nft.modifyRange.encode_input(1, 0, "0xabcd")
    )
    assert nft.getRange(1)[1:5] == (1, 100001, 0, "0xabcd")


def test_nft_modifyRanges(org, nft):
    '''nft modifyRanges'''
    _check_permission(
        org,
        nft,
        "0x786500aa",
        nft.modifyRanges.encode_input(100, 200, 0, "0x1111")
    )
    assert nft.getRange(1)[1:5] == (1, 100, 0, "0x0000")
    assert nft.getRange(100)[1:5] == (100, 200, 0, "0x1111")
    assert nft.getRange(200)[1:5] == (200, 100001, 0, "0x0000")


def _check_permission(org, contract, sig, calldata):

    # deploy the module
    source = module_source.format(sig)
    project = compile_source(source)
    module = project.TestModule.deploy(contract, {'from': accounts[0]})

    # check that call fails prior to attaching module
    with pytest.reverts():
        module.test(calldata, {'from': accounts[0]})

    # attach the module and check that the call now succeeds
    org.attachModule(contract, module, {'from': accounts[0]})
    module.test(calldata, {'from': accounts[0]})

    # detach the module and check that the call fails again
    org.detachModule(contract, module, {'from': accounts[0]})
    with pytest.reverts():
        module.test(calldata, {'from': accounts[0]})
