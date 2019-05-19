#!/usr/bin/python3

import time

from brownie import *
from scripts.deployment import main, deploy_custodian


def setup():
    global token, issuer, cust, cp
    token, issuer, _ = main(SecurityToken, (1,2,3,4,5), (1,))
    cust = deploy_custodian()
    cp = a[0].deploy(MultiCheckpointModule, issuer)
    for i in range(1, 6):
        token.mint(a[i], 3000*i, {'from': a[0]})
        token.transfer(cust, 1000*i, {'from': a[i]})
    issuer.attachModule(token, cp, {'from': a[0]})

def check_balances():
    '''check balances'''
    cptime = rpc.time()+100
    cp.newCheckpoint(token, cptime, {'from': a[0]})
    rpc.sleep(110)
    for i in range(1, 6):
        check.equal(cp.custodianBalanceAt(token, a[i], cust, cptime), i*1000)


def moved_before():
    '''moved before checkpoint'''
    cptime = rpc.time()+100
    cp.newCheckpoint(token, cptime, {'from': a[0]})
    for i in range(1, 6):
        cust.transferInternal(token, a[i], a[0], 1000, {'from':a[0]})
    rpc.sleep(110)
    for i in range(1, 6):
        check.equal(cp.custodianBalanceAt(token, a[i], cust, cptime), (i-1)*1000)


def moved_after():
    '''moved after checkpoint'''
    cptime = rpc.time()+100
    cp.newCheckpoint(token, cptime, {'from': a[0]})
    rpc.sleep(110)
    for i in range(1, 6):
        check.equal(cp.custodianBalanceAt(token, a[i], cust, cptime), i*1000)
        cust.transferInternal(token, a[i], a[0], 1000, {'from':a[0]})
        check.equal(cp.custodianBalanceAt(token, a[i], cust, cptime), i*1000)


def moved_before_after():
    '''moved before and after checkpoint'''
    cptime = rpc.time()+100
    cp.newCheckpoint(token, cptime, {'from': a[0]})
    for i in range(1, 6):
        cust.transferInternal(token, a[i], a[0], 1000, {'from':a[0]})
    rpc.sleep(110)
    for i in range(1, 6):
        check.equal(cp.custodianBalanceAt(token, a[i], cust, cptime), (i-1)*1000)
        cust.transferInternal(token, a[0], a[i], 1000, {'from':a[0]})
        check.equal(cp.custodianBalanceAt(token, a[i], cust, cptime), (i-1)*1000)


def two_checkpoints():
    '''check balances - two checkpoints'''
    cptime = rpc.time()+100
    cp.newCheckpoint(token, cptime, {'from': a[0]})
    cp.newCheckpoint(token, cptime+100, {'from': a[0]})
    rpc.sleep(110)
    for i in range(1, 6):
        check.equal(cp.custodianBalanceAt(token, a[i], cust, cptime), i*1000)
    rpc.sleep(110)
    for i in range(1, 6):
        check.equal(cp.custodianBalanceAt(token, a[i], cust, cptime), i*1000)
        check.equal(cp.custodianBalanceAt(token, a[i], cust, cptime+100), i*1000)


def two_moved_before():
    '''two checkpoints - moved before'''
    cptime = rpc.time()+100
    cp.newCheckpoint(token, cptime, {'from': a[0]})
    cp.newCheckpoint(token, cptime+100, {'from': a[0]})
    for i in range(1, 6):
        cust.transferInternal(token, a[i], a[0], 1000, {'from':a[0]})
    rpc.sleep(110)
    for i in range(1, 6):
        check.equal(cp.custodianBalanceAt(token, a[i], cust, cptime), (i-1)*1000)
    rpc.sleep(110)
    for i in range(1, 6):
        check.equal(cp.custodianBalanceAt(token, a[i], cust, cptime), (i-1)*1000)
        check.equal(cp.custodianBalanceAt(token, a[i], cust, cptime+100), (i-1)*1000)


def two_moved_in_between():
    '''two checkpoints - moved in between'''
    cptime = rpc.time()+100
    cp.newCheckpoint(token, cptime, {'from': a[0]})
    cp.newCheckpoint(token, cptime+100, {'from': a[0]})
    rpc.sleep(110)
    for i in range(1, 6):
        cust.transferInternal(token, a[i], a[0], 1000, {'from':a[0]})
    rpc.sleep(110)
    for i in range(1, 6):
        check.equal(cp.custodianBalanceAt(token, a[i], cust, cptime), i*1000)
        check.equal(cp.custodianBalanceAt(token, a[i], cust, cptime+100), (i-1)*1000)


