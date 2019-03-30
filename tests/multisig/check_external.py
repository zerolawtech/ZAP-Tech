#!/usr/bin/python3

from brownie import *
from scripts.deployment import main


def setup():
    config['test']['always_transact'] = False
    main(SecurityToken)
    global token, nft, issuer, ownerid, id1
    token = SecurityToken[0]
    issuer = IssuingEntity[0]
    nft = a[0].deploy(NFToken, issuer, "Test NFT", "NFT", 1000000)
    issuer.addToken(nft, {'from': a[0]})
    for i in range(6):
        a.add()
        a[0].transfer(a[-1], "1 ether")
    issuer.addAuthority(a[-6:-3],[], 2000000000, 1, {'from': a[0]})
    ownerid = issuer.ownerID()
    id1 = issuer.getID(a[-6])

def modifyAuthorizedSupply():
    _multisig(token.modifyAuthorizedSupply, 10000)
    rpc.revert()
    _multisig(nft.modifyAuthorizedSupply, 10000)





def _multisig(fn, *args):
    args = list(args)+[{'from':a[-6]}]
    # check for failed call, no permission
    check.reverts(fn, args, "dev: not permitted")
    # give permission and check for successful call
    issuer.setAuthoritySignatures(id1, [fn.signature], True, {'from': a[0]})
    check.event_fired(fn(*args),'MultiSigCallApproved')
    rpc.revert()
    # give permission, threhold to 3, check for success and fails
    issuer.setAuthoritySignatures(id1, [fn.signature], True, {'from': a[0]})
    issuer.setAuthorityThreshold(id1, 3, {'from': a[0]})
    args[-1]['from'] = a[-6]
    check.event_not_fired(fn(*args), 'MultiSigCallApproved')
    check.reverts(fn, args, "dev: repeat caller")
    args[-1]['from'] = a[-5]
    check.event_not_fired(fn(*args), 'MultiSigCallApproved')
    check.reverts(fn, args, "dev: repeat caller")
    args[-1]['from'] = a[-4]
    check.event_fired(fn(*args),'MultiSigCallApproved')
    
    
