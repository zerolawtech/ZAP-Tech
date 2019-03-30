#!/usr/bin/python3

from brownie import *
from scripts.deployment import main


def setup():
    config['test']['always_transact'] = False
    main(SecurityToken)
    global token, issuer, id1, id2
    token = SecurityToken[0]
    issuer = IssuingEntity[0]
    for i in range(10):
        a.add()
    issuer.addAuthority([a[-2]], [], 2000000000, 1, {'from': a[0]})
    issuer.addAuthority([a[-1]], [], 2000000000, 1, {'from': a[0]})
    id1 = issuer.getID(a[-2])
    id2 =issuer.getID(a[-1])

def add_addr_owner():
    '''add addresses to owner'''
    issuer.addAuthorityAddresses(issuer.ownerID(), a[-6:-4], {'from': a[0]})
    check.equal(issuer.getAuthority(issuer.ownerID()), (1, 3, 0))
    issuer.addAuthorityAddresses(issuer.ownerID(), [a[-4]], {'from': a[0]})
    check.equal(issuer.getAuthority(issuer.ownerID()), (1, 4, 0))

def remove_addr_owner():
    '''remove addresses from owner'''
    issuer.addAuthorityAddresses(issuer.ownerID(), a[-10:-5], {'from': a[0]})
    issuer.removeAuthorityAddresses(issuer.ownerID(), a[-10:-6], {'from': a[0]})
    check.equal(issuer.getAuthority(issuer.ownerID()), (1, 2, 0))

def add_remove_owner():
    '''add and remove - owner'''
    issuer.addAuthorityAddresses(issuer.ownerID(), a[-10:-5], {'from': a[0]})
    issuer.removeAuthorityAddresses(issuer.ownerID(), a[-10:-6], {'from': a[0]})
    issuer.addAuthorityAddresses(issuer.ownerID(), [a[-10],a[-9],a[-4]], {'from': a[0]})
    check.equal(issuer.getAuthority(issuer.ownerID()), (1, 5, 0))


def add_addr_auth():
    '''add addresses to subauthorities'''
    issuer.addAuthorityAddresses(id1, a[-10:-7], {'from': a[0]})
    check.equal(issuer.getAuthority(id1), (1, 4, 2000000000))
    issuer.addAuthorityAddresses(id1, [a[-7]], {'from': a[0]})
    check.equal(issuer.getAuthority(id1), (1, 5, 2000000000))
    issuer.addAuthorityAddresses(id2, a[-4:-2], {'from': a[0]})
    check.equal(issuer.getAuthority(id2), (1, 3, 2000000000))
