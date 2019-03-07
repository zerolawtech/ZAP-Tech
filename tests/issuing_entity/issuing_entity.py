from brownie import *

def setup():
    config['test']['default_contract_owner'] = False

    global a, countries
    global owner1, owner2
    global authority1, authority2
    global investor1, investor2
    global scratch1 
    global ahash, investorID
    countries = [1,2,3]
    a = accounts
    owner1 = a[0]; 
    owner2 = a[1]
    authority1 = a[2]; 
    authority2 = a[3]
    investor1 = a[4]; 
    investor2 = a[5]
    scratch1 = a[9]
    investorID = ahash = "0xe3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"

#########################################
# getID success path tests

def getID_via_issuer():
    issuer = owner1.deploy(IssuingEntity, [owner1], 1)
    registrar = owner1.deploy(KYCRegistrar, [owner1], 1)
    check.true(issuer.setRegistrar(registrar, True, {'from':owner1}).return_value)
    registrar.addInvestor(investorID, 3, b'abc', 1, 9999999999, [scratch1], {'from':owner1})
    check.equal(investorID, registrar.getID(scratch1))
    check.equal(investorID, issuer.getID(scratch1))

def set_document_hash():
    issuer = owner1.deploy(IssuingEntity, [owner1], 1)
    issuer.setDocumentHash("let there be a document", ahash, {'from':owner1})
    check.equal(issuer.getDocumentHash("let there be a document", {'from':owner1}), ahash)

def set_document_hash_cannot_change():
    issuer = owner1.deploy(IssuingEntity, [owner1], 1)
    issuer.setDocumentHash("let there be a document", ahash, {'from':owner1})
    check.reverts(issuer.setDocumentHash, ["let there be a document", ahash, {'from':owner1}])
    check.equal(issuer.getDocumentHash("let there be a document", {'from':owner1}), ahash)

def set_document_hash_multisig():
    issuer = owner1.deploy(IssuingEntity, [owner1, owner2], 2)
    check.false(issuer.setDocumentHash("let there be a document", ahash, {'from':owner1}).return_value)
    check.true(issuer.setDocumentHash("let there be a document", ahash, {'from':owner2}).return_value)
    check.equal(issuer.getDocumentHash("let there be a document", {'from':owner1}), ahash)

def multisig_same_owner_reverts():
    issuer = owner1.deploy(IssuingEntity, [owner1, owner2], 2)
    check.false(issuer.setDocumentHash("let there be a document", ahash, {'from':owner1}).return_value)
    check.reverts(issuer.setDocumentHash, ["let there be a document", ahash, {'from':owner1}])

def multisig_non_owner_reverts():
    issuer = owner1.deploy(IssuingEntity, [owner1, owner2], 2)
    check.false(issuer.setDocumentHash("let there be a document", ahash, {'from':owner1}).return_value)
    check.reverts(issuer.setDocumentHash, ["let there be a document", ahash, {'from':owner1}])
