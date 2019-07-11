#!/usr/bin/python3

import pytest

from brownie import accounts


@pytest.fixture(scope="module", autouse=True)
def setup(approve_many, issuer, nft):
    nft.mint(issuer, 100000, 0, "0x00", {'from': accounts[0]})


def test_sender_restricted(kyc, issuer, nft):
    '''sender restricted - investor / investor'''
    id_ = kyc.getID(accounts[1])
    nft.transfer(accounts[1], 1000, {'from': accounts[0]})
    issuer.setEntityRestriction(id_, True, {'from': accounts[0]})
    with pytest.reverts("Sender restricted: Issuer"):
        nft.transfer(accounts[2], 1000, {'from': accounts[1]})
    issuer.setEntityRestriction(id_, False, {'from': accounts[0]})
    nft.transfer(accounts[2], 1000, {'from': accounts[1]})


def test_sender_restricted_issuer(issuer, nft):
    '''sender restricted - issuer / investor'''
    with pytest.reverts("dev: authority"):
        issuer.setEntityRestriction(issuer.ownerID(), True, {'from': accounts[0]})
    issuer.addAuthorityAddresses(issuer.ownerID(), [accounts[-1]], {'from': accounts[0]})
    nft.transfer(accounts[1], 1000, {'from': accounts[-1]})
    issuer.removeAuthorityAddresses(issuer.ownerID(), [accounts[-1]], {'from': accounts[0]})
    with pytest.reverts("Restricted Authority Address"):
        nft.transfer(accounts[1], 1000, {'from': accounts[-1]})
    issuer.addAuthorityAddresses(issuer.ownerID(), [accounts[-1]], {'from': accounts[0]})
    nft.transfer(accounts[1], 1000, {'from': accounts[-1]})


def test_sender_restricted_kyc_id(kyc, nft):
    '''sender ID restricted at kyc'''
    nft.transfer(accounts[1], 1000, {'from': accounts[0]})
    kyc.setInvestorRestriction(kyc.getID(accounts[1]), True, {'from': accounts[0]})
    with pytest.reverts("Sender restricted: Registrar"):
        nft.transfer(accounts[2], 1000, {'from': accounts[1]})


def test_sender_restricted_kyc_addr(kyc, nft):
    '''sender address restricted at kyc'''
    nft.transfer(accounts[1], 1000, {'from': accounts[0]})
    kyc.restrictAddresses(kyc.getID(accounts[1]), [accounts[1]], {'from': accounts[0]})
    with pytest.reverts("Sender restricted: Registrar"):
        nft.transfer(accounts[2], 1000, {'from': accounts[1]})


def test_receiver_restricted_issuer(issuer, nft):
    '''receiver restricted'''
    issuer.setEntityRestriction(issuer.getID(accounts[1]), True, {'from': accounts[0]})
    with pytest.reverts("Receiver restricted: Issuer"):
        nft.transfer(accounts[1], 1000, {'from': accounts[0]})


def test_receiver_restricted_kyc_id(kyc, nft):
    '''receiver ID restricted at kyc'''
    kyc.setInvestorRestriction(kyc.getID(accounts[1]), True, {'from': accounts[0]})
    with pytest.reverts("Receiver restricted: Registrar"):
        nft.transfer(accounts[1], 1000, {'from': accounts[0]})


def test_receiver_restricted_kyc_addr(kyc, nft):
    '''receiver address restricted at kyc'''
    kyc.restrictAddresses(kyc.getID(accounts[1]), [accounts[1]], {'from': accounts[0]})
    with pytest.reverts("Receiver restricted: Registrar"):
        nft.transfer(accounts[1], 1000, {'from': accounts[0]})


def test_authority_permission(issuer, nft):
    '''authority transfer permission'''
    issuer.addAuthority([accounts[-1]], ["0xa9059cbb"], 2000000000, 1, {'from': accounts[0]})
    nft.transfer(accounts[1], 1000, {'from': accounts[-1]})
    issuer.setAuthoritySignatures(
        issuer.getID(accounts[-1]),
        ["0xa9059cbb"],
        False,
        {'from': accounts[0]}
    )
    with pytest.reverts("Authority not permitted"):
        nft.transfer(accounts[1], 1000, {'from': accounts[-1]})
    nft.transfer(accounts[-1], 100, {'from': accounts[1]})


def test_receiver_blocked_rating(issuer, nft):
    '''receiver blocked - rating'''
    issuer.setCountry(1, True, 3, (0, 0, 0, 0, 0, 0, 0, 0), {'from': accounts[0]})
    with pytest.reverts("Receiver blocked: Rating"):
        nft.transfer(accounts[1], 1000, {'from': accounts[0]})


def test_receiver_blocked_country(issuer, nft):
    '''receiver blocked - country'''
    issuer.setCountry(1, False, 1, (0, 0, 0, 0, 0, 0, 0, 0), {'from': accounts[0]})
    with pytest.reverts("Receiver blocked: Country"):
        nft.transfer(accounts[1], 1000, {'from': accounts[0]})
