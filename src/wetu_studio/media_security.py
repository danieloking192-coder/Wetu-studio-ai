"""Defense-in-depth media security and malware scanning for WETU uploads."""
from __future__ import annotations
import hashlib, os, shutil, subprocess
from dataclasses import dataclass
from pathlib import Path

@dataclass(frozen=True)
class ScanResult:
    clean: bool
    engine: str
    sha256: str
    size_bytes: int
    reason: str = ""

class MediaSecurityScanner:
    MAGIC = {"image/jpeg": (b"\xff\xd8\xff",), "image/png": (b"\x89PNG\r\n\x1a\n",), "image/webp": (b"RIFF",)}
    def __init__(self, max_bytes=10*1024*1024, require_antivirus=None):
        self.max_bytes=max_bytes
        self.require_antivirus=(os.getenv("WETU_REQUIRE_ANTIVIRUS","0").lower() in {"1","true","yes"} if require_antivirus is None else require_antivirus)
    def scan(self,path,mime_type=None):
        p=Path(path)
        if not p.is_file(): raise FileNotFoundError("media file not found")
        size=p.stat().st_size
        if size<=0 or size>self.max_bytes: raise ValueError("media size outside security limit")
        raw=p.read_bytes(); digest=hashlib.sha256(raw).hexdigest()
        if mime_type in self.MAGIC and not any(raw.startswith(sig) for sig in self.MAGIC[mime_type]): raise ValueError("media signature does not match declared type")
        if (not self.require_antivirus) and os.getenv("WETU_DISABLE_ANTIVIRUS","0").lower() in {"1","true","yes"}:\n            return ScanResult(True,"signature-only",digest,size,"antivirus_disabled_for_test")\n        engine=shutil.which("clamscan") or shutil.which("clamdscan")
        if not engine:
            if self.require_antivirus: raise RuntimeError("antivirus scanner unavailable; upload blocked")
            return ScanResult(True,"signature-only",digest,size,"antivirus_unavailable")
        try: proc=subprocess.run([engine,"--no-summary",str(p)],capture_output=True,text=True,timeout=30)
        except subprocess.TimeoutExpired as exc: raise RuntimeError("antivirus scan timeout; upload blocked") from exc
        if proc.returncode==0: return ScanResult(True,Path(engine).name,digest,size,"clean")
        if proc.returncode==1: return ScanResult(False,Path(engine).name,digest,size,(proc.stdout+proc.stderr).strip()[:500] or "malware detected")
        raise RuntimeError("antivirus scanner error; upload blocked")
