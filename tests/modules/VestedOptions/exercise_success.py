#!/usr/bin/python3

from brownie import *
from scripts.deployment import main


def setup():
    global issuer, token, options, id1
    token, issuer, _ = main(SecurityToken, (1,), (1,))
    options = a[0].deploy(VestedOptions, token, issuer, 1, 10, 6, a[0])
    issuer.attachModule(token, options, {'from': a[0]})
    id1 = issuer.getID(a[1])


def all_no_unvested():
    '''exercise all options, no unvested'''
    _issue(id1, 10)
    _sleep(6)
    options.exerciseOptions(10, 500, {'from': accounts[1], 'amount': 5000})
    check.equal(options.getOptions(id1), (0, 0, []))
    check.equal(token.balanceOf(accounts[1]), 500)


def all_some_unvested():
    '''exercise all vested options, some still unvested'''
    _issue(id1, 10)
    _sleep(4)
    options.exerciseOptions(10, 300, {'from': accounts[1], 'amount': 3000})
    check.equal(options.getOptions(id1), (0, 200, [(10, 1)]))
    check.equal(token.balanceOf(accounts[1]), 300)


def partial_no_unvested():
    '''exercise some options, no unvested'''
    _issue(id1, 10)
    _sleep(6)
    options.exerciseOptions(10, 350, {'from': accounts[1], 'amount': 3500})
    check.equal(options.getOptions(id1), (150, 0, [(10, 1)]))
    check.equal(token.balanceOf(accounts[1]), 350)


def partial_some_unvested():
    '''exercise some options, some still unvested'''
    _issue(id1, 10)
    _sleep(5)
    options.exerciseOptions(10, 350, {'from': accounts[1], 'amount': 3500})
    check.equal(options.getOptions(id1), (50, 100, [(10, 1)]))
    check.equal(token.balanceOf(accounts[1]), 350)


def all_multiple():
    '''exercise all across multiple Options'''
    _issue(id1, 10)
    _sleep(1)
    _issue(id1, 10)
    _sleep(7)
    options.exerciseOptions(10, 1000, {'from': accounts[1], 'amount': 10000})
    check.equal(options.getOptions(id1), (0, 0, []))
    check.equal(token.balanceOf(accounts[1]), 1000)


def all_multiple_some_unvested():
    '''exercise all across multiple Options, some still vested'''
    _issue(id1, 10)
    _sleep(1)
    _issue(id1, 10)
    _sleep(3)
    options.exerciseOptions(10, 500, {'from': accounts[1], 'amount': 5000})
    check.equal(options.getOptions(id1), (0, 500, [(10, 2)]))
    check.equal(token.balanceOf(accounts[1]), 500)


def one_multiple():
    '''exercise one full Option across multiple Options'''
    _issue(id1, 10)
    _sleep(1)
    _issue(id1, 10)
    _sleep(7)
    options.exerciseOptions(10, 500, {'from': accounts[1], 'amount': 5000})
    check.equal(options.getOptions(id1), (500, 0, [(10, 1)]))
    check.equal(token.balanceOf(accounts[1]), 500)
    options.exerciseOptions(10, 500, {'from': accounts[1], 'amount': 5000})
    check.equal(options.getOptions(id1), (0, 0, []))
    check.equal(token.balanceOf(accounts[1]), 1000)


def partial_multiple():
    '''exercise all across multiple Options'''
    _issue(id1, 10)
    _sleep(1)
    _issue(id1, 10)
    _sleep(7)
    options.exerciseOptions(10, 400, {'from': accounts[1], 'amount': 4000})
    check.equal(options.getOptions(id1), (600, 0, [(10, 2)]))
    check.equal(token.balanceOf(accounts[1]), 400)
    options.exerciseOptions(10, 400, {'from': accounts[1], 'amount': 4000})
    check.equal(options.getOptions(id1), (200, 0, [(10, 1)]))
    check.equal(token.balanceOf(accounts[1]), 800)


def partial_multiple_some_unvested():
    '''exercise partially across multiple Options, some still unvested'''
    _issue(id1, 10)
    _sleep(1)
    _issue(id1, 10)
    _sleep(4)
    options.exerciseOptions(10, 300, {'from': accounts[1], 'amount': 3000})
    check.equal(options.getOptions(id1), (400, 300, [(10, 2)]))
    check.equal(token.balanceOf(accounts[1]), 300)
    options.exerciseOptions(10, 200, {'from': accounts[1], 'amount': 2000})
    check.equal(options.getOptions(id1), (200, 300, [(10, 2)]))
    check.equal(token.balanceOf(accounts[1]), 500)
    options.exerciseOptions(10, 200, {'from': accounts[1], 'amount': 2000})
    check.equal(options.getOptions(id1), (0, 300, [(10, 2)]))


def max_auth():
    '''vested options == max authorized supply'''
    options.issueOptions(id1, 1, False, [1000000], [0], {'from': a[0]})
    _sleep(1)
    options.exerciseOptions(1, 1000000, {'from': accounts[1], 'amount': 1000000})


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
