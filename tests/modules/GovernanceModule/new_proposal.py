#!/usr/bin/python3

import time

from brownie import *
from scripts.deployment import main

proposal_inputs = ["0x1234", 1500000000, 2000000000, 2100000000, "test proposal", "0"*40, "0x"]

def setup():
    global token, issuer, cp, gov
    token, issuer, _ = main(SecurityToken, (1,2,3,4,5), (1,))
    cp = a[0].deploy(MultiCheckpointModule, issuer)
    for i in range(1, 6):
        token.mint(a[i], 1000*i, {'from': a[0]})
    issuer.attachModule(token, cp, {'from': a[0]})
    gov = a[0].deploy(GovernanceModule, issuer)
    issuer.setGovernance(gov, {'from': a[0]})
    proposal_inputs.append({'from': a[0]})

def new_proposal():
    gov.newProposal(*proposal_inputs)

def new_proposal_exists():
    gov.newProposal(*proposal_inputs)
    check.reverts(gov.newProposal, proposal_inputs, "dev: proposal already exists")

def new_proposal_start_before_now():
    p = proposal_inputs.copy()
    p[2] = 151000000
    check.reverts(gov.newProposal, p, "dev: start < now")

def new_proposal_start_before_cp():
    p = proposal_inputs.copy()
    p[1] = 2100000000
    check.reverts(gov.newProposal, p, "dev: start < checkpoint")

def new_proposal_end_before_start():
    p = proposal_inputs.copy()
    p[3] = 190000000
    check.reverts(gov.newProposal, p, "dev: end < start")
