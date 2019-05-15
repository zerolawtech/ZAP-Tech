from brownie import *

import itertools


def setup():
    global token, issuer
    kyc = accounts[0].deploy(KYCRegistrar, [accounts[0]], 1)
    issuer = accounts[0].deploy(IssuingEntity, [accounts[0]], 1)
    token = accounts[0].deploy(NFToken, issuer, "Test NFT", "NFT", 2**48 - 2)
    issuer.addToken(token, {'from': accounts[0]})
    issuer.setRegistrar(kyc, True, {'from': accounts[0]})

    # Approves accounts[1:21] in KYCRegistrar, with investor ratings 1-2 and country codes 1-3
    for count, country, rating in [(c, i[0], i[1]) for c, i in enumerate(itertools.product([1, 2, 3, 4, 5], [1, 2, 1, 2]), start=1)]:
        kyc.addInvestor("investor" + str(count), country, 'aws', rating, 9999999999, [accounts[count]], {'from': accounts[0]})

    # Approves investors from country codes 1-3 in IssuingEntity
    issuer.setCountries([1, 2, 3, 4, 5], [1, 1, 1, 1, 1], [0, 0, 0, 0, 0], {'from': accounts[0]})

    token.mint(issuer, 2**48 - 2, 0, "0x00", {'from': accounts[0]})


def fragment_new():
    '''Heavily fragment the token range'''

    for x in range(20):
        for i in range(1, 21):
            _transfer(0, i, 50000)

    for b in range(20000, 100000, 20000):
        for x in range(1, 11):
            for i in range(1, 22 - x):
                _transfer(i, i + x, b)

        for x in range(1, 11):
            for i in range(20, 0 + x, -1):
                _transfer(i, i - x, b)


def _transfer(from_, to, amount):
    check.confirms(
        token.transfer,
        (a[to], amount - 1, {'from': a[from_]}),
        "Transfer failed: {} tokens from {} to {}".format(amount, from_, to)
    )
