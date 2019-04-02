#!/usr/bin/python3

from brownie import *
from scripts.deployment import main


def setup():
    main(SecurityToken)
    global token, issuer, cust
    token = SecurityToken[0]
    issuer = IssuingEntity[0]
    cust = OwnedCustodian.deploy(a[0], [a[0]], 1)
    token.mint(issuer, 1000000, {'from': a[0]})


def add_custodian():
    '''add custodian'''
    issuer.addCustodian(cust, {'from': a[0]})
    check.equal(issuer.getID(cust), cust.ownerID())


def add_custodian_twice():
    '''add custodian - aleady added'''
    issuer.addCustodian(cust, {'from': a[0]})
    issuer.addCustodian(cust, {'from': a[0]})
    check.equal(issuer.getID(cust), cust.ownerID())