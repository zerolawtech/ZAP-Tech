#!/usr/bin/python3

from brownie import *
from scripts.deployment import main


def setup():
    global issuer, token, options, id_
    token, issuer, _ = main(SecurityToken, (1,), (1,))
    options = a[0].deploy(VestedOptions, token, issuer, 1, 120, 6, a[0])
    issuer.attachModule(token, options, {'from': a[0]})
    id_ = issuer.getID(a[1])
    options.issueOptions(
        id_,
        10,
        False,
        [100, 100, 100, 100, 100, 100],
        [1, 2, 3, 4, 5, 6],
        {'from': a[0]}
    )


def issue_and_vest():
    '''issue options, vest over time'''

    check.equal(options.getSortedTotals(), [[10, 0]])
    check.equal(options.getTotalOptionsAtPrice(10), [0, 600])
    check.equal(options.getOptions(id_), [0, 600, [[10, 1]]])

    rpc.sleep(2592001 * 2)
    check.equal(options.getSortedTotals(), [[10, 100]])
    check.equal(options.getTotalOptionsAtPrice(10), [100, 500])
    check.equal(options.getOptions(id_), [100, 500, [[10, 1]]])

    rpc.sleep(2592001 * 5)
    check.equal(options.getSortedTotals(), [[10, 600]])
    check.equal(options.getTotalOptionsAtPrice(10), [600, 0])
    check.equal(options.getOptions(id_), [600, 0, [[10, 1]]])


def multiple_same_expiration():
    '''issue multiple, same expiration'''
    options.issueOptions(
        id_,
        10,
        False,
        [100, 100, 100, 100, 100, 100],
        [1, 2, 3, 4, 5, 6],
        {'from': a[0]}
    )

    check.equal(options.getSortedTotals(), [[10, 0]])
    check.equal(options.getTotalOptionsAtPrice(10), [0, 1200])
    check.equal(options.getOptions(id_), [0, 1200, [[10, 1]]])

    rpc.sleep(2592001 * 2)
    check.equal(options.getSortedTotals(), [[10, 200]])
    check.equal(options.getTotalOptionsAtPrice(10), [200, 1000])
    check.equal(options.getOptions(id_), [200, 1000, [[10, 1]]])

    rpc.sleep(2592001 * 5)
    check.equal(options.getSortedTotals(), [[10, 1200]])
    check.equal(options.getTotalOptionsAtPrice(10), [1200, 0])
    check.equal(options.getOptions(id_), [1200, 0, [[10, 1]]])


def multiple_different_expirations():
    '''issue multiple, different expirations'''
    rpc.sleep(2592001 * 2)
    options.issueOptions(
        id_,
        10,
        False,
        [100, 100, 100, 100, 100, 100],
        [1, 2, 3, 4, 5, 6],
        {'from': a[0]}
    )

    check.equal(options.getSortedTotals(), [[10, 100]])
    check.equal(options.getTotalOptionsAtPrice(10), [100, 1100])
    check.equal(options.getOptions(id_), [100, 1100, [[10, 2]]])

    rpc.sleep(2592001 * 5)
    check.equal(options.getSortedTotals(), [[10, 1000]])
    check.equal(options.getTotalOptionsAtPrice(10), [1000, 200])
    check.equal(options.getOptions(id_), [1000, 200, [[10, 2]]])

    rpc.sleep(2592001 * 5)
    check.equal(options.getSortedTotals(), [[10, 1200]])
    check.equal(options.getTotalOptionsAtPrice(10), [1200, 0])
    check.equal(options.getOptions(id_), [1200, 0, [[10, 2]]])


def expire():
    '''issue options, expire'''

    rpc.sleep(2592001 * 10)
    check.equal(options.getSortedTotals(), [[10, 600]])
    check.equal(options.getTotalOptionsAtPrice(10), [600, 0])
    check.equal(options.getOptions(id_), [600, 0, [[10, 1]]])

    rpc.sleep(2592001 * 120)
    check.equal(options.getSortedTotals(), [])
    check.equal(options.getTotalOptionsAtPrice(10), [0, 0])
    check.equal(options.getOptions(id_), [0, 0, []])


# def expire_multiple_expiration_dates():

# def issue_multiple_investors():

# def issue_multiple_prices():

# def expire_multiple_prices():
