#!/usr/bin/python3

from brownie import *
from scripts.deployment import main


def setup():
    global issuer, token, options, id1
    token, issuer, _ = main(SecurityToken, (1,), (1,))
    options = a[0].deploy(VestedOptions, token, issuer, 1, 10, 6, a[0])
    issuer.attachModule(token, options, {'from': a[0]})
    id1 = issuer.getID(a[1])


def get_options_at():
    _issue(id1, 10)
    check.equal(
        options.getOptionsAt(id1, 10, 0),
        [0, 500, False, _months(11), [0, 100, 100, 100, 100, 100, 0, 0, 0, 0, 0]]
    )
    _sleep(2)
    check.equal(
        options.getOptionsAt(id1, 10, 0),
        [100, 400, False, _months(9), [100, 100, 100, 100, 0, 0, 0, 0, 0]]
    )
    _sleep(8)
    check.equal(
        options.getOptionsAt(id1, 10, 0),
        [500, 0, False, _months(1), [0]]
    )
    _sleep(1)
    check.reverts(options.getOptionsAt, (id1, 10, 0))


def expire_and_recreate():
    _issue(id1, 10)
    _sleep(12)
    check.reverts(options.getOptionsAt, (id1, 10, 0))
    _issue(id1, 10)
    options.getOptionsAt(id1, 10, 0)
    check.reverts(options.getOptionsAt, (id1, 10, 1))
    _issue(id1, 10)
    options.getOptionsAt(id1, 10, 0)
    check.reverts(options.getOptionsAt, (id1, 10, 1))
    _sleep(12)
    check.reverts(options.getOptionsAt, (id1, 10, 0))


def multiple():
    _issue(id1, 10)
    _sleep(6)
    _issue(id1, 10)
    check.equal(
        options.getOptionsAt(id1, 10, 0),
        [500, 0, False, _months(5), [0, 0, 0, 0, 0]]
    )
    check.equal(
        options.getOptionsAt(id1, 10, 1),
        [0, 500, False, _months(11), [0, 100, 100, 100, 100, 100, 0, 0, 0, 0, 0]]
    )
    _sleep(5)
    check.equal(
        options.getOptionsAt(id1, 10, 0),
        [400, 100, False, _months(6), [100, 0, 0, 0, 0, 0]]
    )
    check.reverts(options.getOptionsAt, (id1, 10, 1))


def _issue(id_, price):
    options.issueOptions(
        id_,
        price,
        False,
        [100, 100, 100, 100, 100],
        [1, 2, 3, 4, 5],
        {'from': a[0]}
    )


def _sleep(months):
    now = int(rpc.time() // 2592000 + 1) * 2592000
    rpc.sleep(now - rpc.time() + 1 + 2592000 * (months - 1))


def _months(months):
    return int(rpc.time() // 2592000 + 1) * 2592000 + months * 2592000
