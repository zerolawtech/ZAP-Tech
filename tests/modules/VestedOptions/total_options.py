#!/usr/bin/python3

from brownie import *
from scripts.deployment import main


def setup(always_transact=False):
    global issuer, token, options, id1, id2, id3
    token, issuer, _ = main(SecurityToken, (1, 2, 3), (1,))
    options = a[0].deploy(VestedOptions, token, issuer, 1, 100, 6, a[0])
    issuer.attachModule(token, options, {'from': a[0]})
    id1 = issuer.getID(a[1])
    id2 = issuer.getID(a[2])


def vest_expire():
    '''total options - vesting and expiring'''
    _issue(id1, 10)
    check.equal(options.totalOptions(), 600)
    _issue(id1, 20)
    check.equal(options.totalOptions(), 1200)
    _sleep(10)
    check.equal(options.totalOptions(), 1200)
    _issue(id2, 10)
    check.equal(options.totalOptions(), 1800)
    _sleep(95)
    check.equal(options.totalOptions(), 600)
    _sleep(10)
    check.equal(options.totalOptions(), 0)


def issue_exercise():
    '''total options - issuing and exercising'''
    _issue(id1, 10)
    check.equal(options.totalOptions(), 600)
    _sleep(7)
    check.equal(options.totalOptions(), 600)
    options.exerciseOptions(10, 400, {'from': accounts[1], 'amount': 4000})
    check.equal(options.totalOptions(), 200)
    options.exerciseOptions(10, 200, {'from': accounts[1], 'amount': 2000})
    check.equal(options.totalOptions(), 0)


def _issue(id_, price):
    options.issueOptions(
        id_,
        price,
        False,
        [100, 100, 100, 100, 100, 100],
        [1, 2, 3, 4, 5, 6],
        {'from': a[0]}
    )


def _sleep(months):
    now = int(rpc.time() // 2592000 + 1) * 2592000
    rpc.sleep(now - rpc.time() + 1 + 2592000 * (months - 1))
