from wetu_studio.mature_policy import *

def test_unverified_is_blocked():
    d=MaturePolicy().evaluate(MatureRequest(MatureAccess.UNVERIFIED,True,True))
    assert not d.allowed

def test_verified_adult_non_explicit_can_pass():
    d=MaturePolicy().evaluate(MatureRequest(MatureAccess.VERIFIED_18_PLUS,True,True))
    assert d.allowed

def test_ambiguous_age_fails_closed():
    d=MaturePolicy().evaluate(MatureRequest(MatureAccess.VERIFIED_18_PLUS,True,True,ambiguous_age=True))
    assert not d.allowed

def test_explicit_scope_is_blocked():
    d=MaturePolicy().evaluate(MatureRequest(MatureAccess.VERIFIED_18_PLUS,True,True,explicit=True))
    assert not d.allowed

def test_consent_required():
    d=MaturePolicy().evaluate(MatureRequest(MatureAccess.VERIFIED_18_PLUS,True,False))
    assert not d.allowed
