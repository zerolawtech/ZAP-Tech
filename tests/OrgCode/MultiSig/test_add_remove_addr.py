#!/usr/bin/python3

import pytest

from brownie import accounts


@pytest.fixture(scope="module", autouse=True)
def setup(org, token):
    for i in range(10):
        accounts.add()
    sigs = (
        org.signatures['addAuthorityAddresses'],
        org.signatures['removeAuthorityAddresses'],
    )
    org.addAuthority([accounts[-2]], sigs, 2000000000, 1, {'from': accounts[0]})
    org.addAuthority([accounts[-1]], sigs, 2000000000, 1, {'from': accounts[0]})
    accounts[0].transfer(accounts[-2], "1 ether")
    accounts[0].transfer(accounts[-1], "1 ether")


@pytest.fixture(scope="module")
def ownerid(org):
    yield org.ownerID()


@pytest.fixture(scope="module")
def id1(org):
    yield org.getID(accounts[-2])


@pytest.fixture(scope="module")
def id2(org):
    yield org.getID(accounts[-1])


def test_add_addr_owner(org, ownerid):
    '''add addresses to owner'''
    org.addAuthorityAddresses(ownerid, accounts[-6:-4], {'from': accounts[0]})
    assert org.getAuthority(ownerid) == (3, 1, 0)
    org.addAuthorityAddresses(ownerid, (accounts[-4],), {'from': accounts[0]})
    assert org.getAuthority(ownerid) == (4, 1, 0)


def test_remove_addr_owner(org, ownerid):
    '''remove addresses from owner'''
    org.addAuthorityAddresses(ownerid, accounts[-10:-5], {'from': accounts[0]})
    org.removeAuthorityAddresses(ownerid, accounts[-10:-6], {'from': accounts[0]})
    assert org.getAuthority(ownerid) == (2, 1, 0)


def test_add_remove_owner(org, ownerid):
    '''add and remove - owner'''
    org.addAuthorityAddresses(ownerid, accounts[-10:-5], {'from': accounts[0]})
    org.removeAuthorityAddresses(ownerid, accounts[-10:-6], {'from': accounts[0]})
    org.addAuthorityAddresses(
        ownerid,
        (accounts[-10], accounts[-9], accounts[-4]),
        {'from': accounts[0]}
    )
    assert org.getAuthority(ownerid) == (5, 1, 0)


def test_add_addr_auth(org, id1, id2):
    '''add addresses to authorities'''
    org.addAuthorityAddresses(id1, accounts[-10:-7], {'from': accounts[0]})
    assert org.getAuthority(id1) == (4, 1, 2000000000)
    org.addAuthorityAddresses(id1, (accounts[-7],), {'from': accounts[0]})
    assert org.getAuthority(id1) == (5, 1, 2000000000)
    org.addAuthorityAddresses(id2, accounts[-4:-2], {'from': accounts[0]})
    assert org.getAuthority(id2) == (3, 1, 2000000000)


def test_remove_addr_auth(org, id1, id2):
    '''remove addresses from authorities'''
    org.addAuthorityAddresses(id1, accounts[-10:-7], {'from': accounts[0]})
    org.addAuthorityAddresses(id2, accounts[-4:-2], {'from': accounts[0]})
    org.removeAuthorityAddresses(id1, accounts[-10:-8], {'from': accounts[0]})
    org.removeAuthorityAddresses(id2, accounts[-4:-2], {'from': accounts[0]})
    assert org.getAuthority(id1) == (2, 1, 2000000000)
    assert org.getAuthority(id2) == (1, 1, 2000000000)


def test_add_remove_auth(org, id1, id2):
    '''add and remove - authorities'''
    org.addAuthorityAddresses(id1, accounts[-10:-7], {'from': accounts[0]})
    org.addAuthorityAddresses(id2, accounts[-7:-5], {'from': accounts[0]})
    org.removeAuthorityAddresses(id1, accounts[-10:-8], {'from': accounts[0]})
    org.removeAuthorityAddresses(id2, [accounts[-7]], {'from': accounts[0]})
    org.addAuthorityAddresses(
        id1,
        (accounts[-10], accounts[-9], accounts[-5]),
        {'from': accounts[0]}
    )
    org.addAuthorityAddresses(id2, (accounts[-7], accounts[-4]), {'from': accounts[0]})
    assert org.getAuthority(id1) == (5, 1, 2000000000)
    assert org.getAuthority(id2) == (4, 1, 2000000000)


