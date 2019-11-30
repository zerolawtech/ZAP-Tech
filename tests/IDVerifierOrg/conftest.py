#!/usr/bin/python3

import pytest


@pytest.fixture(scope="module")
def ikyc(IDVerifierOrg, org, accounts):
    kyc = accounts[0].deploy(IDVerifierOrg, org)
    org.setVerifier(kyc, False, {"from": accounts[0]})
    kyc.addMember(
        "member1".encode(),
        1,
        "0x000001",
        1,
        9999999999,
        (accounts[1],),
        {"from": accounts[0]},
    )
    yield kyc
