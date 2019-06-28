#!/usr/bin/python3

from brownie import *
from scripts.deployment import main


def setup():
    global issuer, token, options, id1, id2, id3
    token, issuer, _ = main(SecurityToken, (1, 2, 3), (1,))
    options = a[0].deploy(VestedOptions, token, issuer, 1, 20, 6, a[8])
    issuer.attachModule(token, options, {'from': a[0]})
    id1 = issuer.getID(a[1])
    id2 = issuer.getID(a[2])


def terminate_unvested():
    '''unvested'''
    _issue(id1, 10)
    _issue(id1, 20)
    options.terminateOptions(id1, {'from': a[0]})
    check.equal(options.getOptions(id1), (0, 0, []))
    check.equal(options.getTotalOptionsAtPrice(10), (0, 0))
    check.equal(options.totalOptions(), 0)


def terminate_partial():
    '''partially vested'''
    _issue(id1, 10)
    _issue(id1, 20)
    _sleep(3)
    options.terminateOptions(id1, {'from': a[0]})
    check.equal(options.getOptions(id1), (400, 0, [(10, 1), (20, 1)]))
    check.equal(options.getTotalOptionsAtPrice(10), (200, 0))
    check.equal(options.totalOptions(), 400)
    _sleep(5)
    check.equal(options.getOptions(id1), (400, 0, [(10, 1), (20, 1)]))
    check.equal(options.getTotalOptionsAtPrice(10), (200, 0))
    check.equal(options.totalOptions(), 400)
    _sleep(2)
    check.equal(options.getOptions(id1), (0, 0, []))
    check.equal(options.getTotalOptionsAtPrice(10), (0, 0))
    check.equal(options.totalOptions(), 0)


def terminate_vested():
    '''already vested'''
    _issue(id1, 10)
    _issue(id1, 20)
    _sleep(10)
    options.terminateOptions(id1, {'from': a[0]})
    check.equal(options.getOptions(id1), (1000, 0, [(10, 1), (20, 1)]))
    check.equal(options.getTotalOptionsAtPrice(10), (500, 0))
    check.equal(options.totalOptions(), 1000)
    _sleep(5)
    check.equal(options.getOptions(id1), (1000, 0, [(10, 1), (20, 1)]))
    check.equal(options.getTotalOptionsAtPrice(10), (500, 0))
    check.equal(options.totalOptions(), 1000)
    _sleep(1)
    check.equal(options.getOptions(id1), (0, 0, []))
    check.equal(options.getTotalOptionsAtPrice(10), (0, 0))
    check.equal(options.totalOptions(), 0)


def terminate_do_not_extend_grace():
    '''grace period > expiration date'''
    _issue(id1, 10)
    _issue(id1, 20)
    _sleep(16)
    options.terminateOptions(id1, {'from': a[0]})
    check.equal(options.getOptions(id1), (1000, 0, [(10, 1), (20, 1)]))
    check.equal(options.getTotalOptionsAtPrice(10), (500, 0))
    check.equal(options.totalOptions(), 1000)
    _sleep(4)
    check.equal(options.getOptions(id1), (1000, 0, [(10, 1), (20, 1)]))
    check.equal(options.getTotalOptionsAtPrice(10), (500, 0))
    check.equal(options.totalOptions(), 1000)
    _sleep(1)
    check.equal(options.getOptions(id1), (0, 0, []))
    check.equal(options.getTotalOptionsAtPrice(10), (0, 0))
    check.equal(options.totalOptions(), 0)


def grace_equals_expiration():
    '''grace period == expiration date'''
    _issue(id1, 10)
    _issue(id1, 20)
    _sleep(15)
    options.terminateOptions(id1, {'from': a[0]})
    check.equal(options.getOptions(id1), (1000, 0, [(10, 1), (20, 1)]))
    check.equal(options.getTotalOptionsAtPrice(10), (500, 0))
    check.equal(options.totalOptions(), 1000)
    _sleep(5)
    check.equal(options.getOptions(id1), (1000, 0, [(10, 1), (20, 1)]))
    check.equal(options.getTotalOptionsAtPrice(10), (500, 0))
    check.equal(options.totalOptions(), 1000)
    _sleep(1)
    check.equal(options.getOptions(id1), (0, 0, []))
    check.equal(options.getTotalOptionsAtPrice(10), (0, 0))
    check.equal(options.totalOptions(), 0)


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
