import json
import os
from subprocess import Popen, DEVNULL


SETUP_PUBKEY = [
    "0x01cf7cc93bfbf7b2c5f04a3bc9cb8b72bbcf2defcabdceb09860c493bdf1588d",
    "0x08d554bf59102bbb961ba81107ec71785ef9ce6638e5332b6c1a58b87447d181",
    "0x204e5d81d86c561f9344ad5f122a625f259996b065b80cbbe74a9ad97b6d7cc2",
    "0x02cb2a424885c9e412b94c40905b359e3043275cd29f5b557f008cd0a3e0c0dc"
]
CHAIN_ID = 1
SCALING_FACTOR = "1 ether"

local_accounts = []
params = {}
notes = {}

def setup_environment():
    '''
    Set up the basic aztec environent:

     * Deploy the aztec contracts and a test ERC20
     * Create 5 new local accounts (needed so we can access the private keys)
     * Send 50 ether and 10000 test tokens to each account
     * Approve the aztec bridge contract to transfer tokens for each account
    '''

    global token, bridge
    token = a[0].deploy(ERC20)
    a[0].deploy(AZTEC)
    AZTECERC20Bridge.bytecode = AZTECERC20Bridge.bytecode.replace(
        'AZTECInterface',
        'AZTEC'
    )
    bridge = a[0].deploy(
        AZTECERC20Bridge,
        SETUP_PUBKEY,
        token,
        SCALING_FACTOR,
        CHAIN_ID
    )
    
    for i in range(5):
        local_accounts.append(accounts.add())
        notes[local_accounts[-1]] = []
        a[i].transfer(local_accounts[-1], "50 ether")
        token.approve(bridge, "10000 ether", {'from':local_accounts[-1]})
        token.transfer(local_accounts[-1], "10000 ether", {'from':a[0]})
    
    params.update({
        'accounts': [i.private_key for i in local_accounts],
        "aztecContract": bridge,
        "chainId": CHAIN_ID,
    })


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
    
    json.dump(params, open("params.json",'w'), indent=4, default=str)
    p = Popen(["node","get-proof"], stdin=DEVNULL, stdout=DEVNULL, stderr=DEVNULL)
    if p.wait():
        raise OSError("Could not generate transaction proofs")
    data = json.load(open('txdata.json','r'))
    os.unlink('txdata.json')
    os.unlink('params.json')

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


def deploy():

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

    send_tx(notes[local_accounts[3]], [
        {'owner': local_accounts[0], 'amount': 30}
    ], local_accounts[3])