def two_moved_after():
    '''two checkpoints - moved after'''
    cptime = rpc.time()+100
    cp.newCheckpoint(token, cptime, {'from': a[0]})
    cp.newCheckpoint(token, cptime+100, {'from': a[0]})
    rpc.sleep(210)
    for i in range(1, 6):
        cust.transferInternal(token, a[i], a[0], 1000, {'from':a[0]})
        check.equal(cp.custodianBalanceAt(token, a[i], cust, cptime), i*1000)
        check.equal(cp.custodianBalanceAt(token, a[i], cust, cptime+100), i*1000)


def two_moved_before_after():
    '''two checkpoints - moved before and after'''
    cptime = rpc.time()+100
    cp.newCheckpoint(token, cptime, {'from': a[0]})
    cp.newCheckpoint(token, cptime+100, {'from': a[0]})
    for i in range(1, 6):
        cust.transferInternal(token, a[i], a[0], 1000, {'from':a[0]})
    rpc.sleep(210)
    for i in range(1, 6):
        cust.transferInternal(token, a[0], a[i], 1000, {'from':a[0]})
        check.equal(cp.custodianBalanceAt(token, a[i], cust, cptime), (i-1)*1000)
        check.equal(cp.custodianBalanceAt(token, a[i], cust, cptime+100), (i-1)*1000)


def two_moved_before_in_between_after():
    '''two checkpoints - moved before, in between, after'''
    cptime = rpc.time()+100
    cp.newCheckpoint(token, cptime, {'from': a[0]})
    cp.newCheckpoint(token, cptime+100, {'from': a[0]})
    for i in range(1, 6):
        cust.transferInternal(token, a[i], a[0], 1000, {'from':a[0]})
    rpc.sleep(110)
    for i in range(1, 6):
        cust.transferInternal(token, a[0], a[i], 1000, {'from':a[0]})
    rpc.sleep(110)
    for i in range(1, 6):
        cust.transferInternal(token, a[i], a[0], 1000, {'from':a[0]})
        check.equal(cp.custodianBalanceAt(token, a[i], cust, cptime), (i-1)*1000)
        check.equal(cp.custodianBalanceAt(token, a[i], cust, cptime+100), i*1000)

def three_checkpoints():
    '''check balances - three checkpoints'''
    cptime = rpc.time()+100
    cp.newCheckpoint(token, cptime, {'from': a[0]})
    cp.newCheckpoint(token, cptime+100, {'from': a[0]})
    cp.newCheckpoint(token, cptime+200, {'from': a[0]})
    rpc.sleep(110)
    for i in range(1, 6):
        check.equal(cp.custodianBalanceAt(token, a[i], cust, cptime), i*1000)
    rpc.sleep(110)
    for i in range(1, 6):
        check.equal(cp.custodianBalanceAt(token, a[i], cust, cptime), i*1000)
        check.equal(cp.custodianBalanceAt(token, a[i], cust, cptime+100), i*1000)
    rpc.sleep(110)
    for i in range(1, 6):
        check.equal(cp.custodianBalanceAt(token, a[i], cust, cptime), i*1000)
        check.equal(cp.custodianBalanceAt(token, a[i], cust, cptime+100), i*1000)
        check.equal(cp.custodianBalanceAt(token, a[i], cust, cptime+200), i*1000)

def three_before():
    '''three checkpoints - moved before'''
    cptime = rpc.time()+100
    cp.newCheckpoint(token, cptime, {'from': a[0]})
    cp.newCheckpoint(token, cptime+100, {'from': a[0]})
    cp.newCheckpoint(token, cptime+200, {'from': a[0]})
    for i in range(1, 6):
        cust.transferInternal(token, a[i], a[0], 1000, {'from':a[0]})
    rpc.sleep(310)
    for i in range(1, 6):
        check.equal(cp.custodianBalanceAt(token, a[i], cust, cptime), (i-1)*1000)
        check.equal(cp.custodianBalanceAt(token, a[i], cust, cptime+100), (i-1)*1000)
        check.equal(cp.custodianBalanceAt(token, a[i], cust, cptime+200), (i-1)*1000)

def three_after():
    '''three checkpoints - moved after'''
    cptime = rpc.time()+100
    cp.newCheckpoint(token, cptime, {'from': a[0]})
    cp.newCheckpoint(token, cptime+100, {'from': a[0]})
    cp.newCheckpoint(token, cptime+200, {'from': a[0]})
    rpc.sleep(310)
    for i in range(1, 6):
        cust.transferInternal(token, a[i], a[0], 1000, {'from':a[0]})
        check.equal(cp.custodianBalanceAt(token, a[i], cust, cptime), i*1000)
        check.equal(cp.custodianBalanceAt(token, a[i], cust, cptime+100), i*1000)
        check.equal(cp.custodianBalanceAt(token, a[i], cust, cptime+200), i*1000)


