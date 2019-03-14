from brownie import *


def setup():
    config['test']['default_contract_owner'] = False

    global a, countries
    global owner1, owner2
    global unknown_address
    global registrar
    global investorID
    global issuer, token
    countries = [1, 2, 3]
    owner1 = accounts[0]
    owner2 = accounts[1]
    unknown_address = accounts[9]
    investorID = b"aaaainvestor"

    kyc = accounts[0].deploy(KYCRegistrar, [owner1], 1)
    issuer = owner1.deploy(IssuingEntity, [owner1], 1)
    token = owner1.deploy(SecurityToken, issuer, "Test Token", "TST", 1000000)
    issuer.addToken(token, {'from': owner1})
    issuer.setRegistrar(kyc, True, {'from': owner1})

    # Approves investors from country codes 1-3 in IssuingEntity
    issuer.setCountries([1, 2, 3], [1, 1, 1], [0, 0, 0], {'from': owner1})


# TODO: mint directly to Investor (instead of to issuer)
# TODO: review for completeness, these are mainly just the original tests

def mint_tokens_to_issuer():
    token.mint(issuer.address, 1000000, {'from': owner1})
    check.equal(token.balanceOf(issuer.address), 1000000)


def mint_tokens_by_unauthorised_address():
    check.reverts(
        token.mint,
        [issuer.address, 1, {'from': unknown_address}]
    )


def successful_burn():
    token.mint(issuer.address, 1000000, {'from': owner1})
    token.burn(issuer.address, 1000000, {'from': owner1})
    check.equal(token.balanceOf(issuer.address), 0)


def burn_by_unauthorised_address():
    token.mint(issuer.address, 1000000, {'from': owner1})
    check.reverts(
        token.burn,
        [issuer.address, 1000000, {'from': unknown_address}]
    )


def attempt_to_burn_more_tokens_than_balance():
    token.mint(issuer.address, 1000000, {'from': owner1})
    check.reverts(
        token.burn,
        [issuer.address, 2000000, {'from': owner1}]
    )


def attempt_to_burn_when_balance_is_zero():
    check.reverts(
        token.burn,
        [issuer.address, 1, {'from': owner1}]
    )


def attempt_to_burn_zero_tokens():
    token.mint(issuer.address, 1000000, {'from': owner1})
    check.reverts(
        token.burn,
        [issuer.address, 0, {'from': owner1}]
    )


def burn_correctly_reduces_total_supply():
    token.mint(issuer.address, 500000, {'from': owner1})
    token.burn(issuer.address, 100000, {'from': owner1})
    supply = token.totalSupply()
    check.equal(supply, 400000)
