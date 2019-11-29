#!/usr/bin/python3

import pytest

from brownie import accounts


@pytest.fixture(scope="module", autouse=True)
def module_setup(kyc, auth_id):
    kyc.setAuthorityCountries(auth_id, (1,), False, {'from': accounts[0]})
    kyc.addMember("0x1111", 1, 1, 1, 9999999999, (accounts[-3],), {'from': accounts[0]})


def test_add_member(kyc):
    '''add member'''
    assert not kyc.isRegistered("0x1234")
    kyc.addMember("0x1234", 1, 1, 1, 9999999999, (accounts[3],), {'from': accounts[0]})
    assert kyc.isRegistered("0x1234")
    assert kyc.getMember(accounts[3])[1:] == (True, 1, 1)
    assert kyc.getExpires("0x1234") == 9999999999


def test_add_member_country_zero(kyc):
    '''add member - country 0'''
    with pytest.reverts("dev: country 0"):
        kyc.addMember(
            "0x1234",
            0,
            1,
            1,
            9999999999,
            (accounts[1], accounts[2]),
            {'from': accounts[0]}
        )


def test_add_member_rating_zero(kyc):
    '''add member - rating 0'''
    with pytest.reverts("dev: rating 0"):
        kyc.addMember(
            "0x1234",
            1,
            1,
            0,
            9999999999,
            (accounts[1], accounts[2]),
            {'from': accounts[0]}
        )


def test_add_member_authority_id(kyc, auth_id):
    '''add member - known authority ID'''
    with pytest.reverts("dev: authority ID"):
        kyc.addMember(
            auth_id,
            1,
            1,
            1,
            9999999999,
            (accounts[1], accounts[2]),
            {'from': accounts[0]}
        )


def test_add_member_member_id(kyc, auth_id):
    '''add member - known member ID'''
    with pytest.reverts("dev: member ID"):
        kyc.addMember("0x1111", 1, 1, 1, 9999999999, (accounts[3],), {'from': accounts[0]})


def test_add_member_authority_country(kyc, auth_id):
    '''add member - authority country permission'''
    with pytest.reverts("dev: country"):
        kyc.addMember("0x1234", 1, 1, 1, 9999999999, (accounts[3],), {'from': accounts[-1]})
    kyc.setAuthorityCountries(auth_id, (1,), True, {'from': accounts[0]})
    kyc.addMember("0x1234", 1, 1, 1, 9999999999, (accounts[3],), {'from': accounts[-1]})
    with pytest.reverts("dev: country"):
        kyc.addMember("0x5678", 2, 1, 1, 9999999999, (accounts[4],), {'from': accounts[-1]})
    kyc.setAuthorityCountries(auth_id, (1,), False, {'from': accounts[0]})
    with pytest.reverts("dev: country"):
        kyc.addMember("0x5678", 1, 1, 1, 9999999999, (accounts[4],), {'from': accounts[-1]})


def test_update_member(kyc):
    '''update member'''
    assert kyc.isRegistered("0x1111")
    kyc.updateMember("0x1111", 2, 4, 1234567890, {'from': accounts[0]})
    assert kyc.isRegistered("0x1111")
    assert kyc.getMember(accounts[-3])[1:] == (False, 4, 1)
    assert kyc.getExpires("0x1111") == 1234567890
    assert kyc.getRegion("0x1111") == "0x000002"


def test_update_member_unknown_id(kyc, auth_id):
    '''update member - unknown ID'''
    with pytest.reverts("dev: country 0"):
        kyc.updateMember("0x1234", 1, 1, 9999999999, {'from': accounts[0]})
    with pytest.reverts("dev: country 0"):
        kyc.updateMember(auth_id, 1, 1, 9999999999, {'from': accounts[0]})


def test_update_member_rating_zero(kyc):
    '''update member - rating zero'''
    with pytest.reverts("dev: rating 0"):
        kyc.updateMember("0x1111", 1, 0, 9999999999, {'from': accounts[0]})


def test_update_member_authority_country(kyc, auth_id):
    '''update member - authority country permission'''
    with pytest.reverts("dev: country"):
        kyc.updateMember("0x1111", 1, 1, 9999999999, {'from': accounts[-1]})
    kyc.setAuthorityCountries(auth_id, (1,), True, {'from': accounts[0]})
    kyc.updateMember("0x1111", 1, 1, 9999999999, {'from': accounts[-1]}),
    kyc.setAuthorityCountries(auth_id, (1,), False, {'from': accounts[0]})
    with pytest.reverts("dev: country"):
        kyc.updateMember("0x1111", 1, 1, 9999999999, {'from': accounts[-1]})


def test_set_restriction(kyc):
    '''set member restriction'''
    assert kyc.isPermittedID("0x1111")
    kyc.setMemberRestriction("0x1111", True, {'from': accounts[0]})
    assert not kyc.isPermittedID("0x1111")
    kyc.setMemberRestriction("0x1111", False, {'from': accounts[0]})
    assert kyc.isPermittedID("0x1111")


def test_set_authority(kyc, auth_id):
    '''set member authority'''
    assert kyc.isPermittedID("0x1111")
    kyc.setAuthorityRestriction(auth_id, True, {'from': accounts[0]})
    assert kyc.isPermittedID("0x1111")
    kyc.setMemberAuthority(auth_id, ("0x1111",), {'from': accounts[0]})
    assert not kyc.isPermittedID("0x1111")
    kyc.setMemberAuthority(kyc.getAuthorityID(accounts[0]), ("0x1111",), {'from': accounts[0]})
    assert kyc.isPermittedID("0x1111")


def test_set_authority_unknown_id(kyc, auth_id):
    '''set member authority - unknown id'''
    id_ = kyc.getAuthorityID(accounts[0])
    with pytest.reverts("dev: unknown ID"):
        kyc.setMemberAuthority(id_, (auth_id,), {'from': accounts[0]})
    with pytest.reverts("dev: unknown ID"):
        kyc.setMemberAuthority(auth_id, (id_,), {'from': accounts[0]})
    with pytest.reverts("dev: unknown ID"):
        kyc.setMemberAuthority(id_, ("0x1234",), {'from': accounts[0]})
