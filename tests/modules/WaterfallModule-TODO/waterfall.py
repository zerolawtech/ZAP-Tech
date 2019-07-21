#!/usr/bin/python3

import string

from brownie import *
from scripts.deployment import main


def setup(always_transact=False):
    global issuer, common, merger, options, id_
    common, issuer, _ = main(SecurityToken, (1,), (1,))
    common.mint(a[1], 1000000, {'from': a[0]})
    common.modifyAuthorizedSupply(10000000, {'from': a[0]})

    options = a[0].deploy(VestedOptions, common, issuer, 1, 100, 6, a[0])
    issuer.attachModule(common, options, {'from': a[0]})

    merger = a[0].deploy(WaterfallModule, issuer, common, options)


def _options(start, stop, inc, amount):
    for i in range(start, stop, inc):
        options.issueOptions(id_, i, False, [amount], [0], {'from': a[0]})
    rpc.sleep(2592001)
    return options


def _preferred(total_supply, consideration, convertible, participating, senior):
    for i in range(len(total_supply)):
        token = accounts[0].deploy(
            SecurityToken,
            IssuingEntity[0],
            f"Preferred Series {string.ascii_uppercase[i]}",
            f"Pref{string.ascii_uppercase[i]}",
            total_supply[i]
        )
        IssuingEntity[0].addToken(token, {'from': a[0]})
        token.mint(accounts[1], total_supply[i], {'from': accounts[0]})
        merger.addToken(
            token,
            consideration[i],
            convertible[i],
            participating[i],
            senior[i],
            {'from': a[0]}
        )
    return SecurityToken[1:]


def below_total_preference():
    pref = _preferred(
        [1000000, 1000000, 1000000],
        [1000, 2000, 3000],
        [True, True, True],
        [False, False, False],
        [True, True, True]
    )
    merger.calculateConsiderations(5500000000, [0, 0, 0], {'from': a[0]})
    assert not merger.getPerShareConsideration(common)
    assert merger.getPerShareConsideration(pref[0]) == 500
    assert merger.getPerShareConsideration(pref[1]) == 2000
    assert merger.getPerShareConsideration(pref[2]) == 3000


def below_preference_pari_passu():
    pref = _preferred(
        [1000000, 1000000, 1000000],
        [1000, 2000, 3000],
        [True, True, True],
        [False, False, False],
        [True, False, False]
    )
    merger.calculateConsiderations(600000000, [0, 0, 0], {'from': a[0]})
    assert not merger.getPerShareConsideration(common)
    assert merger.getPerShareConsideration(pref[0]) == 100
    assert merger.getPerShareConsideration(pref[1]) == 200
    assert merger.getPerShareConsideration(pref[2]) == 300


def below_preference_pari_passu_multiple():
    pref = _preferred(
        [1000000, 1000000, 1000000, 1000000],
        [1000, 2000, 3000, 4000],
        [True, True, True, True],
        [False, False, False, True],
        [True, False, True, False]
    )
    merger.calculateConsiderations(8000000000, [0, 0, 0], {'from': a[0]})
    assert not merger.getPerShareConsideration(common)
    assert merger.getPerShareConsideration(pref[0]) == 333
    assert merger.getPerShareConsideration(pref[1]) == 666
    assert merger.getPerShareConsideration(pref[2]) == 3000
    assert merger.getPerShareConsideration(pref[4]) == 4000
