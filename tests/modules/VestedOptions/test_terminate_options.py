#!/usr/bin/python3

from brownie import accounts


def test_terminate_unvested(options, id1, issueoptions):
    """unvested"""
    issueoptions(id1, 10)
    issueoptions(id1, 20)
    options.terminateOptions(id1, {"from": accounts[0]})
    assert options.getOptions(id1) == (0, 0, [])
    assert options.getTotalOptionsAtPrice(10) == (0, 0)
    assert options.totalOptions() == 0


def test_terminate_partial(options, id1, issueoptions, sleep):
    """partially vested"""
    issueoptions(id1, 10)
    issueoptions(id1, 20)
    sleep(3)
    options.terminateOptions(id1, {"from": accounts[0]})
    assert options.getOptions(id1), (400, 0, [(10, 1) == (20, 1)])
    assert options.getTotalOptionsAtPrice(10) == (200, 0)
    assert options.totalOptions() == 400
    sleep(5)
    assert options.getOptions(id1), (400, 0, [(10, 1) == (20, 1)])
    assert options.getTotalOptionsAtPrice(10) == (200, 0)
    assert options.totalOptions() == 400
    sleep(2)
    assert options.getOptions(id1) == (0, 0, [])
    assert options.getTotalOptionsAtPrice(10) == (0, 0)
    assert options.totalOptions() == 0


def test_terminate_vested(options, id1, issueoptions, sleep):
    """already vested"""
    issueoptions(id1, 10)
    issueoptions(id1, 20)
    sleep(10)
    options.terminateOptions(id1, {"from": accounts[0]})
    assert options.getOptions(id1) == (1000, 0, [(10, 1), (20, 1)])
    assert options.getTotalOptionsAtPrice(10) == (500, 0)
    assert options.totalOptions() == 1000
    sleep(5)
    assert options.getOptions(id1) == (1000, 0, [(10, 1), (20, 1)])
    assert options.getTotalOptionsAtPrice(10) == (500, 0)
    assert options.totalOptions() == 1000
    sleep(1)
    assert options.getOptions(id1) == (0, 0, [])
    assert options.getTotalOptionsAtPrice(10) == (0, 0)
    assert options.totalOptions() == 0


def test_terminate_do_not_extend_grace(options, id1, issueoptions, sleep):
    """grace period > expiration date"""
    issueoptions(id1, 10)
    issueoptions(id1, 20)
    sleep(16)
    options.terminateOptions(id1, {"from": accounts[0]})
    assert options.getOptions(id1) == (1000, 0, [(10, 1), (20, 1)])
    assert options.getTotalOptionsAtPrice(10) == (500, 0)
    assert options.totalOptions() == 1000
    sleep(4)
    assert options.getOptions(id1) == (1000, 0, [(10, 1), (20, 1)])
    assert options.getTotalOptionsAtPrice(10) == (500, 0)
    assert options.totalOptions() == 1000
    sleep(80)
    assert options.getOptions(id1) == (0, 0, [])
    assert options.getTotalOptionsAtPrice(10) == (0, 0)
    assert options.totalOptions() == 0


def test_grace_equals_expiration(options, id1, issueoptions, sleep):
    """grace period == expiration date"""
    issueoptions(id1, 10)
    issueoptions(id1, 20)
    sleep(15)
    options.terminateOptions(id1, {"from": accounts[0]})
    assert options.getOptions(id1), (1000, 0, [(10, 1) == (20, 1)])
    assert options.getTotalOptionsAtPrice(10) == (500, 0)
    assert options.totalOptions() == 1000
    sleep(5)
    assert options.getOptions(id1) == (1000, 0, [(10, 1), (20, 1)])
    assert options.getTotalOptionsAtPrice(10) == (500, 0)
    assert options.totalOptions() == 1000
    sleep(1)
    assert options.getOptions(id1) == (0, 0, [])
    assert options.getTotalOptionsAtPrice(10) == (0, 0)
    assert options.totalOptions() == 0
