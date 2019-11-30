#!/usr/bin/python3

import pytest

from brownie import accounts


@pytest.fixture(scope="module", autouse=True)
def setup(org, share, kyc2):
    org.setVerifier(kyc2, False, {"from": accounts[0]})
    share.mint(org, 1000000, {"from": accounts[0]})


@pytest.fixture(scope="module")
def kyc2(IDVerifierRegistrar, org):
    kyc2 = accounts[0].deploy(IDVerifierRegistrar, [accounts[0]], 1)
    org.setVerifier(kyc2, False, {"from": accounts[0]})
    yield kyc2


def test_unknown_address(org):
    """unknown address"""
    org.getID(accounts[0])
    with pytest.reverts("Address not registered"):
        org.getID(accounts[1])


def test_registrar_restricted(org, kyc):
    """registrar restricted"""
    kyc.addMember("0x1234", 1, 1, 1, 9999999999, (accounts[1],), {"from": accounts[0]})
    org.getID.transact(accounts[1])
    org.setVerifier(kyc, True, {"from": accounts[0]})
    with pytest.reverts("Verifier restricted"):
        org.getID(accounts[1])


def test_different_registrar(org, kyc, kyc2):
    """multiple registrars, different addresses"""
    kyc.addMember(
        "0x1234", 1, 1, 1, 9999999999, (accounts[1], accounts[3]), {"from": accounts[0]}
    )
    kyc2.addMember(
        "0x1234", 1, 1, 1, 9999999999, (accounts[1], accounts[2]), {"from": accounts[0]}
    )
    org.setVerifier(kyc2, True, {"from": accounts[0]})
    org.getID.transact(accounts[1])
    org.setVerifier(kyc2, False, {"from": accounts[0]})
    with pytest.reverts("Address not registered"):
        org.getID(accounts[2])
    org.getID(accounts[3])


def test_restrict_registrar(org, kyc, kyc2):
    """change registrar"""
    kyc.addMember(
        "0x1234", 1, 1, 1, 9999999999, (accounts[1], accounts[3]), {"from": accounts[0]}
    )
    kyc2.addMember(
        "0x1234", 1, 1, 1, 9999999999, (accounts[1], accounts[2]), {"from": accounts[0]}
    )
    org.getID(accounts[1])
    org.setVerifier(kyc, True, {"from": accounts[0]})
    org.getID(accounts[1])
    org.getID(accounts[2])
    with pytest.reverts("Address not registered"):
        org.getID(accounts[3])


def test_cust_auth_id(org, kyc, rpc):
    """member / authority collisions"""
    org.addAuthority([accounts[-1]], [], 2000000000, 1, {"from": accounts[0]})
    id_ = org.getID(accounts[-1])
    kyc.addMember(
        id_, 1, 1, 1, 9999999999, (accounts[1], accounts[3]), {"from": accounts[0]}
    )
    with pytest.reverts("Address not registered"):
        org.getID(accounts[1])
    rpc.revert()
    kyc.addMember(
        id_, 1, 1, 1, 9999999999, (accounts[1], accounts[3]), {"from": accounts[0]}
    )
    org.getID.transact(accounts[1])
    with pytest.reverts("dev: known ID"):
        org.addAuthority([accounts[-1]], [], 2000000000, 1, {"from": accounts[0]})
