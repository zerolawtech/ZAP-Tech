#!/usr/bin/python3

from brownie import accounts


def test_vest_expire(options, id1, id2, issueoptions, sleep):
    '''total options - vesting and expiring'''
    issueoptions(id1, 10)
    assert options.totalOptions() == 500
    issueoptions(id1, 20)
    assert options.totalOptions() == 1000
    sleep(10)
    assert options.totalOptions() == 1000
    issueoptions(id2, 10)
    assert options.totalOptions() == 1500
    sleep(95)
    assert options.totalOptions() == 500
    sleep(10)
    assert options.totalOptions() == 0


def test_issue_exercise(options, id1, issueoptions, sleep):
    '''total options - issuing and exercising'''
    issueoptions(id1, 10)
    assert options.totalOptions() == 500
    sleep(7)
    assert options.totalOptions() == 500
    options.exerciseOptions(10, 400, {'from': accounts[1], 'amount': 4000})
    assert options.totalOptions() == 100
    options.exerciseOptions(10, 100, {'from': accounts[1], 'amount': 1000})
    assert options.totalOptions() == 0
