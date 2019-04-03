#!/usr/bin/python3

from brownie import *
from scripts.deployment import main 

module_source = """
pragma solidity 0.4.25;

interface Modular {
    function setHook(bytes4, bool, bool) external returns (bool);
    function setHookTags(bytes4, bool, bytes1, bytes1[]) external returns (bool);
    function clearHookTags(bytes4, bytes1[]) external returns (bool);
}

contract TestModule {

    Modular owner;
    bool hookReturn = true;

    constructor(address _owner) public { owner = Modular(_owner); }
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
        bytes4[] memory _hooks = new bytes4[](2);
        _hooks[0] = 0x2d79c6d7;
        _hooks[1] = 0xead529f5;
        return (permissions, _hooks, 0);
    }

    function setActive(bool _return) external {
        hookReturn = _return;
    }

    function checkTransferRange(
        address[2] _addr,
        bytes32 _authID,
        bytes32[2] _id,
        uint8[2] _rating,
        uint16[2] _country,
        uint48[2] _range
    )
        external
        view
        returns (bool)
    {

    }

    function transferTokenRange(
        address[2] _addr,
        bytes32[2] _id,
        uint8[2] _rating,
        uint16[2] _country,
        uint48[2] _range
    )
        external
        returns (bool);

}"""


def setup():
    main(NFToken)
    global issuer, nft, cust
    nft = NFToken[0]
    issuer = IssuingEntity[0]
    cust = OwnedCustodian.deploy(a[0], [a[0]], 1)
    issuer.addCustodian(cust, {'from': a[0]})
    nft.mint(issuer, 100000, 0, "0x00", {'from': a[0]})
    print(compile_source(module_source))