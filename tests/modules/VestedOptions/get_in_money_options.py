#!/usr/bin/python3

from brownie import *
from scripts.deployment import main


def setup():
    global issuer, token, options, id1
    token, issuer, _ = main(SecurityToken, (1,), (1,))
    options = a[0].deploy(VestedOptions, token, issuer, 1, 10, 6, a[0])
    issuer.attachModule(token, options, {'from': a[0]})
    id1 = issuer.getID(a[1])


def in_money():
    '''get in money options'''
    _issue(id1, 10)
    _issue(id1, 20)
    _issue(id1, 30)
    check.equal(options.getInMoneyOptions(id1, 40), (0, 0))
    _sleep(2)
    check.equal(options.getInMoneyOptions(id1, 5), (0, 0))
    check.equal(options.getInMoneyOptions(id1, 10), (0, 0))
    check.equal(options.getInMoneyOptions(id1, 11), (100, 1000))
    check.equal(options.getInMoneyOptions(id1, 20), (100, 1000))
    check.equal(options.getInMoneyOptions(id1, 21), (200, 3000))
    check.equal(options.getInMoneyOptions(id1, 30), (200, 3000))
    check.equal(options.getInMoneyOptions(id1, 31), (300, 6000))
    _sleep(1)
    check.equal(options.getInMoneyOptions(id1, 31), (600, 12000))


def reverts():
    '''no options, expired options'''
    check.equal(options.getInMoneyOptions(id1, 11), (0, 0))
    _issue(id1, 10)
    check.equal(options.getInMoneyOptions(id1, 11), (0, 0))
    _sleep(2)
    check.equal(options.getInMoneyOptions(id1, 11), (100, 1000))
    _sleep(10)
    check.equal(options.getInMoneyOptions(id1, 11), (0, 0))


def multiple_expirations():
    '''multiple expiration dates'''
    _issue(id1, 10)
    _sleep(3)
    _issue(id1, 10)
    check.equal(options.getInMoneyOptions(id1, 11), (200, 2000))
    _sleep(3)
    check.equal(options.getInMoneyOptions(id1, 11), (700, 7000))
    _sleep(7)
    check.equal(options.getInMoneyOptions(id1, 11), (500, 5000))


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
