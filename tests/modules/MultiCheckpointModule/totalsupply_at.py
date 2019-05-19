#!/usr/bin/python3

import time

from brownie import *
from scripts.deployment import main


def setup():
    global token, issuer, cp
    token, issuer, _ = main(SecurityToken, (1,), (1,))
    cp = a[0].deploy(MultiCheckpointModule, issuer)
    token.mint(a[1], 10000, {'from': a[0]})
    issuer.attachModule(token, cp, {'from': a[0]})

def check_balances():
    '''check totalSupply'''
    cptime = rpc.time()+100
    cp.newCheckpoint(token, cptime, {'from': a[0]})
    rpc.sleep(110)
    check.equal(cp.totalSupplyAt(token, cptime), 10000)


def mint_before():
    '''minted before checkpoint'''
    cptime = rpc.time()+100
    cp.newCheckpoint(token, cptime, {'from': a[0]})
    token.mint(a[1], 10000, {'from': a[0]})
    rpc.sleep(110)
    check.equal(cp.totalSupplyAt(token, cptime), 20000)


def mint_after():
    '''minted after checkpoint'''
    cptime = rpc.time()+100
    cp.newCheckpoint(token, cptime, {'from': a[0]})
    rpc.sleep(110)
    token.mint(a[1], 10000, {'from': a[0]})
    check.equal(cp.totalSupplyAt(token, cptime), 10000)


def mint_before_after():
    '''minted before and after checkpoint'''
    cptime = rpc.time()+100
    cp.newCheckpoint(token, cptime, {'from': a[0]})
    token.mint(a[1], 10000, {'from': a[0]})
    rpc.sleep(110)
    token.mint(a[1], 10000, {'from': a[0]})
    check.equal(cp.totalSupplyAt(token, cptime), 20000)


def two_checkpoints():
    '''check totalSupply - two checkpoints'''
    cptime = rpc.time()+100
    cp.newCheckpoint(token, cptime, {'from': a[0]})
    cp.newCheckpoint(token, cptime+100, {'from': a[0]})
    rpc.sleep(110)
    check.equal(cp.totalSupplyAt(token, cptime), 10000)
    rpc.sleep(110)
    check.equal(cp.totalSupplyAt(token, cptime), 10000)
    check.equal(cp.totalSupplyAt(token, cptime+100), 10000)

def two_mint_before():
    '''two checkpoints - mint before'''
    cptime = rpc.time()+100
    cp.newCheckpoint(token, cptime, {'from': a[0]})
    cp.newCheckpoint(token, cptime+100, {'from': a[0]})
    token.mint(a[1], 10000, {'from': a[0]})
    rpc.sleep(110)
    check.equal(cp.totalSupplyAt(token, cptime), 20000)
    rpc.sleep(110)
    check.equal(cp.totalSupplyAt(token, cptime), 20000)
    check.equal(cp.totalSupplyAt(token, cptime+100), 20000)

def two_mint_in_between():
    '''two checkpoints - mint in between'''
    cptime = rpc.time()+100
    cp.newCheckpoint(token, cptime, {'from': a[0]})
    cp.newCheckpoint(token, cptime+100, {'from': a[0]})
    rpc.sleep(110)
    check.equal(cp.totalSupplyAt(token, cptime), 10000)
    token.mint(a[1], 10000, {'from': a[0]})
    rpc.sleep(110)
    check.equal(cp.totalSupplyAt(token, cptime), 10000)
    check.equal(cp.totalSupplyAt(token, cptime+100), 20000)

def two_mint_after():
    '''two checkpoints - mint after'''
    cptime = rpc.time()+100
    cp.newCheckpoint(token, cptime, {'from': a[0]})
    cp.newCheckpoint(token, cptime+100, {'from': a[0]})
    rpc.sleep(110)
    check.equal(cp.totalSupplyAt(token, cptime), 10000)
    rpc.sleep(110)
    token.mint(a[1], 10000, {'from': a[0]})
    check.equal(cp.totalSupplyAt(token, cptime), 10000)
    check.equal(cp.totalSupplyAt(token, cptime+100), 10000)


def two_mint_before_after():
    '''two checkpoints - mint before and after'''
    cptime = rpc.time()+100
    cp.newCheckpoint(token, cptime, {'from': a[0]})
    cp.newCheckpoint(token, cptime+100, {'from': a[0]})
    token.mint(a[1], 10000, {'from': a[0]})
    rpc.sleep(110)
    check.equal(cp.totalSupplyAt(token, cptime), 20000)
    rpc.sleep(110)
    token.mint(a[1], 10000, {'from': a[0]})
    check.equal(cp.totalSupplyAt(token, cptime), 20000)
    check.equal(cp.totalSupplyAt(token, cptime+100), 20000)



def two_mint_before_inbetween_after():
    '''two checkpoints - mint before, in between, after'''
    cptime = rpc.time()+100
    cp.newCheckpoint(token, cptime, {'from': a[0]})
    cp.newCheckpoint(token, cptime+100, {'from': a[0]})
    token.mint(a[1], 10000, {'from': a[0]})
    rpc.sleep(110)
    check.equal(cp.totalSupplyAt(token, cptime), 20000)
    token.mint(a[1], 10000, {'from': a[0]})
    rpc.sleep(110)
    token.mint(a[1], 10000, {'from': a[0]})
    check.equal(cp.totalSupplyAt(token, cptime), 20000)
    check.equal(cp.totalSupplyAt(token, cptime+100), 30000)


