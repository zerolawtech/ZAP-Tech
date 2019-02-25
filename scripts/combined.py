#!/usr/bin/python3

import itertools
import json
import os
from subprocess import Popen, DEVNULL

from brownie import *

SETUP_PUBKEY = [
    "0x01cf7cc93bfbf7b2c5f04a3bc9cb8b72bbcf2defcabdceb09860c493bdf1588d",
    "0x08d554bf59102bbb961ba81107ec71785ef9ce6638e5332b6c1a58b87447d181",
    "0x204e5d81d86c561f9344ad5f122a625f259996b065b80cbbe74a9ad97b6d7cc2",
    "0x02cb2a424885c9e412b94c40905b359e3043275cd29f5b557f008cd0a3e0c0dc"
]
CHAIN_ID = 1
SCALING_FACTOR = 10

local_accounts = []
params = {}
notes = {}


def send_tx(inputs, outputs, sender):
    '''Generates and sends an aztec transaction.

    arguments:
    inputs: list of input notes as found in the global dict 'notes'
    outputs: list of outputs notes as {'owner':account,'amount':int}
    sender: account to send tx from

    Calling this function will modify the global 'notes' dict, removing the spent
    notes and adding the newly generated ones.
    '''
    
    kPublic = sum(i['amount'] for i in inputs)-sum(i['amount'] for i in outputs)
    params.update({
        "inputNotes": [(i['owner'],i['hash']) for i in inputs],
        "outputs": [(i['owner'],i['amount']) for i in outputs],
        "kPublic": sum(i['amount'] for i in inputs)-sum(i['amount'] for i in outputs),
        "sender": sender
    })
    
    json.dump(params, open("aztec/params.json",'w'), indent=4, default=str)
    p = Popen(["node","aztec/get-proof"], stdin=DEVNULL, stdout=DEVNULL, stderr=DEVNULL)
    if p.wait():
        raise OSError("Could not generate transaction proofs")
    data = json.load(open('aztec/txdata.json','r'))
    os.unlink('aztec/txdata.json')
    os.unlink('aztec/params.json')

    tx = data['tx']
    bridge.confidentialTransfer(
        tx['proofData'],
        tx['m'],
        tx['challenge'],
        tx['inputSignatures'],
        tx['outputOwners'],
        tx['metadata'],
        {'from': sender}
    )

    for i in inputs:
        notes[i['owner']].remove(i)

    for i in range(len(outputs)):
        notes[outputs[i]['owner'].address].append({
            'hash': data['outputs'][i],
            'owner': outputs[i]['owner'].address,
            'amount': outputs[i]['amount']
        })

def setup_environment():

    global bridge, token
    owner = accounts.add()
    a[-2].transfer(owner, "50 ether")
    kyc = accounts[0].deploy(KYCRegistrar, [accounts[0]], 1)
    issuer = accounts[1].deploy(IssuingEntity, [accounts[1], owner], 1)
    token = accounts[1].deploy(SecurityToken, issuer, "Test Token", "TST", "10000 ether")
    
    issuer.addToken(token)
    token.modifyTotalSupply(issuer, "10000 ether")
    issuer.setRegistrar(kyc, True)
    
    a[0].deploy(AZTEC)
    AztecCustodian.bytecode = AztecCustodian.bytecode.replace(
        'AZTECInterface',
        'AZTEC'
    )
    bridge = a[0].deploy(
        AztecCustodian,
        SETUP_PUBKEY,
        token,
        SCALING_FACTOR,
        CHAIN_ID
    )

    issuer.addCustodian(bridge)

    issuer.setCountries([1,2,3],[1,1,1],[0,0,0])
    for count,country,rating in [(c,i[0],i[1]) for c,i in enumerate(itertools.product([1,2,3], [1,2]))]:
        local_accounts.append(accounts.add())
        notes[local_accounts[-1]] = []
        a[count].transfer(local_accounts[-1], "50 ether")
        kyc.addInvestor("investor"+str(count), country, 'aws', rating, 9999999999, [local_accounts[-1]])
        token.approve(bridge, "100 ether", {'from':local_accounts[-1]})
        token.transfer(local_accounts[-1], "100 ether", {'from':a[1]})

    params.update({
        'accounts': [i.private_key for i in local_accounts],
        "aztecContract": bridge,
        "chainId": CHAIN_ID,
        'issuerKey': owner.private_key
    })

def main():

    config['test']['default_contract_owner'] = True
    setup_environment()

    send_tx([], [
        {'owner': local_accounts[1], 'amount': 200},
        {'owner': local_accounts[1], 'amount': 100}
    ], local_accounts[0])

    send_tx(notes[local_accounts[1]], [
        {'owner': local_accounts[0], 'amount': 30},
        {'owner': local_accounts[2], 'amount': 60},
        {'owner': local_accounts[2], 'amount': 70},
        {'owner': local_accounts[1], 'amount': 5},
        {'owner': local_accounts[3], 'amount': 5},
        {'owner': local_accounts[3], 'amount': 130},
    ], local_accounts[1])

    send_tx(notes[local_accounts[0]], [
        {'owner': local_accounts[1], 'amount': 5}
    ], local_accounts[0])

    send_tx([], [
        {'owner': local_accounts[4], 'amount':100},
        {'owner': local_accounts[0], 'amount':50},
        {'owner': local_accounts[2], 'amount':50},
    ], local_accounts[4])

    send_tx(notes[local_accounts[4]], [
        {'owner': local_accounts[1], 'amount': 20},
        {'owner': local_accounts[3], 'amount': 20}
    ], local_accounts[4])