def three_between_first_second():
    '''three checkpoints - moved between first and second'''
    cptime = rpc.time()+100
    cp.newCheckpoint(token, cptime, {'from': a[0]})
    cp.newCheckpoint(token, cptime+100, {'from': a[0]})
    cp.newCheckpoint(token, cptime+200, {'from': a[0]})
    rpc.sleep(110)
    for i in range(1, 6):
        cust.transferInternal(token, a[i], a[0], 1000, {'from':a[0]})
    rpc.sleep(210)
    for i in range(1, 6):
        check.equal(cp.custodianBalanceAt(token, a[i], cust, cptime), i*1000)
        check.equal(cp.custodianBalanceAt(token, a[i], cust, cptime+100), (i-1)*1000)
        check.equal(cp.custodianBalanceAt(token, a[i], cust, cptime+200), (i-1)*1000)


def three_between_second_third():
    '''three checkpoints - moved between second and third'''
    cptime = rpc.time()+100
    cp.newCheckpoint(token, cptime, {'from': a[0]})
    cp.newCheckpoint(token, cptime+100, {'from': a[0]})
    cp.newCheckpoint(token, cptime+200, {'from': a[0]})
    rpc.sleep(210)
    for i in range(1, 6):
        cust.transferInternal(token, a[i], a[0], 1000, {'from':a[0]})
    rpc.sleep(110)
    for i in range(1, 6):
        check.equal(cp.custodianBalanceAt(token, a[i], cust, cptime), i*1000)
        check.equal(cp.custodianBalanceAt(token, a[i], cust, cptime+100), i*1000)
        check.equal(cp.custodianBalanceAt(token, a[i], cust, cptime+200), (i-1)*1000)

def three_between():
    '''three checkpoints - moved in between'''
    cptime = rpc.time()+100
    cp.newCheckpoint(token, cptime, {'from': a[0]})
    cp.newCheckpoint(token, cptime+100, {'from': a[0]})
    cp.newCheckpoint(token, cptime+200, {'from': a[0]})
    rpc.sleep(110)
    for i in range(1, 6):
        cust.transferInternal(token, a[i], a[0], 1000, {'from':a[0]})
    rpc.sleep(110)
    for i in range(1, 6):
        cust.transferInternal(token, a[0], a[i], 1000, {'from':a[0]})
    rpc.sleep(110)
    for i in range(1, 6):
        check.equal(cp.custodianBalanceAt(token, a[i], cust, cptime), i*1000)
        check.equal(cp.custodianBalanceAt(token, a[i], cust, cptime+100), (i-1)*1000)
        check.equal(cp.custodianBalanceAt(token, a[i], cust, cptime+200), i*1000)


def three_before_after():
    '''three checkpoints - moved before and after'''
    cptime = rpc.time()+100
    cp.newCheckpoint(token, cptime, {'from': a[0]})
    cp.newCheckpoint(token, cptime+100, {'from': a[0]})
    cp.newCheckpoint(token, cptime+200, {'from': a[0]})
    for i in range(1, 6):
        cust.transferInternal(token, a[i], a[0], 1000, {'from':a[0]})
    rpc.sleep(310)
    for i in range(1, 6):
        cust.transferInternal(token, a[0], a[i], 1000, {'from':a[0]})
        check.equal(cp.custodianBalanceAt(token, a[i], cust, cptime), (i-1)*1000)
        check.equal(cp.custodianBalanceAt(token, a[i], cust, cptime+100), (i-1)*1000)
        check.equal(cp.custodianBalanceAt(token, a[i], cust, cptime+200), (i-1)*1000)


def three_before_in_betwee_after():
    '''three checkpoints - moved before, in between, after'''
    cptime = rpc.time()+100
    cp.newCheckpoint(token, cptime, {'from': a[0]})
    cp.newCheckpoint(token, cptime+100, {'from': a[0]})
    cp.newCheckpoint(token, cptime+200, {'from': a[0]})
    for i in range(1, 6):
        cust.transferInternal(token, a[i], a[0], 1000, {'from':a[0]})
    rpc.sleep(110)
    for i in range(1, 6):
        cust.transferInternal(token, a[0], a[i], 1000, {'from':a[0]})
    rpc.sleep(110)
    for i in range(1, 6):
        cust.transferInternal(token, a[i], a[0], 1000, {'from':a[0]})
    rpc.sleep(110)
    for i in range(1, 6):
        cust.transferInternal(token, a[0], a[i], 1000, {'from':a[0]})
        check.equal(cp.custodianBalanceAt(token, a[i], cust, cptime), (i-1)*1000)
        check.equal(cp.custodianBalanceAt(token, a[i], cust, cptime+100), i*1000)
        check.equal(cp.custodianBalanceAt(token, a[i], cust, cptime+200), (i-1)*1000)
