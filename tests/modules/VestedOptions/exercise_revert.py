#!/usr/bin/python3

from brownie import *
from scripts.deployment import main


def setup():
    global issuer, token, options, id1
    token, issuer, _ = main(SecurityToken, (1,), (1,))
    options = a[0].deploy(VestedOptions, token, issuer, 1, 10, 6, a[0])
    issuer.attachModule(token, options, {'from': a[0]})
    id1 = issuer.getID(a[1])


def wrong_price():
    '''incorrect payment amount'''
    _issue(id1, 10)
    _sleep(7)
    options.exerciseOptions(10, 100, {'from': accounts[1], 'amount': 1000})
    check.reverts(
        options.exerciseOptions,
        (10, 100, {'from': accounts[1], 'amount': 100}),
        "Incorrect payment"
    )
    check.reverts(
        options.exerciseOptions,
        (10, 100, {'from': accounts[1]}),
        "Incorrect payment"
    )
    check.reverts(
        options.exerciseOptions,
        (10, 100, {'from': accounts[1], 'amount': 100000}),
        "Incorrect payment"
    )


def unknown_id():
    '''unknown investor ID'''
    check.reverts(
        options.exerciseOptions,
        (10, 100, {'from': accounts[9], 'amount': 1000}),
        "Address not registered"
    )


def no_options_at_price():
    '''no options at this price'''
    _issue(id1, 10)
    _sleep(7)
    check.reverts(
        options.exerciseOptions,
        (20, 500, {'from': accounts[1], 'amount': 10000}),
        "No options at this price"
    )
    options.exerciseOptions(10, 500, {'from': accounts[1], 'amount': 5000})
    check.reverts(
        options.exerciseOptions,
        (10, 500, {'from': accounts[1], 'amount': 5000}),
        "No options at this price"
    )


def not_enough_options():
    '''insufficient vested options'''
    _issue(id1, 10)
    _sleep(3)
    check.reverts(
        options.exerciseOptions,
        (10, 400, {'from': accounts[1], 'amount': 4000}),
        "Insufficient vested options"
    )
    options.exerciseOptions(10, 200, {'from': accounts[1], 'amount': 2000})
    check.reverts(
        options.exerciseOptions,
        (10, 100, {'from': accounts[1], 'amount': 1000}),
        "Insufficient vested options"
    )


def zero_options():
    '''cannot exercise zero options'''
    _issue(id1, 10)
    _sleep(3)
    check.reverts(
        options.exerciseOptions,
        (10, 0, {'from': accounts[1], 'amount': 0}),
        "dev: mint 0"
    )


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
