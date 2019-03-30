#!/usr/bin/python3

from brownie import *
from scripts.deployment import main


def setup():
    config['test']['always_transact'] = False
    main(SecurityToken)
    global token, issuer, ownerid, id1, id2
    token = SecurityToken[0]
    issuer = IssuingEntity[0]
    for i in range(10):
        a.add()
    issuer.addAuthority([a[-2]], [], 2000000000, 1, {'from': a[0]})
    issuer.addAuthority([a[-1]], [], 2000000000, 1, {'from': a[0]})
    ownerid = issuer.ownerID()
    id1 = issuer.getID(a[-2])
    id2 =issuer.getID(a[-1])

def add_addr_owner():
    '''add addresses to owner'''
    issuer.addAuthorityAddresses(ownerid, a[-6:-4], {'from': a[0]})
    check.equal(issuer.getAuthority(ownerid), (1, 3, 0))
    issuer.addAuthorityAddresses(ownerid, (a[-4],), {'from': a[0]})
    check.equal(issuer.getAuthority(ownerid), (1, 4, 0))

def remove_addr_owner():
    '''remove addresses from owner'''
    issuer.addAuthorityAddresses(ownerid, a[-10:-5], {'from': a[0]})
    issuer.removeAuthorityAddresses(ownerid, a[-10:-6], {'from': a[0]})
    check.equal(issuer.getAuthority(ownerid), (1, 2, 0))

def add_remove_owner():
    '''add and remove - owner'''
    issuer.addAuthorityAddresses(ownerid, a[-10:-5], {'from': a[0]})
    issuer.removeAuthorityAddresses(ownerid, a[-10:-6], {'from': a[0]})
    issuer.addAuthorityAddresses(ownerid, (a[-10], a[-9], a[-4]), {'from': a[0]})
    check.equal(issuer.getAuthority(ownerid), (1, 5, 0))

def add_addr_auth():
    '''add addresses to authorities'''
    issuer.addAuthorityAddresses(id1, a[-10:-7], {'from': a[0]})
    check.equal(issuer.getAuthority(id1), (1, 4, 2000000000))
    issuer.addAuthorityAddresses(id1, (a[-7],), {'from': a[0]})
    check.equal(issuer.getAuthority(id1), (1, 5, 2000000000))
    issuer.addAuthorityAddresses(id2, a[-4:-2], {'from': a[0]})
    check.equal(issuer.getAuthority(id2), (1, 3, 2000000000))

def remove_addr_auth():
    '''remove addresses from authorities'''
    issuer.addAuthorityAddresses(id1, a[-10:-7], {'from': a[0]})
    issuer.addAuthorityAddresses(id2, a[-4:-2], {'from': a[0]})
    issuer.removeAuthorityAddresses(id1, a[-10:-8], {'from': a[0]})
    issuer.removeAuthorityAddresses(id2, a[-4:-2], {'from': a[0]})
    check.equal(issuer.getAuthority(id1), (1, 2, 2000000000))
    check.equal(issuer.getAuthority(id2), (1, 1, 2000000000))

def add_remove_auth():
    '''add and remove - authorities'''
    issuer.addAuthorityAddresses(id1, a[-10:-7], {'from': a[0]})
    issuer.addAuthorityAddresses(id2, a[-7:-5], {'from': a[0]})
    issuer.removeAuthorityAddresses(id1, a[-10:-8], {'from': a[0]})
    issuer.removeAuthorityAddresses(id2, [a[-7]], {'from': a[0]})
    issuer.addAuthorityAddresses(id1, (a[-10], a[-9], a[-5]), {'from': a[0]})
    issuer.addAuthorityAddresses(id2, (a[-7], a[-4]), {'from': a[0]})
    check.equal(issuer.getAuthority(id1), (1, 5, 2000000000))
    check.equal(issuer.getAuthority(id2), (1, 4, 2000000000))

def add_known():
    '''add known addresses'''
    issuer.addAuthorityAddresses(id1, a[-10:-7], {'from': a[0]})
    check.reverts(
        issuer.addAuthorityAddresses,
        (id1, a[-9:-6], {'from': a[0]}),
        "dev: known address"
    )
    check.reverts(
        issuer.addAuthorityAddresses,
        (id1, (a[-6], a[-5], a[-6]), {'from': a[0]}),
        "dev: known address"
    )

def add_other():
    '''add already assocaited address'''
    token.mint(a[1], 100, {'from': a[0]})
    issuer.addAuthorityAddresses(id1, (a[-10],), {'from': a[0]})
    check.reverts(
        issuer.addAuthorityAddresses,
        (id1, (a[-10],), {'from': a[0]}),
        "dev: known address"
    )
    check.reverts(
        issuer.addAuthorityAddresses,
        (id1, (a[1],), {'from': a[0]}),
        "dev: known address"
    )


def remove_below_threshold():
    '''remove below threshold'''
    issuer.addAuthorityAddresses(id1, a[-10:-7], {'from': a[0]})
    issuer.setAuthorityThreshold(id1, 3, {'from': a[0]})
    check.reverts(
        issuer.removeAuthorityAddresses,
        (id1, a[-10:-7], {'from': a[0]}),
        "dev: count below threshold"
    )
    issuer.removeAuthorityAddresses(id1, (a[-10],), {'from': a[0]})
    check.reverts(
        issuer.removeAuthorityAddresses,
        (id1, a[-9:-7], {'from': a[0]}),
        "dev: count below threshold"
    )
    check.reverts(
        issuer.removeAuthorityAddresses,
        (id2, (a[-1],), {'from': a[0]}),
        "dev: count below threshold"
    )

def remove_unknown_addresses():
    '''remove unknown addresses'''
    issuer.addAuthorityAddresses(id1, a[-10:-8], {'from': a[0]})
    check.reverts(
        issuer.removeAuthorityAddresses,
        (id1, a[-10:-6], {'from': a[0]}),
        "dev: wrong ID"
    )

def remove_repeat():
    '''remove already restricted address'''
    issuer.addAuthorityAddresses(id1, a[-10:-8], {'from': a[0]})
    check.reverts(
        issuer.removeAuthorityAddresses,
        (id1, (a[-10], a[-9], a[-10]), {'from': a[0]}),
        "dev: already restricted"
    )

def add_unknown_id():
    '''add to unknown id'''
    check.reverts(
        issuer.addAuthorityAddresses,
        ("0x1234", a[-10:-8], {'from': a[0]}),
        "dev: unknown ID"
    )

def remove_unknown_id():
    '''remove from unknown id'''
    check.reverts(
        issuer.removeAuthorityAddresses,
        ("0x1234", (a[-10],), {'from': a[0]}),
        "dev: wrong ID"
    )