def three_checkpoints():
    '''check totalSupply - two checkpoints'''
    cptime = rpc.time()+100
    cp.newCheckpoint(token, cptime, {'from': a[0]})
    cp.newCheckpoint(token, cptime+100, {'from': a[0]})
    cp.newCheckpoint(token, cptime+200, {'from': a[0]})
    rpc.sleep(110)
    check.equal(cp.totalSupplyAt(token, cptime), 10000)
    rpc.sleep(110)
    check.equal(cp.totalSupplyAt(token, cptime), 10000)
    check.equal(cp.totalSupplyAt(token, cptime+100), 10000)
    rpc.sleep(110)
    check.equal(cp.totalSupplyAt(token, cptime), 10000)
    check.equal(cp.totalSupplyAt(token, cptime+100), 10000)
    check.equal(cp.totalSupplyAt(token, cptime+200), 10000)


def three_before():
    '''three checkpoints - mint before'''
    cptime = rpc.time()+100
    cp.newCheckpoint(token, cptime, {'from': a[0]})
    cp.newCheckpoint(token, cptime+100, {'from': a[0]})
    cp.newCheckpoint(token, cptime+200, {'from': a[0]})
    token.mint(a[1], 10000, {'from': a[0]})
    rpc.sleep(310)
    check.equal(cp.totalSupplyAt(token, cptime), 20000)
    check.equal(cp.totalSupplyAt(token, cptime+100), 20000)
    check.equal(cp.totalSupplyAt(token, cptime+200), 20000)


def three_after():
    '''three checkpoints - mint after'''
    cptime = rpc.time()+100
    cp.newCheckpoint(token, cptime, {'from': a[0]})
    cp.newCheckpoint(token, cptime+100, {'from': a[0]})
    cp.newCheckpoint(token, cptime+200, {'from': a[0]})
    rpc.sleep(310)
    token.mint(a[1], 10000, {'from': a[0]})
    check.equal(cp.totalSupplyAt(token, cptime), 10000)
    check.equal(cp.totalSupplyAt(token, cptime+100), 10000)
    check.equal(cp.totalSupplyAt(token, cptime+200), 10000)


def three_between_first_second():
    '''three checkpoints - mint between first and second'''
    cptime = rpc.time()+100
    cp.newCheckpoint(token, cptime, {'from': a[0]})
    cp.newCheckpoint(token, cptime+100, {'from': a[0]})
    cp.newCheckpoint(token, cptime+200, {'from': a[0]})
    rpc.sleep(110)
    token.mint(a[1], 10000, {'from': a[0]})
    rpc.sleep(210)
    check.equal(cp.totalSupplyAt(token, cptime), 10000)
    check.equal(cp.totalSupplyAt(token, cptime+100), 20000)
    check.equal(cp.totalSupplyAt(token, cptime+200), 20000)


def three_between_second_third():
    '''three checkpoints - mint between second and third'''
    cptime = rpc.time()+100
    cp.newCheckpoint(token, cptime, {'from': a[0]})
    cp.newCheckpoint(token, cptime+100, {'from': a[0]})
    cp.newCheckpoint(token, cptime+200, {'from': a[0]})
    rpc.sleep(210)
    token.mint(a[1], 10000, {'from': a[0]})
    rpc.sleep(110)
    check.equal(cp.totalSupplyAt(token, cptime), 10000)
    check.equal(cp.totalSupplyAt(token, cptime+100), 10000)
    check.equal(cp.totalSupplyAt(token, cptime+200), 20000)

def three_between():
    '''three checkpoints - mint in between'''
    cptime = rpc.time()+100
    cp.newCheckpoint(token, cptime, {'from': a[0]})
    cp.newCheckpoint(token, cptime+100, {'from': a[0]})
    cp.newCheckpoint(token, cptime+200, {'from': a[0]})
    rpc.sleep(110)
    token.mint(a[1], 10000, {'from': a[0]})
    rpc.sleep(110)
    token.mint(a[1], 10000, {'from': a[0]})
    rpc.sleep(110)
    check.equal(cp.totalSupplyAt(token, cptime), 10000)
    check.equal(cp.totalSupplyAt(token, cptime+100), 20000)
    check.equal(cp.totalSupplyAt(token, cptime+200), 30000)



def three_before_after():
    '''three checkpoints - mint before and after'''
    cptime = rpc.time()+100
    cp.newCheckpoint(token, cptime, {'from': a[0]})
    cp.newCheckpoint(token, cptime+100, {'from': a[0]})
    cp.newCheckpoint(token, cptime+200, {'from': a[0]})
    token.mint(a[1], 10000, {'from': a[0]})
    rpc.sleep(310)
    token.mint(a[1], 10000, {'from': a[0]})
    check.equal(cp.totalSupplyAt(token, cptime), 20000)
    check.equal(cp.totalSupplyAt(token, cptime+100), 20000)
    check.equal(cp.totalSupplyAt(token, cptime+200), 20000)


def three_before_in_betwee_after():
    '''three checkpoints - moved before, in between, after'''
    cptime = rpc.time()+100
    cp.newCheckpoint(token, cptime, {'from': a[0]})
    cp.newCheckpoint(token, cptime+100, {'from': a[0]})
    cp.newCheckpoint(token, cptime+200, {'from': a[0]})
    token.mint(a[1], 10000, {'from': a[0]})
    rpc.sleep(110)
    token.mint(a[1], 10000, {'from': a[0]})
    rpc.sleep(110)
    token.mint(a[1], 10000, {'from': a[0]})
    rpc.sleep(110)
    token.mint(a[1], 10000, {'from': a[0]})
    check.equal(cp.totalSupplyAt(token, cptime), 20000)
    check.equal(cp.totalSupplyAt(token, cptime+100), 30000)
    check.equal(cp.totalSupplyAt(token, cptime+200), 40000)