from brownie import *
from scripts.nftoken import main


def setup():
    config['test']['always_transact'] = False
    config['test']['default_contract_owner'] = True
    main()
    global token, issuer
    token = NFToken[0]
    issuer = IssuingEntity[0]

def mint_no_merge_owner():
    '''Mint and do not merge - different owners'''
    token.mint(a[1], 10000, 0, "0x00")
    token.mint(a[2], 5000, 0, "0x00")
    check.equal(token.totalSupply(), 15000)
    check.equal(token.rangesOf(a[1]), ((1,10001),))
    check.equal(token.balanceOf(a[1]), 10000)
    check.equal(token.rangesOf(a[2]), ((10001,15001),))
    check.equal(token.balanceOf(a[2]), 5000)

def mint_no_merge_tag():
    '''Mint and do not merge - different tags'''
    token.mint(a[1], 10000, 0, "0x00")
    token.mint(a[1], 5000, 0, "0x01")
    check.equal(token.totalSupply(), 15000)
    check.equal(token.rangesOf(a[1]), ((1,10001), (10001,15001)))
    check.equal(token.balanceOf(a[1]), 15000)

def mint_merge():
    '''Mint and merge range'''
    token.mint(a[1], 10000, 0, "0x00")
    token.mint(a[1], 5000, 0, "0x00")
    check.equal(token.totalSupply(), 15000)
    check.equal(token.rangesOf(a[1]), ((1,15001),))
    check.equal(token.balanceOf(a[1]), 15000)

def burn():
    '''Burn'''
    token.mint(a[1], 10000, 0, "0x00")
    token.mint(a[2], 5000, 0, "0x00")
    token.mint(a[1], 5000, 0, "0x00")
    check.equal(token.totalSupply(), 20000)
    check.equal(token.rangesOf(a[1]), ((1,10001),(15001,20001)))
    check.equal(token.rangesOf(a[2]), ((10001,15001),))
    token.burn(10001, 15001)
    check.equal(token.totalSupply(), 15000)
    check.equal(token.rangesOf(a[1]), ((1,10001),(15001,20001)))
    check.equal(token.rangesOf(a[2]), tuple())
    check.equal(token.balanceOf(a[2]), 0)