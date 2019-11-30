#!/usr/bin/python3


def test_in_money(options, id1, issueoptions, sleep):
    """get in money options"""
    issueoptions(id1, 10)
    issueoptions(id1, 20)
    issueoptions(id1, 30)
    assert options.getInMoneyOptions(id1, 40) == (0, 0)
    sleep(2)
    assert options.getInMoneyOptions(id1, 5) == (0, 0)
    assert options.getInMoneyOptions(id1, 10) == (0, 0)
    assert options.getInMoneyOptions(id1, 11) == (100, 1000)
    assert options.getInMoneyOptions(id1, 20) == (100, 1000)
    assert options.getInMoneyOptions(id1, 21) == (200, 3000)
    assert options.getInMoneyOptions(id1, 30) == (200, 3000)
    assert options.getInMoneyOptions(id1, 31) == (300, 6000)
    sleep(1)
    assert options.getInMoneyOptions(id1, 31) == (600, 12000)


def test_reverts(options, id1, issueoptions, sleep):
    """no options, expired options"""
    assert options.getInMoneyOptions(id1, 11) == (0, 0)
    issueoptions(id1, 10)
    assert options.getInMoneyOptions(id1, 11) == (0, 0)
    sleep(2)
    assert options.getInMoneyOptions(id1, 11) == (100, 1000)
    sleep(100)
    assert options.getInMoneyOptions(id1, 11) == (0, 0)


def test_multiple_expirations(options, id1, issueoptions, sleep):
    """multiple expiration dates"""
    issueoptions(id1, 10)
    sleep(3)
    issueoptions(id1, 10)
    assert options.getInMoneyOptions(id1, 11) == (200, 2000)
    sleep(3)
    assert options.getInMoneyOptions(id1, 11) == (700, 7000)
    sleep(97)
    assert options.getInMoneyOptions(id1, 11) == (500, 5000)
