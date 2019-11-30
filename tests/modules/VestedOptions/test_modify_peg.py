#!/usr/bin/python3

from brownie import accounts


def test_modify_peg(options, id1, issueoptions, sleep):
    issueoptions(id1, 10)
    sleep(7)
    options.modifyPeg(2, {"from": accounts[0]})
    balance = accounts[0].balance()
    options.exerciseOptions(10, 200, {"from": accounts[1], "amount": 4000})
    assert accounts[0].balance() == balance + 4000
    options.modifyPeg(5, {"from": accounts[0]})
    balance = accounts[0].balance()
    options.exerciseOptions(10, 100, {"from": accounts[1], "amount": 5000})
    assert accounts[0].balance() == balance + 5000
    options.modifyPeg(1, {"from": accounts[0]})
    balance = accounts[0].balance()
    options.exerciseOptions(10, 200, {"from": accounts[1], "amount": 2000})
    assert accounts[0].balance() == balance + 2000
