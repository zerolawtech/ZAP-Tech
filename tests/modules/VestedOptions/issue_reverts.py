#!/usr/bin/python3

from brownie import *
from scripts.deployment import main


def setup():
    global issuer, token, options, id_
    token, issuer, _ = main(SecurityToken, (1,), (1,))
    options = a[0].deploy(VestedOptions, token, issuer, 1, 120, 6, a[0])
    issuer.attachModule(token, options, {'from': a[0]})
    id_ = issuer.getID(a[1])


def exercise_price_zero():
    '''exercise price cannot be zero'''
    check.reverts(
        options.issueOptions,
        (id_, 0, False, [1, 2], [1, 2], {'from': a[0]}),
        "dev: exercise price == 0"
    )


def mismatch():
    '''arrays must be of same length'''
    check.reverts(
        options.issueOptions,
        (id_, 10, False, [1, 2], [1, 2, 3], {'from': a[0]}),
        "dev: length mismatch"
    )


def vest_exceeds_expiration():
    '''vesting months cannot exceed expiration'''
    check.reverts(
        options.issueOptions,
        (id_, 10, False, [1, 2], [1, 120], {'from': a[0]}),
        "dev: vest > expiration"
    )
    options.issueOptions(id_, 10, False, [1, 2], [1, 119], {'from': a[0]})


def exceeds_authorized_supply():
    '''options + tokens cannot exceed authorized supply'''
    options.issueOptions(id_, 10, False, [250000, 250000], [1, 2], {'from': a[0]})
    token.mint(a[1], 250000, {'from': a[0]})
    check.reverts(
        options.issueOptions,
        (id_, 20, False, [250000, 250000], [1, 2], {'from': a[0]}),
        "dev: exceeds authorized"
    )
    options.issueOptions(id_, 20, False, [250000], [4], {'from': a[0]})
    check.reverts(
        options.issueOptions,
        (id_, 10, False, [1], [4], {'from': a[0]}),
        "dev: exceeds authorized"
    )
