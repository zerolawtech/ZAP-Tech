#!/usr/bin/python3

from brownie import *
from scripts.deployment import main


def setup():
    global issuer, token, options, id1, id2, id3
    token, issuer, _ = main(SecurityToken, (1, 2, 3), (1,))
    options = a[0].deploy(VestedOptions, token, issuer, 1, 10, 6, a[8])
    issuer.attachModule(token, options, {'from': a[0]})
    id1 = issuer.getID(a[1])
    id2 = issuer.getID(a[2])


def accellerate_fully_unvested():
    '''fully unvested'''
    _issue(id1, 10)
    _issue(id1, 20)
    options.accellerateVesting(id1, {'from': a[0]})
    check.equal(options.getOptions(id1), (1000, 0, [(10, 1), (20, 1)]))
    _sleep(10)
    check.equal(options.getOptions(id1), (1000, 0, [(10, 1), (20, 1)]))
    _sleep(1)
    check.equal(options.getOptions(id1), (0, 0, []))


def accellerate_partially_unvested():
    '''partially vested'''
    _issue(id1, 10)
    _issue(id1, 20)
    _sleep(2)
    options.accellerateVesting(id1, {'from': a[0]})
    check.equal(options.getOptions(id1), (1000, 0, [(10, 1), (20, 1)]))
    check.equal(options.getTotalOptionsAtPrice(10), (500, 0))
    check.equal(options.getTotalOptionsAtPrice(20), (500, 0))
    check.equal(options.totalOptions(), 1000)
    _sleep(8)
    check.equal(options.getOptions(id1), (1000, 0, [(10, 1), (20, 1)]))
    _sleep(1)
    check.equal(options.getOptions(id1), (0, 0, []))


def accellerate_already_vested():
    '''already vested'''
    _issue(id1, 10)
    _issue(id1, 20)
    _sleep(7)
    options.accellerateVesting(id1, {'from': a[0]})
    check.equal(options.getOptions(id1), (1000, 0, [(10, 1), (20, 1)]))
    check.equal(options.getTotalOptionsAtPrice(10), (500, 0))
    check.equal(options.getTotalOptionsAtPrice(20), (500, 0))
    check.equal(options.totalOptions(), 1000)
    _sleep(3)
    check.equal(options.getOptions(id1), (1000, 0, [(10, 1), (20, 1)]))
    _sleep(1)
    check.equal(options.getOptions(id1), (0, 0, []))


def accellerate_multiple_expirations():
    '''accellerate multiple, different expirations'''
    _issue(id1, 10)
    _sleep(2)
    _issue(id1, 10)
    _sleep(2)
    _issue(id1, 10)
    _sleep(1)
    options.accellerateVesting(id1, {'from': a[0]})
    check.equal(options.getOptions(id1), (1500, 0, [(10, 3)]))
    check.equal(options.getTotalOptionsAtPrice(10), (1500, 0))
    check.equal(options.totalOptions(), 1500)


def accellerate_multiple_prices():
    '''accellerate multiple, different prices and expirations'''
    _issue(id1, 10)
    _sleep(2)
    _issue(id1, 20)
    _sleep(2)
    _issue(id1, 10)
    _issue(id1, 20)
    _sleep(1)
    options.accellerateVesting(id1, {'from': a[0]})
    check.equal(options.getOptions(id1), (2000, 0, [(10, 2), (20, 2)]))
    check.equal(options.getTotalOptionsAtPrice(10), (1000, 0))
    check.equal(options.getTotalOptionsAtPrice(20), (1000, 0))
    check.equal(options.totalOptions(), 2000)


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
