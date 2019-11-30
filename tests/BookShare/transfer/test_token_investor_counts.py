#!/usr/bin/python3

import pytest

from brownie import accounts


@pytest.fixture(scope="module", autouse=True)
def setup(approve_many, org, share):
    share.mint(org, 1000000, {"from": accounts[0]})


def test_org_to_member(check_counts, share):
    """member counts - org/member transfers"""
    check_counts()
    share.transfer(accounts[1], 1000, {"from": accounts[0]})
    check_counts(one=(1, 1, 0))
    share.transfer(accounts[1], 1000, {"from": accounts[0]})
    share.transfer(accounts[2], 1000, {"from": accounts[0]})
    share.transfer(accounts[3], 1000, {"from": accounts[0]})
    check_counts(one=(2, 1, 1), two=(1, 1, 0))
    share.transfer(accounts[1], 996000, {"from": accounts[0]})
    check_counts(one=(2, 1, 1), two=(1, 1, 0))
    share.transfer(accounts[0], 1000, {"from": accounts[1]})
    check_counts(one=(2, 1, 1), two=(1, 1, 0))
    share.transfer(accounts[0], 997000, {"from": accounts[1]})
    check_counts(one=(1, 0, 1), two=(1, 1, 0))
    share.transfer(accounts[0], 1000, {"from": accounts[2]})
    share.transfer(accounts[0], 1000, {"from": accounts[3]})
    check_counts()


def test_member_to_member(check_counts, share):
    """member counts - member/member transfers"""
    share.transfer(accounts[1], 1000, {"from": accounts[0]})
    share.transfer(accounts[2], 1000, {"from": accounts[0]})
    share.transfer(accounts[3], 1000, {"from": accounts[0]})
    share.transfer(accounts[4], 1000, {"from": accounts[0]})
    share.transfer(accounts[5], 1000, {"from": accounts[0]})
    share.transfer(accounts[6], 1000, {"from": accounts[0]})
    check_counts(one=(2, 1, 1), two=(2, 1, 1), three=(2, 1, 1))
    share.transfer(accounts[2], 500, {"from": accounts[1]})
    check_counts(one=(2, 1, 1), two=(2, 1, 1), three=(2, 1, 1))
    share.transfer(accounts[2], 500, {"from": accounts[1]})
    check_counts(one=(1, 0, 1), two=(2, 1, 1), three=(2, 1, 1))
    share.transfer(accounts[3], 2000, {"from": accounts[2]})
    check_counts(two=(2, 1, 1), three=(2, 1, 1))
    share.transfer(accounts[3], 1000, {"from": accounts[4]})
    check_counts(two=(1, 1, 0), three=(2, 1, 1))
    share.transfer(accounts[4], 500, {"from": accounts[3]})
    check_counts(two=(2, 1, 1), three=(2, 1, 1))
