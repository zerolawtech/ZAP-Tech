#!/usr/bin/python3

from brownie import *
from scripts.deployment import main

source = '''pragma solidity 0.4.25;

contract TestCustodian {

    bytes32 public ownerID = 0x1234;

    function setID (bytes32 _id) public { ownerID = _id; }

}'''


def setup():
    main(SecurityToken)
    global token, issuer, TestCustodian, cust
    token = SecurityToken[0]
    issuer = IssuingEntity[0]
    TestCustodian = compile_source(source)[0]
    cust = TestCustodian.deploy(a[0])
    token.mint(issuer, 1000000, {'from': a[0]})


def add():
    '''add custodian'''
    issuer.addCustodian(cust, {'from': a[0]})
    check.equal(issuer.getID(cust), cust.ownerID())


def add_twice():
    '''add custodian - already added'''
    issuer.addCustodian(cust, {'from': a[0]})
    check.reverts(
        issuer.addCustodian,
        (cust, {'from': a[0]}),
        "dev: known address"
    )
    c = TestCustodian.deploy(a[0])
    check.reverts(
        issuer.addCustodian,
        (c, {'from': a[0]}),
        "dev: custodian ID"
    )


def add_zero_id():
    '''add custodian - zero id'''
    cust.setID(0, {'from': a[0]})
    check.reverts(
        issuer.addCustodian,
        (cust, {'from': a[0]}),
        "dev: zero id"
    )