def test_add_known(org, id1):
    '''add known addresses'''
    org.addAuthorityAddresses(id1, accounts[-10:-7], {'from': accounts[0]})
    with pytest.reverts("dev: known address"):
        org.addAuthorityAddresses(id1, accounts[-9:-6], {'from': accounts[0]})
    with pytest.reverts("dev: known address"):
        org.addAuthorityAddresses(
            id1,
            (accounts[-6], accounts[-5], accounts[-6]),
            {'from': accounts[0]}
        )


def test_add_other(set_countries, org, kyc, token, id1):
    '''add already associated address'''
    kyc.addInvestor(
        b'investor1',
        1,
        '0x000001',
        1,
        9999999999,
        (accounts[1],),
        {'from': accounts[0]}
    )
    token.mint(accounts[1], 100, {'from': accounts[0]})
    org.addAuthorityAddresses(id1, (accounts[-10],), {'from': accounts[0]})
    with pytest.reverts("dev: known address"):
        org.addAuthorityAddresses(id1, (accounts[-10],), {'from': accounts[0]})
    with pytest.reverts("dev: known address"):
        org.addAuthorityAddresses(id1, (accounts[1],), {'from': accounts[0]})


def test_remove_below_threshold(org, id1, id2):
    '''remove below threshold'''
    org.addAuthorityAddresses(id1, accounts[-10:-7], {'from': accounts[0]})
    org.setAuthorityThreshold(id1, 3, {'from': accounts[0]})
    with pytest.reverts("dev: count below threshold"):
        org.removeAuthorityAddresses(id1, accounts[-10:-7], {'from': accounts[0]})
    org.removeAuthorityAddresses(id1, (accounts[-10],), {'from': accounts[0]})
    with pytest.reverts("dev: count below threshold"):
        org.removeAuthorityAddresses(id1, accounts[-9:-7], {'from': accounts[0]})
    with pytest.reverts("dev: count below threshold"):
        org.removeAuthorityAddresses(id2, (accounts[-1],), {'from': accounts[0]})


def test_remove_unknown_addresses(org, id1):
    '''remove unknown addresses'''
    org.addAuthorityAddresses(id1, accounts[-10:-8], {'from': accounts[0]})
    with pytest.reverts("dev: wrong ID"):
        org.removeAuthorityAddresses(id1, accounts[-10:-6], {'from': accounts[0]})


def test_remove_repeat(org, id1):
    '''remove already restricted address'''
    org.addAuthorityAddresses(id1, accounts[-10:-8], {'from': accounts[0]})
    with pytest.reverts("dev: already restricted"):
        org.removeAuthorityAddresses(
            id1,
            (accounts[-10], accounts[-9], accounts[-10]),
            {'from': accounts[0]}
        )


def test_add_unknown_id(org):
    '''add to unknown id'''
    with pytest.reverts("dev: unknown ID"):
        org.addAuthorityAddresses("0x1234", accounts[-10:-8], {'from': accounts[0]})


def test_remove_unknown_id(org):
    '''remove from unknown id'''
    with pytest.reverts("dev: wrong ID"):
        org.removeAuthorityAddresses("0x1234", (accounts[-10],), {'from': accounts[0]})


def test_authority_add_to_self(org, id1, id2):
    '''authority - add to self'''
    org.addAuthorityAddresses(id1, accounts[-10:-8], {'from': accounts[-2]})
    org.addAuthorityAddresses(id2, accounts[-8:-6], {'from': accounts[-1]})


def test_authority_remove_self(org, id1, id2):
    '''authority - remove from self'''
    org.addAuthorityAddresses(id1, accounts[-10:-8], {'from': accounts[-2]})
    org.addAuthorityAddresses(id2, accounts[-8:-6], {'from': accounts[-1]})
    org.removeAuthorityAddresses(id1, accounts[-10:-8], {'from': accounts[-2]})
    org.removeAuthorityAddresses(id2, (accounts[-8], accounts[-1]), {'from': accounts[-1]})


def test_authority_add_to_other(org, id1):
    '''authority - add to other'''
    with pytest.reverts("dev: wrong authority"):
        org.addAuthorityAddresses(id1, accounts[-10:-8], {'from': accounts[-1]})


def test_authority_remove_from_other(org, id1):
    '''authority - remove from olther'''
    org.addAuthorityAddresses(id1, accounts[-10:-8], {'from': accounts[-2]})
    with pytest.reverts("dev: wrong authority"):
        org.removeAuthorityAddresses(id1, accounts[-10:-8], {'from': accounts[-1]})
