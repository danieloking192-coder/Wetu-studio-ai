"""Secure provider-output ingestion and deterministic media acceptance gates."""
from __future__ import annotations
import ipaddress, json, socket, subprocess, tempfile, urllib.parse, urllib.request
from dataclasses import dataclass
from pathlib import Path
from typing import Any
from .media_security import MediaSecurityScanner
from .media_stability import MediaStabilityEngine

class UnsafeProviderUrl(ValueError): pass

@dataclass(frozen=True)
class MediaAcceptanceReport:
    accepted: bool
    sha256: str
    size_bytes: int
    mime_type: str
    ffprobe: dict[str, Any]
    stability_issues: tuple[str, ...]
    security_engine: str
    reason: str = ""

class ProviderUrlPolicy:
    def __init__(self, allowed_hosts: set[str] | None = None):
        self.allowed_hosts={h.strip().lower().rstrip(".") for h in (allowed_hosts or set()) if h.strip()}
    @staticmethod
    def _public_ips(host: str):
        try: infos=socket.getaddrinfo(host,None,type=socket.SOCK_STREAM)
        except OSError as exc: raise UnsafeProviderUrl("provider host cannot be resolved") from exc
        addresses=[]
        for info in infos:
            try: addr=ipaddress.ip_address(info[4][0])
            except ValueError as exc: raise UnsafeProviderUrl("provider returned an invalid IP") from exc
            if not addr.is_global: raise UnsafeProviderUrl("provider URL resolves to a non-public address")
            addresses.append(addr)
        if not addresses: raise UnsafeProviderUrl("provider host has no usable address")
        return addresses
    def validate(self,url:str):
        parsed=urllib.parse.urlparse(url)
        if parsed.scheme!="https" or not parsed.hostname or parsed.username or parsed.password:
            raise UnsafeProviderUrl("provider output must be an HTTPS URL without userinfo")
        host=parsed.hostname.lower().rstrip(".")
        if self.allowed_hosts and host not in self.allowed_hosts: raise UnsafeProviderUrl("provider host is not allowlisted")
        self._public_ips(host)
        return parsed

class MediaAcceptancePipeline:
    def __init__(self, *, url_policy=None, security=None, stability=None, max_bytes=100*1024*1024, timeout=60.0):
        self.url_policy=url_policy or ProviderUrlPolicy()
        self.security=security or MediaSecurityScanner(max_bytes=max_bytes)
        self.stability=stability or MediaStabilityEngine()
        self.max_bytes=max_bytes; self.timeout=timeout
    def _download(self,url,destination):
        self.url_policy.validate(url)
        req=urllib.request.Request(url,headers={"User-Agent":"WETU-MediaGateway/1.0"})
        total=0
        with urllib.request.urlopen(req,timeout=self.timeout) as response, destination.open("wb") as out:
            length=response.headers.get("Content-Length")
            if length and int(length)>self.max_bytes: raise ValueError("provider media exceeds size limit")
            while True:
                chunk=response.read(min(1024*1024,self.max_bytes+1-total))
                if not chunk: break
                total+=len(chunk)
                if total>self.max_bytes: raise ValueError("provider media exceeds size limit")
                out.write(chunk)
        if total<=0: raise ValueError("provider returned an empty media file")
        return total
    @staticmethod
    def _ffprobe(path):
        cmd=["ffprobe","-v","error","-show_format","-show_streams","-of","json",str(path)]
        try: result=subprocess.run(cmd,capture_output=True,text=True,timeout=45)
        except FileNotFoundError as exc: raise RuntimeError("ffprobe is required for provider media acceptance") from exc
        except subprocess.TimeoutExpired as exc: raise RuntimeError("ffprobe timed out") from exc
        if result.returncode!=0: raise ValueError("provider media failed ffprobe")
        try: payload=json.loads(result.stdout or "{}")
        except json.JSONDecodeError as exc: raise ValueError("ffprobe returned invalid JSON") from exc
        if not isinstance(payload,dict): raise ValueError("ffprobe returned invalid metadata")
        return payload
    @staticmethod
    def _decode_check(path):
        cmd=["ffmpeg","-v","error","-err_detect","explode","-i",str(path),"-map","0:v:0","-f","null","-"]
        try: result=subprocess.run(cmd,capture_output=True,text=True,timeout=120)
        except FileNotFoundError as exc: raise RuntimeError("ffmpeg is required for provider media acceptance") from exc
        except subprocess.TimeoutExpired as exc: raise RuntimeError("full video decode timed out") from exc
        if result.returncode!=0: raise ValueError("provider video failed full decode")
    def accept(self,url,*,target=None):
        with tempfile.NamedTemporaryFile(prefix="wetu-provider-",suffix=".mp4",delete=False) as handle: path=Path(handle.name)
        try:
            size=self._download(url,path)
            scan=self.security.scan(path)
            if not scan.clean: raise ValueError("provider media failed malware scan")
            metadata=self._ffprobe(path)
            streams=metadata.get("streams",[])
            video=next((s for s in streams if s.get("codec_type")=="video"),None)
            if not video: raise ValueError("provider output contains no video stream")
            duration=float(metadata.get("format",{}).get("duration",video.get("duration",0)) or 0)
            width,height=int(video.get("width",0)),int(video.get("height",0))
            fps_text=video.get("avg_frame_rate") or video.get("r_frame_rate") or "0/1"
            num,den=(fps_text.split("/",1)+["1"])[:2]; fps=float(num)/float(den or 1)
            stability=self.stability.validate({"width":width,"height":height,"duration_seconds":duration,"fps":fps,"decode_ok":True},target)
            if not stability.passed: raise ValueError("provider media failed stability gate: "+",".join(stability.issues))
            self._decode_check(path)
            return path,MediaAcceptanceReport(True,scan.sha256,size,"video/mp4",metadata,stability.issues,scan.engine,"accepted")
        except Exception:
            try: path.unlink(missing_ok=True)
            except OSError: pass
            raise
