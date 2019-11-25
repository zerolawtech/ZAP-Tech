#!/usr/bin/python3

import pytest

from brownie import accounts


# def test_setup():
#     global org, share, options, id1
#     share, org, _ = main(BookShare, (1,), (1,))
#     options = accounts[0].deploy(VestedOptions, share, org, 1, 10, 6, accounts[0])
#     org.attachModule(share, options, {'from': accounts[0]})
#     id1 = org.getID(accounts[1])


def test_wrong_price(options, id1, issueoptions, sleep):
    '''incorrect payment amount'''
    issueoptions(id1, 10)
    sleep(7)
    options.exerciseOptions(10, 100, {'from': accounts[1], 'amount': 1000})
    with pytest.reverts("Incorrect payment"):
        options.exerciseOptions(10, 100, {'from': accounts[1], 'amount': 100})
    with pytest.reverts("Incorrect payment"):
        options.exerciseOptions(10, 100, {'from': accounts[1]})
    with pytest.reverts("Incorrect payment"):
        options.exerciseOptions(10, 100, {'from': accounts[1], 'amount': 100000})


def test_unknown_id(options):
    '''unknown investor ID'''
    with pytest.reverts("Address not registered"):
        options.exerciseOptions(10, 100, {'from': accounts[9], 'amount': 1000})


def test_no_options_at_price(options, id1, issueoptions, sleep):
    '''no options at this price'''
    issueoptions(id1, 10)
    sleep(7)
    with pytest.reverts("No options at this price"):
        options.exerciseOptions(20, 500, {'from': accounts[1], 'amount': 10000})
    options.exerciseOptions(10, 500, {'from': accounts[1], 'amount': 5000})
    with pytest.reverts("No options at this price"):
        options.exerciseOptions(10, 500, {'from': accounts[1], 'amount': 5000})


def test_not_enough_options(options, id1, issueoptions, sleep):
    '''insufficient vested options'''
    issueoptions(id1, 10)
    sleep(3)
    with pytest.reverts("Insufficient vested options"):
        options.exerciseOptions(10, 400, {'from': accounts[1], 'amount': 4000})
    options.exerciseOptions(10, 200, {'from': accounts[1], 'amount': 2000})
    with pytest.reverts("Insufficient vested options"):
        options.exerciseOptions(10, 100, {'from': accounts[1], 'amount': 1000})


def test_zero_options(options, id1, issueoptions, sleep):
    '''cannot exercise zero options'''
    issueoptions(id1, 10)
    sleep(3)
    with pytest.reverts("dev: mint 0"):
        options.exerciseOptions(10, 0, {'from': accounts[1], 'amount': 0})
