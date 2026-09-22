from wetu_studio.character_engine import CharacterEngine
from wetu_studio.identity import IdentityProfile, IdentityType


def test_fictional_character_has_persistent_visual_identity():
    character = CharacterEngine().create("c1", "Amani")
    CharacterEngine().set_visual_identity(
        character, face="distinctive", skin="deep brown", hair="short",
        eyes="brown", body="athletic", age="30", signature_features="small scar"
    )
    assert character.is_identifiable()
    assert character.validate_likeness()


def test_real_likeness_requires_verified_consent():
    identity = IdentityProfile("id1", IdentityType.AUTHORIZED_REAL_PERSON, "consent-1", verified=False)
    character = CharacterEngine().create("c1", "Real Person", identity=identity)
    assert not character.validate_likeness()


def test_verified_real_likeness_is_allowed():
    identity = IdentityProfile("id1", IdentityType.AUTHORIZED_REAL_PERSON, "consent-1", verified=True)
    character = CharacterEngine().create("c1", "Real Person", identity=identity)
    assert character.validate_likeness()
