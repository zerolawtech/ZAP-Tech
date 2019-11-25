#!/usr/bin/python3

import pytest

from brownie import accounts


def test_add_authority(org):
    '''add an authority'''
    org.addAuthority([accounts[-1]], [], 2000000000, 1, {'from': accounts[0]})
    assert org.getAuthority(org.getID(accounts[-1])) == (1, 1, 2000000000)


def test_zero_threshold(org):
    '''threshold zero'''
    with pytest.reverts("dev: threshold zero"):
        org.addAuthority([accounts[-1]], [], 2000000000, 0, {'from': accounts[0]})


def test_high_threshold(org):
    '''threshold too low'''
    with pytest.reverts("dev: treshold > count"):
        org.addAuthority([accounts[-1], accounts[-2]], [], 2000000000, 3, {'from': accounts[0]})
    with pytest.reverts("dev: treshold > count"):
        org.addAuthority([], [], 2000000000, 1, {'from': accounts[0]})


def test_repeat_addr(org):
    '''repeat address in addAuthority array'''
    with pytest.reverts("dev: known address"):
        org.addAuthority([accounts[-1], accounts[-1]], [], 2000000000, 1, {'from': accounts[0]})


def test_known_address(org, token, id1):
    '''known address'''
    with pytest.reverts("dev: known address"):
        org.addAuthority([accounts[0]], [], 2000000000, 1, {'from': accounts[0]})
    token.mint(accounts[1], 100, {'from': accounts[0]})
    with pytest.reverts("dev: known address"):
        org.addAuthority([accounts[1]], [], 2000000000, 1, {'from': accounts[0]})


def test_known_auth(org):
    '''known authority'''
    org.addAuthority([accounts[-1]], [], 2000000000, 1, {'from': accounts[0]})
    with pytest.reverts("dev: known authority"):
        org.addAuthority([accounts[-1]], [], 2000000000, 1, {'from': accounts[0]})
