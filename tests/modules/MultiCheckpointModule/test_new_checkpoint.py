#!/usr/bin/python3

import pytest

from brownie import accounts, rpc


def test_set_checkpoint(cp, token, cptime):
    '''set a checkpoint'''
    cp.newCheckpoint(token, cptime, {'from': accounts[0]})


def test_set_checkpoint_time(cp, token):
    '''set a checkpoint - time already passed'''
    with pytest.reverts("dev: time"):
        cp.newCheckpoint(token, rpc.time() - 100, {'from': accounts[0]})
    with pytest.reverts("dev: time"):
        cp.newCheckpoint(token, rpc.time(), {'from': accounts[0]})


def test_set_checkpoint_restricted_token(cp, org, token, cptime):
    '''set a checkpoint - restricted token'''
    org.setTokenRestriction(token, True, {'from': accounts[0]})
    with pytest.reverts("dev: token"):
        cp.newCheckpoint(token, cptime, {'from': accounts[0]})


def test_set_checkpoint_not_token(cp, org, cptime):
    '''set a checkpoint - not a token'''
    with pytest.reverts("dev: token"):
        cp.newCheckpoint(org, cptime, {'from': accounts[0]})
    with pytest.reverts("dev: token"):
        cp.newCheckpoint(accounts[3], cptime, {'from': accounts[0]})


def test_set_checkpoint_already_set(cp, token, cptime):
    '''set a checkpoint - already exists'''
    cp.newCheckpoint(token, cptime, {'from': accounts[0]})
    with pytest.reverts("dev: already set"):
        cp.newCheckpoint(token, cptime, {'from': accounts[0]})


def test_set_checkpoint_second_token(cp, org, token, token2, cptime):
    '''set a checkpoint - second token'''
    # token2 = accounts[0].deploy(SecurityToken, org, "Test Token", "TST", 1000000)
    # org.addToken(token2, {'from': accounts[0]})
    org.attachModule(token2, cp, {'from': accounts[0]})
    cp.newCheckpoint(token, cptime, {'from': accounts[0]})
    cp.newCheckpoint(token2, cptime, {'from': accounts[0]})
