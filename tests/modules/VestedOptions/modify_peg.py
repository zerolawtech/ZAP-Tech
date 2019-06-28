#!/usr/bin/python3

from brownie import *
from scripts.deployment import main


def setup(always_transact=False):
    global issuer, token, options, id1, id2, id3
    token, issuer, _ = main(SecurityToken, (1, 2, 3), (1,))
    options = a[0].deploy(VestedOptions, token, issuer, 1, 10, 6, a[8])
    issuer.attachModule(token, options, {'from': a[0]})
    id1 = issuer.getID(a[1])


def modify_peg():
    balance = a[8].balance()
    _issue(id1, 10)
    _sleep(7)
    options.modifyPeg(2, {'from': a[0]})
    options.exerciseOptions(10, 200, {'from': accounts[1], 'amount': 4000})
    options.modifyPeg(5, {'from': a[0]})
    options.exerciseOptions(10, 100, {'from': accounts[1], 'amount': 5000})
    options.modifyPeg(1, {'from': a[0]})
    options.exerciseOptions(10, 200, {'from': accounts[1], 'amount': 2000})
    check.equal(balance + 11000, a[8].balance())


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
