#!/usr/bin/python3

import itertools

from brownie import *


def main(share_contract=BookShare, countries=(1, 2, 3), ratings=(1, 2)):
    share, issuer, kyc = deploy_contracts(share_contract)
    add_investors(countries, ratings)
    return share, issuer, kyc


def deploy_contracts(share_contract=BookShare):
    kyc = accounts[0].deploy(IDVerifierRegistrar, [accounts[0]], 1)
    issuer = accounts[0].deploy(OrgCode, [accounts[0]], 1)
    share = accounts[0].deploy(share_contract, issuer, "Test Token", "TST", 1000000)
    issuer.addOrgShare(share, {"from": accounts[0]})
    issuer.setVerifier(kyc, False, {"from": accounts[0]})
    return share, issuer, kyc


def deploy_custodian():
    accounts[0].deploy(OwnedCustodian, [a[0]], 1)
    OrgCode[0].addCustodian(OwnedCustodian[0], {"from": a[0]})
    return OwnedCustodian[0]


def add_investors(countries=(1, 2, 3), ratings=(1, 2)):
    # Approves accounts[1:7] in IDVerifierRegistrar[0], investor ratings 1-2 and country codes 1-3
    product = itertools.product(countries, ratings)
    for count, country, rating in [
        (c, i[0], i[1]) for c, i in enumerate(product, start=1)
    ]:
        IDVerifierRegistrar[0].addInvestor(
            ("investor" + str(count)).encode(),
            country,
            "0x000001",
            rating,
            9999999999,
            [accounts[count]],
            {"from": accounts[0]},
        )
    # Approves investors from country codes 1-3 in OrgCode[0]
    OrgCode[0].setCountries(
        countries, [1] * len(countries), [0] * len(countries), {"from": accounts[0]}
    )
