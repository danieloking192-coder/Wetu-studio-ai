from dataclasses import dataclass, field

@dataclass(frozen=True)
class QACheck:
    check_id: str
    passed: bool
    severity: str = "INFO"
    notes: str = ""

@dataclass
class QAReport:
    checks: list[QACheck] = field(default_factory=list)
    @property
    def passed(self) -> bool:
        return all(c.passed or c.severity != "BLOCKER" for c in self.checks)

class QAEngine:
    def add_check(self, report: QAReport, check_id: str, passed: bool, severity="INFO", notes="") -> QACheck:
        if severity not in {"INFO", "WARNING", "BLOCKER"}: raise ValueError("invalid severity")
        check=QACheck(check_id,passed,severity,notes); report.checks.append(check); return check
    def validate_identity(self, report: QAReport, expected_signature, actual_signature) -> QACheck:
        return self.add_check(report,"identity_continuity",expected_signature == actual_signature,"BLOCKER" if expected_signature != actual_signature else "INFO","visual identity mismatch" if expected_signature != actual_signature else "")
    def validate_timing(self, report: QAReport, start_ms: int, end_ms: int) -> QACheck:
        return self.add_check(report,"timing",start_ms >= 0 and end_ms >= start_ms,"BLOCKER" if not (start_ms >= 0 and end_ms >= start_ms) else "INFO")
