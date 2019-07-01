#!/usr/bin/python3

from operator import itemgetter

from brownie import *
from scripts.deployment import main


def setup(always_transact=False):
    global issuer, token, options, id1, id2, id3
    token, issuer, _ = main(SecurityToken, (1, 2, 3), (1,))
    options = a[0].deploy(VestedOptions, token, issuer, 1, 100, 6, a[0])
    issuer.attachModule(token, options, {'from': a[0]})
    id1 = issuer.getID(a[1])
    id2 = issuer.getID(a[2])


def issue_and_vest():
    '''issue options, vest over time'''
    _issue(id1, 10)
    _sleep(1)
    at_price = list(zip(range(0, 700, 100), range(600, -100, -100)))
    _check(
        [[(i[0],), (i[1],)] for i in zip([10] * 7, range(0, 700, 100))],
        at_price,
        [i + ([[10, 1]],) for i in at_price]
    )
    _sleep(92)
    _check(
        [[(10,), (600,)], [(10,), (600,)], [tuple(), tuple()]],
        [(600, 0), (600, 0), (0, 0)],
        [(600, 0, [(10, 1)]), (600, 0, [(10, 1)]), (0, 0, [])]
    )


def multiple_same_expiration():
    '''issue multiple, same expiration'''
    _issue(id1, 10)
    _issue(id1, 10)
    _sleep(1)
    at_price = list(zip(range(0, 1400, 200), range(1200, -200, -200)))
    _check(
        [[(i[0],), (i[1],)] for i in zip([10] * 7, range(0, 1400, 200))],
        at_price,
        [i + ([[10, 1]],) for i in at_price]
    )
    _sleep(93)
    _check(
        [[(10,), (1200,)], [tuple(), tuple()]],
        [(1200, 0), (0, 0)],
        [(1200, 0, [(10, 1)]), (0, 0, [])]
    )


def multiple_different_expirations():
    '''issue multiple, different expirations'''
    _issue(id1, 10)
    _sleep(1)
    _issue(id1, 10)
    _sleep(1)

    at_price = list(zip(range(100, 1300, 200), range(1100, -100, -200)))
    _check(
        [[(i[0],), (i[1],)] for i in zip([10] * 7, range(100, 1300, 200))],
        at_price,
        [i + ([[10, 2]],) for i in at_price]
    )
    _sleep(93)
    _check(
        [[(10,), (1200,)], [(10,), (600,)], [tuple(), tuple()]],
        [(1200, 0), (600, 0), (0, 0)],
        [(1200, 0, [(10, 2)]), (600, 0, [(10, 1)]), (0, 0, [])]
    )


def multiple_investors():
    '''multiple investors'''
    _issue(id1, 10)
    _issue(id2, 10)
    _sleep(1)
    _check(
        [[(i[0],), (i[1],)] for i in zip([10] * 7, range(0, 1400, 200))],
        list(zip(range(0, 1400, 200), range(1200, -200, -200))),
        [i + ([[10, 1]],) for i in list(zip(range(0, 700, 100), range(600, -100, -100)))]
    )
    _sleep(93)
    _check(
        [[(10,), (1200,)], [tuple(), tuple()]],
        [(1200, 0), (0, 0)],
        [(600, 0, [(10, 1)]), (0, 0, [])]
    )


def issue_multiple_prices():
    '''multiple prices'''
    _issue(id1, 10)
    _issue(id1, 20)
    _issue(id1, 25)
    _sleep(1)
    totals = [[(10, 20, 25), (i, i, i)] for i in range(0, 700, 100)]
    at_price = list(zip(range(0, 700, 100), range(600, -100, -100)))

    _check(
        totals,
        at_price,
        [
            i + ([[10, 1], [20, 1], [25, 1]],) for i in
            list(zip(range(0, 2100, 300), range(1800, -100, -300)))
        ]
    )
    _sleep(93)
    _check(
        [[(10, 20, 25), (600, 600, 600)], [tuple(), tuple()]],
        [(600, 0), (0, 0)],
        [(1800, 0, [(10, 1), (20, 1), (25, 1)]), (0, 0, [])]
    )


def last_month():
    '''lower and upper limits'''
    options.issueOptions(id1, 10, False, [100, 100], [0, 99], {'from': a[0]})
    _check(
        [[(10,), (0,)], [(10,), (100,)]],
        [(0, 200), (100, 100)],
        [(0, 200, [(10, 1)]), (100, 100, [(10, 1)])]
    )
    _sleep(98)
    _check(
        [[(10,), (100,)], [(10,), (200,)], [tuple(), tuple()]],
        [(100, 100), (200, 0), (0, 0)],
        [(100, 100, [(10, 1)]), (200, 0, [(10, 1)]), (0, 0, [])]
    )


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


def _check(sorted_totals, at_price, get_options):
    for i in range(len(sorted_totals) - 1):
        now = int(rpc.time() // 2592000 + 1) * 2592000
        rpc.sleep(now - rpc.time() - 5)
        check.equal(options.getSortedTotals(), sorted_totals[i])
        check.equal(options.getTotalOptionsAtPrice(10), at_price[i])
        check.equal(options.getOptions(id1), get_options[i])
        rpc.sleep(10)
        check.equal(options.getSortedTotals(), sorted_totals[i + 1])
        check.equal(options.getTotalOptionsAtPrice(10), at_price[i + 1])
        check.equal(options.getOptions(id1), get_options[i + 1])
