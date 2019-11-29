#!/usr/bin/python3

import pytest

from brownie import accounts, rpc


def test_set_checkpoint(cp, share, cptime):
    '''set a checkpoint'''
    cp.newCheckpoint(share, cptime, {'from': accounts[0]})


def test_set_checkpoint_time(cp, share):
    '''set a checkpoint - time already passed'''
    with pytest.reverts("dev: time"):
        cp.newCheckpoint(share, rpc.time() - 100, {'from': accounts[0]})
    with pytest.reverts("dev: time"):
        cp.newCheckpoint(share, rpc.time(), {'from': accounts[0]})


def test_set_checkpoint_restricted_share(cp, org, share, cptime):
    '''set a checkpoint - restricted share'''
    org.setOrgShareRestriction(share, True, {'from': accounts[0]})
    with pytest.reverts("dev: share"):
        cp.newCheckpoint(share, cptime, {'from': accounts[0]})


def test_set_checkpoint_not_share(cp, org, cptime):
    '''set a checkpoint - not a share'''
    with pytest.reverts("dev: share"):
        cp.newCheckpoint(org, cptime, {'from': accounts[0]})
    with pytest.reverts("dev: share"):
        cp.newCheckpoint(accounts[3], cptime, {'from': accounts[0]})


def test_set_checkpoint_already_set(cp, share, cptime):
    '''set a checkpoint - already exists'''
    cp.newCheckpoint(share, cptime, {'from': accounts[0]})
    with pytest.reverts("dev: already set"):
        cp.newCheckpoint(share, cptime, {'from': accounts[0]})


def test_set_checkpoint_second_share(cp, org, share, share2, cptime):
    '''set a checkpoint - second share'''
    # share2 = accounts[0].deploy(BookShare, org, "Test Share", "TST", 1000000)
    # org.addOrgShare(share2, {'from': accounts[0]})
    org.attachModule(share2, cp, {'from': accounts[0]})
    cp.newCheckpoint(share, cptime, {'from': accounts[0]})
    cp.newCheckpoint(share2, cptime, {'from': accounts[0]})
