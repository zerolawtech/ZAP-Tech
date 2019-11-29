#!/usr/bin/python3

import functools
import pytest

from brownie import accounts, rpc


def test_issue_and_vest(id1, issueoptions, sleep, check):
    '''issue options, vest over time'''
    issueoptions(id1, 10)
    sleep(1)
    at_price = list(zip(range(0, 600, 100), range(500, -100, -100)))
    check(
        [[(i[0],), (i[1],)] for i in zip([10] * 6, range(0, 600, 100))],
        at_price,
        [i + ([[10, 1]],) for i in at_price]
    )
    sleep(93)
    check(
        [[(10,), (500,)], [(10,), (500,)], [tuple(), tuple()]],
        [(500, 0), (500, 0), (0, 0)],
        [(500, 0, [(10, 1)]), (500, 0, [(10, 1)]), (0, 0, [])]
    )


def test_multiple_same_expiration(id1, issueoptions, sleep, check):
    '''issue  multiple, same expiration'''
    issueoptions(id1, 10)
    issueoptions(id1, 10)
    sleep(1)
    at_price = list(zip(range(0, 1200, 200), range(1000, -200, -200)))
    check(
        [[(i[0],), (i[1],)] for i in zip([10] * 6, range(0, 1200, 200))],
        at_price,
        [i + ([[10, 1]],) for i in at_price]
    )
    sleep(94)
    check(
        [[(10,), (1000,)], [tuple(), tuple()]],
        [(1000, 0), (0, 0)],
        [(1000, 0, [(10, 1)]), (0, 0, [])]
    )


def test_multiple_different_expirations(id1, issueoptions, sleep, check):
    '''issue multiple, different expirations'''
    issueoptions(id1, 10)
    sleep(1)
    issueoptions(id1, 10)
    sleep(1)

    at_price = list(zip(range(100, 1100, 200), range(900, -100, -200)))
    check(
        [[(i[0],), (i[1],)] for i in zip([10] * 6, range(100, 1100, 200))],
        at_price,
        [i + ([[10, 2]],) for i in at_price]
    )
    sleep(94)
    check(
        [[(10,), (1000,)], [(10,), (500,)], [tuple(), tuple()]],
        [(1000, 0), (500, 0), (0, 0)],
        [(1000, 0, [(10, 2)]), (500, 0, [(10, 1)]), (0, 0, [])]
    )


def test_multiple_members(id1, id2, issueoptions, sleep, check):
    '''multiple members'''
    issueoptions(id1, 10)
    issueoptions(id2, 10)
    sleep(1)
    check(
        [[(i[0],), (i[1],)] for i in zip([10] * 6, range(0, 1200, 200))],
        list(zip(range(0, 1200, 200), range(1000, -200, -200))),
        [i + ([[10, 1]],) for i in list(zip(range(0, 600, 100), range(500, -100, -100)))]
    )
    sleep(94)
    check(
        [[(10,), (1000,)], [tuple(), tuple()]],
        [(1000, 0), (0, 0)],
        [(500, 0, [(10, 1)]), (0, 0, [])]
    )


def test_issue_multiple_prices(id1, issueoptions, sleep, check):
    '''multiple prices'''
    issueoptions(id1, 10)
    issueoptions(id1, 20)
    issueoptions(id1, 25)
    sleep(1)
    totals = [[(10, 20, 25), (i, i, i)] for i in range(0, 600, 100)]
    at_price = list(zip(range(0, 600, 100), range(500, -100, -100)))
    check(
        totals,
        at_price,
        [
            i + ([[10, 1], [20, 1], [25, 1]],) for i in
            list(zip(range(0, 1800, 300), range(1500, -100, -300)))
        ]
    )
    sleep(94)
    check(
        [[(10, 20, 25), (500, 500, 500)], [tuple(), tuple()]],
        [(500, 0), (0, 0)],
        [(1500, 0, [(10, 1), (20, 1), (25, 1)]), (0, 0, [])]
    )


def test_last_month(id1, options, sleep, check):
    '''lower and upper limits'''
    options.issueOptions(id1, 10, False, [100, 100], [0, 99], {'from': accounts[0]})
    check(
        [[(10,), (0,)], [(10,), (100,)]],
        [(0, 200), (100, 100)],
        [(0, 200, [(10, 1)]), (100, 100, [(10, 1)])]
    )
    sleep(98)
    check(
        [[(10,), (100,)], [(10,), (200,)], [tuple(), tuple()]],
        [(100, 100), (200, 0), (0, 0)],
        [(100, 100, [(10, 1)]), (200, 0, [(10, 1)]), (0, 0, [])]
    )


@pytest.fixture(scope="module")
def check(options, id1):
    yield functools.partial(_check, options, id1)


def _check(options, id1, sorted_totals, at_price, get_options):
    for i in range(len(sorted_totals) - 1):
        now = int(rpc.time() // 2592000 + 1) * 2592000
        rpc.sleep(now - rpc.time() - 5)
        rpc.mine()
        assert options.getSortedTotals() == sorted_totals[i]
        assert options.getTotalOptionsAtPrice(10) == at_price[i]
        assert options.getOptions(id1) == get_options[i]
        rpc.sleep(10)
        rpc.mine()
        assert options.getSortedTotals() == sorted_totals[i + 1]
        assert options.getTotalOptionsAtPrice(10) == at_price[i + 1]
        assert options.getOptions(id1) == get_options[i + 1]
