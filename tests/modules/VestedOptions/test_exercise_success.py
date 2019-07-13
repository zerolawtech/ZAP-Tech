#!/usr/bin/python3

from brownie import accounts


def test_all_no_unvested(token, options, id1, issueoptions, sleep):
    '''exercise all options, no unvested'''
    issueoptions(id1, 10)
    sleep(6)
    options.exerciseOptions(10, 500, {'from': accounts[1], 'amount': 5000})
    assert options.getOptions(id1) == (0, 0, [])
    assert token.balanceOf(accounts[1]) == 500


def test_all_some_unvested(token, options, id1, issueoptions, sleep):
    '''exercise all vested options, some still unvested'''
    issueoptions(id1, 10)
    sleep(4)
    options.exerciseOptions(10, 300, {'from': accounts[1], 'amount': 3000})
    assert options.getOptions(id1) == (0, 200, [(10, 1)])
    assert token.balanceOf(accounts[1]) == 300


def test_partial_no_unvested(token, options, id1, issueoptions, sleep):
    '''exercise some options, no unvested'''
    issueoptions(id1, 10)
    sleep(6)
    options.exerciseOptions(10, 350, {'from': accounts[1], 'amount': 3500})
    assert options.getOptions(id1) == (150, 0, [(10, 1)])
    assert token.balanceOf(accounts[1]) == 350


def test_partial_some_unvested(token, options, id1, issueoptions, sleep):
    '''exercise some options, some still unvested'''
    issueoptions(id1, 10)
    sleep(5)
    options.exerciseOptions(10, 350, {'from': accounts[1], 'amount': 3500})
    assert options.getOptions(id1) == (50, 100, [(10, 1)])
    assert token.balanceOf(accounts[1]) == 350


def test_all_multiple(token, options, id1, issueoptions, sleep):
    '''exercise all across multiple Options'''
    issueoptions(id1, 10)
    sleep(1)
    issueoptions(id1, 10)
    sleep(7)
    options.exerciseOptions(10, 1000, {'from': accounts[1], 'amount': 10000})
    assert options.getOptions(id1) == (0, 0, [])
    assert token.balanceOf(accounts[1]) == 1000


def test_all_multiple_some_unvested(token, options, id1, issueoptions, sleep):
    '''exercise all across multiple Options, some still vested'''
    issueoptions(id1, 10)
    sleep(1)
    issueoptions(id1, 10)
    sleep(3)
    options.exerciseOptions(10, 500, {'from': accounts[1], 'amount': 5000})
    assert options.getOptions(id1) == (0, 500, [(10, 2)])
    assert token.balanceOf(accounts[1]) == 500


def test_one_multiple(token, options, id1, issueoptions, sleep):
    '''exercise one full Option across multiple Options'''
    issueoptions(id1, 10)
    sleep(1)
    issueoptions(id1, 10)
    sleep(7)
    options.exerciseOptions(10, 500, {'from': accounts[1], 'amount': 5000})
    assert options.getOptions(id1) == (500, 0, [(10, 1)])
    assert token.balanceOf(accounts[1]) == 500
    options.exerciseOptions(10, 500, {'from': accounts[1], 'amount': 5000})
    assert options.getOptions(id1) == (0, 0, [])
    assert token.balanceOf(accounts[1]) == 1000


def test_partial_multiple(token, options, id1, issueoptions, sleep):
    '''exercise all across multiple Options'''
    issueoptions(id1, 10)
    sleep(1)
    issueoptions(id1, 10)
    sleep(7)
    options.exerciseOptions(10, 400, {'from': accounts[1], 'amount': 4000})
    assert options.getOptions(id1) == (600, 0, [(10, 2)])
    assert token.balanceOf(accounts[1]) == 400
    options.exerciseOptions(10, 400, {'from': accounts[1], 'amount': 4000})
    assert options.getOptions(id1) == (200, 0, [(10, 1)])
    assert token.balanceOf(accounts[1]) == 800


def test_partial_multiple_some_unvested(token, options, id1, issueoptions, sleep):
    '''exercise partially across multiple Options, some still unvested'''
    issueoptions(id1, 10)
    sleep(1)
    issueoptions(id1, 10)
    sleep(4)
    options.exerciseOptions(10, 300, {'from': accounts[1], 'amount': 3000})
    assert options.getOptions(id1) == (400, 300, [(10, 2)])
    assert token.balanceOf(accounts[1]) == 300
    options.exerciseOptions(10, 200, {'from': accounts[1], 'amount': 2000})
    assert options.getOptions(id1) == (200, 300, [(10, 2)])
    assert token.balanceOf(accounts[1]) == 500
    options.exerciseOptions(10, 200, {'from': accounts[1], 'amount': 2000})
    assert options.getOptions(id1) == (0, 300, [(10, 2)])


def test_max_auth(options, id1, sleep):
    '''vested options == max authorized supply'''
    options.issueOptions(id1, 1, False, [1000000], [0], {'from': accounts[0]})
    sleep(1)
    options.exerciseOptions(1, 1000000, {'from': accounts[1], 'amount': 1000000})
