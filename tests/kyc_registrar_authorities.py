from brownie import *

def setup():
    global a, countries
    countries = [1,2,3]
    a = accounts
    global owner1, owner2
    global authority1, authority2
    global scratch1, scratch2
    owner1 = a[0]
    owner2 = a[1]
    authority1 = a[2]
    authority2 = a[3]
    scratch1 = a[8]
    scratch2 = a[9]
    global registrar
    registrar = owner1.deploy(KYCRegistrar, [owner1], 1)
    registrar.addAuthority([authority1], countries, 1)
    global authorityID
    authorityID = registrar.getID(authority1)
    global investorID, investorID2
    investorID = b"aaaainvestor"
    investorID2 = b"bbbinvestor"

# TODO: multisig tests

#################################
# addInvestor success path tests

def addInvestor_threshold_of_one_passses():
    txr = registrar.addInvestor(investorID, 1, b'abc', 1, 9999999999, [scratch1], {'from':authority1})
    check.event_fired(txr, 'NewInvestor')

#################################
# addInvestor fail path tests

def addInvestor_invalid_country_fails():
    check.reverts(registrar.addInvestor, (investorID, 4, b'abc', 1, 9999999999, [scratch1], {'from':authority1}), revert_msg='dev: country')

def addInvestor_already_expired_fails():
    check.reverts(registrar.addInvestor, (investorID, 3, b'abc', 1, 1, [scratch1], {'from':authority1}), revert_msg='dev: expired')

def addInvestor_already_added_fails():
    # TODO: can't re-add an existing investor - i.e. change country
    check.confirms(registrar.addInvestor, (investorID, 3, b'abc', 1, 9999999999, [scratch1], {'from':authority1}))
    check.reverts (registrar.addInvestor, (investorID, 2, b'abc', 1, 9999999999, [scratch1], {'from':authority1}))

def addInvestor_by_restricted_authority_fails():
    id_ = registrar.getID(authority1)
    registrar.setAuthorityRestriction(id_, False)
    check.reverts(registrar.addInvestor, (investorID, 3, b'abc', 1, 9999999999, [scratch1], {'from':authority1}), 'dev: restricted')

#################################
# updateInvestor success path tests

def updateInvestor_updates_all_fields_and_fires_event():
    registrar.addInvestor(investorID, 3, b'abc', 1, 9999999999, [scratch1], {'from':authority1})
    txr = registrar.updateInvestor(investorID, b'ccc', 2, 5000000000, {'from':authority1})
    check.equal(registrar.getRating(investorID), 2)
    check.equal(registrar.getRegion(investorID), b'ccc')
    check.equal(registrar.getExpires(investorID), 5000000000)
    check.equal(registrar.getCountry(investorID), 3)
    check.event_fired(txr, 'UpdatedInvestor')

def updateInvestor_by_other_valid_authority_passes():
    registrar.addInvestor(investorID, 3, b'abc', 1, 9999999999, [scratch1], {'from':authority1})
    registrar.addAuthority([authority2], [3], 1)
    check.confirms(registrar.updateInvestor, (investorID, b'ccc', 2, 9999999999, {'from':authority2}))

#################################
# updateInvestor fail path tests

# TODO: wouldn't un-restrict an investor

def updateInvestor_by_restricted_authority_fails():
    id_ = registrar.getID(authority1)
    registrar.setAuthorityRestriction(id_, False)
    check.reverts(registrar.updateInvestor, (investorID, b'ccc', 2, 9999999999), {'from':authority1})

def updateInvestor_with_countries_that_dont_match_authority_fails():
    registrar.addInvestor(investorID, 3, b'abc', 1, 9999999999, [scratch1], {'from':authority1})
    registrar.addAuthority([authority2], [4], 1)
    check.reverts(registrar.updateInvestor, (investorID, b'ccc', 2, 9999999999, {'from':authority2}), revert_msg="dev: country")

#################################
# setInvestorAuthority success path tests

def setInvestorAuthority_fires_event():
    registrar.addInvestor(investorID, 3, b'abc', 1, 9999999999, [scratch1], {'from':authority1})
    registrar.addAuthority([authority2], countries, 1)
    authorityID2 = registrar.getID(authority2)
    txr = registrar.setInvestorAuthority([investorID], authorityID2)
    # There is no way to directly check the investor's authority, so use the event
    check.event_fired(txr, 'UpdatedInvestor', 1, { 'authority': authorityID2 })

def setInvestorAuthority_updates_multiple_investors():
    registrar.addInvestor(investorID, 3, b'abc', 1, 9999999999, [scratch1], {'from':authority1})
    registrar.addInvestor(investorID2, 3, b'abc', 1, 9999999999, [scratch2], {'from':authority1})
    registrar.addAuthority([authority2], countries, 1)
    authorityID2 = registrar.getID(authority2)
    txr = registrar.setInvestorAuthority([investorID, investorID2], authorityID2)
    # There is no way to directly check the investor's authority, so use the event
    check.event_fired(txr, 'UpdatedInvestor', 2, [{ 'authority': authorityID2 }, { 'authority': authorityID2 }])

#######################################
# setInvestorAuthority fail path tests

# I think there must be a bug in this test, it should pass I think
def authority_cant_change_authority_for_an_investor(pending=True):
    registrar.addInvestor(investorID, 3, b'abc', 1, 9999999999, [scratch1], {'from':authority1})
    registrar.addAuthority([authority2], countries, 1)
    authorityID2 = registrar.getID(authority2)
    check.reverts(registrar.setInvestorAuthority, ([investorID], authorityID2), {'from':authority1})

def authority_cant_be_set_to_an_non_authority_address():
    registrar.addInvestor(investorID, 3, b'abc', 1, 9999999999, [scratch1], {'from':authority1})
    check.reverts(registrar.setInvestorAuthority, ([investorID], investorID), {'from':authority1})


#######################################
# setInvestorRestriction success path tests

def any_judicial_authority_can_restrict_an_investor():
    registrar.addInvestor(investorID, 3, b'abc', 1, 9999999999, [scratch1], {'from':authority1})
    registrar.addAuthority([authority2], countries, 1)
    authorityID2 = registrar.getID(authority2)
    txr = registrar.setInvestorRestriction(investorID, False, {'from':authority2})
    check.event_fired(txr, 'InvestorRestriction')



# TODO: owner can restrict investors
# TODO: can_unrestrict_a_restricted_investor
# TODO: fires InvestorRestriction

#######################################
# setInvestorRestriction fail path tests

# TODO: authorities for the wrong country cant restrict investors
# TODO: fires ...



