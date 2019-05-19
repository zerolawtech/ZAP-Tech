#!/usr/bin/python3

import time

from brownie import *
from scripts.deployment import main


def setup():
    global token, issuer, cp
    token, issuer, _ = main(SecurityToken, (1,2,3,4,5), (1,))
    cp = a[0].deploy(MultiCheckpointModule, issuer)
    issuer.attachModule(token, cp, {'from': a[0]})

def set_checkpoint():
    '''set a checkpoint'''
    cp.newCheckpoint(token, rpc.time()+100, {'from': a[0]})

def set_checkpoint_time():
    '''set a checkpoint - time already passed'''
    check.reverts(
        cp.newCheckpoint,
        (token, rpc.time()-100, {'from': a[0]}),
        "dev: time"
    )
    check.reverts(
        cp.newCheckpoint,
        (token, rpc.time(), {'from': a[0]}),
        "dev: time"
    )

def set_checkpoint_restricted_token():
    '''set a checkpoint - restricted token'''
    issuer.setTokenRestriction(token, False, {'from': a[0]})
    check.reverts(
        cp.newCheckpoint,
        (token, rpc.time()+100, {'from': a[0]}),
        "dev: token"
    )

def set_checkpoint_not_token():
    '''set a checkpoint - not a token'''
    check.reverts(
        cp.newCheckpoint,
        (issuer, rpc.time()+100, {'from': a[0]}),
        "dev: token"
    )
    check.reverts(
        cp.newCheckpoint,
        (a[3], rpc.time()+100, {'from': a[0]}),
        "dev: token"
    )

def set_checkpoint_already_set():
    '''set a checkpoint - already exists'''
    cptime = rpc.time()+100
    cp.newCheckpoint(token, cptime, {'from': a[0]})
    check.reverts(
        cp.newCheckpoint,
        (token, cptime, {'from': a[0]}),
        "dev: already set"
    )

def set_checkpoint_second_token():
    '''set a checkpoint - second token'''
    token2 = accounts[0].deploy(SecurityToken, issuer, "Test Token", "TST", 1000000)
    issuer.addToken(token2, {'from': accounts[0]})
    issuer.attachModule(token2, cp, {'from': a[0]})
    cptime = rpc.time()+100
    cp.newCheckpoint(token, cptime, {'from': a[0]})
    cp.newCheckpoint(token2, cptime, {'from': a[0]})