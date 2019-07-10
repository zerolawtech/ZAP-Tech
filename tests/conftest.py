#!/usr/bin/python3

import functools
import itertools
import pytest


@pytest.fixture(autouse=True)
def isolate(test_isolation):
    pass


@pytest.fixture(scope="module")
def approve_many(kyc, issuer, accounts):
    issuer.setCountries((1, 2, 3), (1, 1, 1), (0, 0, 0), {'from': accounts[0]})
    product = itertools.product((1, 2, 3), (1, 2))
    for count, country, rating in [(c, i[0], i[1]) for c, i in enumerate(product, start=1)]:
        kyc.addInvestor(
            ("investor" + str(count)).encode(),
            country,
            '0x000001',
            rating,
            9999999999,
            (accounts[count],),
            {'from': accounts[0]}
        )


@pytest.fixture(scope="module")
def approve_one(kyc, issuer, accounts):
    issuer.setCountries((1, 2, 3), (1, 1, 1), (0, 0, 0), {'from': accounts[0]})
    kyc.addInvestor(
        "investor1".encode(),
        1,
        '0x000001',
        1,
        9999999999,
        (accounts[1],),
        {'from': accounts[0]}
    )


@pytest.fixture(scope="module")
def token(SecurityToken, issuer, accounts):
    t = accounts[0].deploy(SecurityToken, issuer, "Test Token", "TST", 1000000)
    issuer.addToken(t, {'from': accounts[0]})
    yield t


@pytest.fixture(scope="module")
def token2(SecurityToken, issuer, accounts, token):
    t = accounts[0].deploy(SecurityToken, issuer, "Test Token2", "TS2", 1000000)
    issuer.addToken(t, {'from': accounts[0]})
    yield t


@pytest.fixture(scope="module")
def nft(NFToken, issuer, accounts):
    token = accounts[0].deploy(NFToken, issuer, "Test NFT", "NFT", 1000000)
    issuer.addToken(token, {'from': accounts[0]})
    yield token


@pytest.fixture(scope="module")
def issuer(IssuingEntity, accounts):
    issuer = accounts[0].deploy(IssuingEntity, [accounts[0]], 1)
    yield issuer


@pytest.fixture(scope="module")
def kyc(KYCRegistrar, issuer, accounts):
    kyc = accounts[0].deploy(KYCRegistrar, [accounts[0]], 1)
    issuer.setRegistrar(kyc, False, {'from': accounts[0]})
    yield kyc


@pytest.fixture(scope="module")
def cust(OwnedCustodian, accounts, issuer):
    accounts[0].deploy(OwnedCustodian, [accounts[0]], 1)
    issuer.addCustodian(OwnedCustodian[0], {'from': accounts[0]})
    yield OwnedCustodian[0]


@pytest.fixture(scope="module")
def check_counts(issuer, approve_many):
    yield functools.partial(_check_countries, issuer)


def _check_countries(issuer, one=(0, 0, 0), two=(0, 0, 0), three=(0, 0, 0)):
    assert issuer.getInvestorCounts()[0][:3] == (
        one[0] + two[0] + three[0],
        one[1] + two[1] + three[1],
        one[2] + two[2] + three[2]
    )
    assert issuer.getCountry(1)[1][:3] == one
    assert issuer.getCountry(2)[1][:3] == two
    assert issuer.getCountry(3)[1][:3] == three
