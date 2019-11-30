#!/usr/bin/python3

import pytest

from brownie import accounts, compile_source

source = """pragma solidity 0.4.25;

contract TestCustodian {

    bytes32 public ownerID = 0x1234;

    function setID (bytes32 _id) public { ownerID = _id; }

}"""


@pytest.fixture(scope="module")
def TestCustodian():
    yield compile_source(source).TestCustodian


@pytest.fixture(scope="module")
def testcust(TestCustodian):
    cust = accounts[0].deploy(TestCustodian)
    yield cust


def test_add(id1, id2, org, testcust):
    """add custodian"""
    org.addCustodian(testcust, {"from": accounts[0]})
    assert org.getID(testcust) == testcust.ownerID()


def test_add_twice(org, testcust, TestCustodian):
    """add custodian - already added"""
    org.addCustodian(testcust, {"from": accounts[0]})
    with pytest.reverts("dev: known address"):
        org.addCustodian(testcust, {"from": accounts[0]})
    c = accounts[1].deploy(TestCustodian)
    with pytest.reverts("dev: known ID"):
        org.addCustodian(c, {"from": accounts[0]})


def test_add_zero_id(org, testcust):
    """add custodian - zero id"""
    testcust.setID(0, {"from": accounts[0]})
    with pytest.reverts("dev: zero ID"):
        org.addCustodian(testcust, {"from": accounts[0]})


def test_add_member_id(share, org, testcust):
    """custodian / member collision - member seen first"""
    share.mint(accounts[2], 100, {"from": accounts[0]})
    id_ = org.getID.call(accounts[2])
    testcust.setID(id_, {"from": accounts[0]})
    with pytest.reverts("dev: known ID"):
        org.addCustodian(testcust, {"from": accounts[0]})


def test_add_member_id2(share, org, testcust):
    """custodian / member collision - custodian seen first"""
    share.mint(org, 100, {"from": accounts[0]})
    id_ = org.getID.call(accounts[2])
    testcust.setID(id_, {"from": accounts[0]})
    org.addCustodian(testcust, {"from": accounts[0]})
    with pytest.reverts():
        share.transfer(accounts[2], 100, {"from": accounts[0]})


def test_cust_auth_id(org, share, testcust, rpc):
    """custodian / authority collisions"""
    org.addAuthority([accounts[-1]], [], 2000000000, 1, {"from": accounts[0]})
    id_ = org.getID(accounts[-1])
    testcust.setID(id_, {"from": accounts[0]})
    with pytest.reverts("dev: authority ID"):
        org.addCustodian(testcust, {"from": accounts[0]})
    rpc.revert()
    testcust.setID(id_, {"from": accounts[0]})
    org.addCustodian(testcust, {"from": accounts[0]})
    with pytest.reverts("dev: known ID"):
        org.addAuthority([accounts[-1]], [], 2000000000, 1, {"from": accounts[0]})
