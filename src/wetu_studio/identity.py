from dataclasses import dataclass
from enum import Enum


class IdentityType(str, Enum):
    FICTIONAL = "FICTIONAL"
    AUTHORIZED_REAL_PERSON = "AUTHORIZED_REAL_PERSON"
    UNVERIFIED = "UNVERIFIED"
    RESTRICTED = "RESTRICTED"


@dataclass(frozen=True)
class IdentityProfile:
    identity_id: str
    identity_type: IdentityType
    consent_reference: str = ""
    likeness_reference: str = ""
    verified: bool = False

    def can_use_likeness(self) -> bool:
        if self.identity_type is IdentityType.FICTIONAL:
            return True
        return self.identity_type is IdentityType.AUTHORIZED_REAL_PERSON and self.verified and bool(self.consent_reference)
