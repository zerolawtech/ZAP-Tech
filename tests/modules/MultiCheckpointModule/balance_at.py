#!/usr/bin/python3

import time

from brownie import *
from scripts.deployment import main


def setup():
    main(SecurityToken)
    global token, issuer, cp
    token = SecurityToken[0]
    issuer = IssuingEntity[0]
    cp = a[0].deploy(MultiCheckpointModule, issuer)
    for i in range(1, 6):
        token.mint(a[i], 1000*i, {'from': a[0]})
    issuer.attachModule(token, cp, {'from': a[0]})

def check_balances():
    '''check balances'''
    cptime = rpc.time()+100
    cp.newCheckpoint(token, cptime, {'from': a[0]})
    rpc.sleep(110)
    for i in range(1, 6):
        check.equal(cp.balanceAt(token, a[i], cptime), i*1000)

def moved_after():
    '''check balances - moved after checkpoint'''
    cptime = rpc.time()+100
    cp.newCheckpoint(token, cptime, {'from': a[0]})
    rpc.sleep(110)
    for i in range(1, 6):
        check.equal(cp.balanceAt(token, a[i], cptime), i*1000)
        token.transfer(a[0], 1000, {'from':a[i]})
        check.equal(cp.balanceAt(token, a[i], cptime), i*1000)

def moved_before():
    '''check balances - moved before checkpoint'''
    cptime = rpc.time()+100
    cp.newCheckpoint(token, cptime, {'from': a[0]})
    for i in range(1, 6):
        token.transfer(a[0], 1000, {'from':a[i]})
    rpc.sleep(110)
    for i in range(1, 6):
        check.equal(cp.balanceAt(token, a[i], cptime), (i-1)*1000)


def moved_before_after():
    '''check balances - moved before and after checkpoint'''
    cptime = rpc.time()+100
    cp.newCheckpoint(token, cptime, {'from': a[0]})
    for i in range(1, 6):
        token.transfer(a[0], 1000, {'from':a[i]})
    rpc.sleep(110)
    for i in range(1, 6):
        check.equal(cp.balanceAt(token, a[i], cptime), (i-1)*1000)
        token.transfer(a[i], 1000, {'from':a[0]})
        check.equal(cp.balanceAt(token, a[i], cptime), (i-1)*1000)


def multiple_checkpoints():
    '''check balances - multiple checkpoints'''
    cptime = rpc.time()+100
    cp.newCheckpoint(token, cptime, {'from': a[0]})
    cp.newCheckpoint(token, cptime+100, {'from': a[0]})
    rpc.sleep(110)
    for i in range(1, 6):
        check.equal(cp.balanceAt(token, a[i], cptime), i*1000)
    rpc.sleep(110)
    for i in range(1, 6):
        check.equal(cp.balanceAt(token, a[i], cptime), i*1000)
        check.equal(cp.balanceAt(token, a[i], cptime+100), i*1000)