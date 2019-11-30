#!/usr/bin/python3

import functools
import itertools
import pytest

from brownie import accounts
from brownie.convert import to_bytes


# test isolation, always use!


@pytest.fixture(autouse=True)
def isolation(fn_isolation):
    pass


# share deployments / linking


@pytest.fixture(scope="module")
def share(BookShare, org, accounts):
    t = accounts[0].deploy(BookShare, org, "Test Share", "TST", 1000000)
    org.addOrgShare(t, {"from": accounts[0]})
    yield t


@pytest.fixture(scope="module")
def share2(BookShare, org, accounts, share):
    t = accounts[0].deploy(BookShare, org, "Test Share2", "TS2", 1000000)
    org.addOrgShare(t, {"from": accounts[0]})
    yield t


@pytest.fixture(scope="module")
def nft(CertShare, org, accounts):
    share = accounts[0].deploy(CertShare, org, "Test NFT", "NFT", 1000000)
    org.addOrgShare(share, {"from": accounts[0]})
    yield share


@pytest.fixture(scope="module")
def org(OrgCode, accounts):
    org = accounts[0].deploy(OrgCode, [accounts[0]], 1)
    yield org


@pytest.fixture(scope="module")
def kyc(IDVerifierRegistrar, org, accounts):
    kyc = accounts[0].deploy(IDVerifierRegistrar, [accounts[0]], 1)
    org.setVerifier(kyc, False, {"from": accounts[0]})
    yield kyc


@pytest.fixture(scope="module")
def cust(OwnedCustodian, accounts, org):
    accounts[0].deploy(OwnedCustodian, [accounts[0]], 1)
    org.addCustodian(OwnedCustodian[0], {"from": accounts[0]})
    yield OwnedCustodian[0]


# member approval


@pytest.fixture(scope="module")
def ownerid(org):
    yield org.ownerID()


@pytest.fixture(scope="module")
def set_countries(org):
    org.setCountries((1, 2, 3), (1, 1, 1), (0, 0, 0), {"from": accounts[0]})


@pytest.fixture(scope="module")
def id1(set_countries, kyc):
    yield _add_member(kyc, 1, 1, 1)


@pytest.fixture(scope="module")
def id2(set_countries, kyc):
    yield _add_member(kyc, 2, 1, 2)


@pytest.fixture(scope="module")
def approve_many(id1, id2, kyc):
    product = list(itertools.product((2, 3), (1, 2)))
    for count, country, rating in [
        (c, i[0], i[1]) for c, i in enumerate(product, start=3)
    ]:
        _add_member(kyc, count, country, rating)


def _add_member(kyc, i, country, rating):
    id_ = to_bytes(f"member{i}".encode()).hex()
    kyc.addMember(
        id_,
        country,
        "0x000001",
        rating,
        9999999999,
        (accounts[i],),
        {"from": accounts[0]},
    )
    return id_


@pytest.fixture
def check_counts(org, approve_many, no_call_coverage):
    yield functools.partial(_check_countries, org)


def _check_countries(org, one=(0, 0, 0), two=(0, 0, 0), three=(0, 0, 0)):
    assert org.getMemberCounts()[0][:3] == (
        one[0] + two[0] + three[0],
        one[1] + two[1] + three[1],
        one[2] + two[2] + three[2],
    )
    assert org.getCountry(1)[1][:3] == one
    assert org.getCountry(2)[1][:3] == two
    assert org.getCountry(3)[1][:3] == three
