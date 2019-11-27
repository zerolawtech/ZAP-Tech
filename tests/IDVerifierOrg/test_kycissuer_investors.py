#!/usr/bin/python3

import pytest

from brownie import accounts

id_ = "member1".encode()


def test_add_member(ikyc):
    '''add member'''
    assert not ikyc.isRegistered("0x1234")
    ikyc.addMember("0x1234", 1, 1, 1, 9999999999, (accounts[3],), {'from': accounts[0]})
    assert ikyc.isRegistered("0x1234")
    assert ikyc.getMember(accounts[3])[1:] == (True, 1, 1)
    assert ikyc.getExpires("0x1234") == 9999999999


def test_add_member_country_zero(ikyc):
    '''add member - country 0'''
    with pytest.reverts("dev: country 0"):
        ikyc.addMember(
            "0x1234",
            0,
            1,
            1,
            9999999999,
            (accounts[1], accounts[2]),
            {'from': accounts[0]}
        )


def test_add_member_rating_zero(ikyc):
    '''add member - rating 0'''
    with pytest.reverts("dev: rating 0"):
        ikyc.addMember(
            "0x1234",
            1,
            1,
            0,
            9999999999,
            (accounts[1], accounts[2]),
            {'from': accounts[0]}
        )


def test_add_member_authority_id(ikyc, org):
    '''add member - known authority ID'''
    oid = org.ownerID()
    with pytest.reverts("dev: authority ID"):
        ikyc.addMember(oid, 1, 1, 1, 9999999999, (accounts[2],), {'from': accounts[0]})


def test_add_member_member_id(ikyc):
    '''add member - known member ID'''
    with pytest.reverts("dev: member ID"):
        ikyc.addMember(id_, 1, 1, 1, 9999999999, (accounts[3],), {'from': accounts[0]})


def test_update_member(ikyc, share):
    '''update member'''
    assert ikyc.isRegistered(id_)
    ikyc.updateMember(id_, 2, 4, 1234567890, {'from': accounts[0]})
    assert ikyc.isRegistered(id_)
    assert ikyc.getMember(accounts[1])[1:] == (False, 4, 1)
    assert ikyc.getExpires(id_) == 1234567890
    assert ikyc.getRegion(id_) == "0x000002"


def test_update_member_unknown_id(ikyc, org):
    '''update member - unknown ID'''
    oid = org.ownerID()
    with pytest.reverts("dev: unknown ID"):
        ikyc.updateMember("0x1234", 1, 1, 9999999999, {'from': accounts[0]})
    with pytest.reverts("dev: unknown ID"):
        ikyc.updateMember(oid, 1, 1, 9999999999, {'from': accounts[0]})


def test_update_member_rating_zero(ikyc):
    '''update member - rating zero'''
    with pytest.reverts("dev: rating 0"):
        ikyc.updateMember(id_, 1, 0, 9999999999, {'from': accounts[0]})


def test_set_restriction(ikyc):
    '''set member restriction'''
    assert ikyc.isPermittedID(id_)
    ikyc.setMemberRestriction(id_, True, {'from': accounts[0]})
    assert not ikyc.isPermittedID(id_)
    ikyc.setMemberRestriction(id_, False, {'from': accounts[0]})
    assert ikyc.isPermittedID(id_)
