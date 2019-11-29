#!/usr/bin/python3

import pytest

from brownie import accounts


@pytest.fixture(scope="module", autouse=True)
def setup(org):
    for i in range(3):
        accounts.add()
        accounts[0].transfer(accounts[-1], "1 ether")
    sigs = (
        org.signatures['setAuthoritySignatures'],
        org.signatures['setAuthorityApprovedUntil'],
        org.signatures['setAuthorityThreshold']
    )
    org.addAuthority((accounts[-2],), sigs, 2000000000, 1, {'from': accounts[0]})
    org.addAuthority((accounts[-1], accounts[-3]), sigs, 2000000000, 1, {'from': accounts[0]})


@pytest.fixture(scope="module")
def id1(org):
    yield org.getID(accounts[-2])


@pytest.fixture(scope="module")
def id2(org):
    yield org.getID(accounts[-1])


def test_set_approval(org, id1):
    '''set authrority approved until'''
    org.setAuthorityApprovedUntil(id1, 12345, {'from': accounts[0]})
    assert org.getAuthority(id1) == (1, 1, 12345)
    org.setAuthorityApprovedUntil(id1, 0, {'from': accounts[0]})
    assert org.getAuthority(id1) == (1, 1, 0)
    org.setAuthorityApprovedUntil(id1, 2000000000, {'from': accounts[0]})
    assert org.getAuthority(id1) == (1, 1, 2000000000)


def test_set_approval_as_authority(org, id1):
    '''set authority approved until - as authority (reverts)'''
    with pytest.reverts():
        org.setAuthorityApprovedUntil(id1, 12345, {'from': accounts[-2]})


def test_set_signatures(org, id1):
    '''set authority signatures'''
    sigs = (
        org.signatures['addAuthorityAddresses'],
        org.signatures['removeAuthorityAddresses']
    )
    assert not org.isApprovedAuthority(accounts[-2], sigs[0])
    assert not org.isApprovedAuthority(accounts[-2], sigs[1])
    org.setAuthoritySignatures(id1, sigs, True, {'from': accounts[0]})
    assert org.isApprovedAuthority(accounts[-2], sigs[0])
    assert org.isApprovedAuthority(accounts[-2], sigs[1])
    org.setAuthoritySignatures(id1, sigs, False, {'from': accounts[0]})
    assert not org.isApprovedAuthority(accounts[-2], sigs[0])
    assert not org.isApprovedAuthority(accounts[-2], sigs[1])


def test_set_sigs_as_authority(org, id1):
    '''set authority signatures - as authority (reverts)'''
    with pytest.reverts():
        org.setAuthoritySignatures(
            id1,
            (org.signatures['setAuthoritySignatures'],),
            True,
            {'from': accounts[-2]}
        )


def test_set_threshold(org, id2):
    '''set threshold'''
    org.setAuthorityThreshold(id2, 2, {'from': accounts[0]})
    assert org.getAuthority(id2) == (2, 2, 2000000000)
    org.setAuthorityThreshold(id2, 1, {'from': accounts[0]})
    assert org.getAuthority(id2) == (2, 1, 2000000000)


def test_set_threshold_as_authority(org, id2):
    '''set threshold as authority'''
    org.setAuthorityThreshold(id2, 2, {'from': accounts[-1]})
    assert org.getAuthority(id2) == (2, 2, 2000000000)
    org.setAuthorityThreshold(id2, 1, {'from': accounts[-1]})
    assert org.getAuthority(id2) == (2, 2, 2000000000)
    org.setAuthorityThreshold(id2, 1, {'from': accounts[-3]})
    assert org.getAuthority(id2) == (2, 1, 2000000000)


def test_set_threshold_as_authority_not_permitted(org, id2):
    '''set threshold as authority, not permitted'''
    org.setAuthoritySignatures(
        id2,
        (org.signatures['setAuthorityThreshold'],),
        False,
        {'from': accounts[0]}
    )
    with pytest.reverts():
        org.setAuthorityThreshold(id2, 2, {'from': accounts[-1]})
    org.setAuthoritySignatures(
        id2,
        (org.signatures['setAuthorityThreshold'],),
        True,
        {'from': accounts[0]}
    )
    org.setAuthorityThreshold(id2, 2, {'from': accounts[-1]})


def test_set_other_authority_threshold(org, id1):
    '''set other authority threshold (reverts)'''
    with pytest.reverts("dev: wrong authority"):
        org.setAuthorityThreshold(id1, 1, {'from': accounts[-1]})


def test_set_threshold_too_high(org, id1):
    '''set threshold too high'''
    with pytest.reverts("dev: threshold too high"):
        org.setAuthorityThreshold(id1, 2, {'from': accounts[-2]})
