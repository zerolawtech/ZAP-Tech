#!/usr/bin/python3

from brownie import *
from scripts.deployment import main


def setup():
    global issuer, token, options
    token, issuer, _ = main(SecurityToken, (1,), (1,))
    options = a[0].deploy(VestedOptions, token, issuer, 1, 1000, 100, a[0])
    issuer.attachModule(token, options, {'from': a[0]})


def permissions():
    check.true(token.isPermittedModule(options, token.mint.signature))


def hooks():
    result = options.getPermissions()
    check.equal(result['hooks'], ('0x741b5078',))
    check.equal(result['hookBools'], 2**256 - 1)
