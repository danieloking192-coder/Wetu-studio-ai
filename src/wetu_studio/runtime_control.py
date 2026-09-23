"""Persistent runtime job state, provider health and bounded observability for WETU."""
from __future__ import annotations
import json, os, tempfile, threading
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()

@dataclass
class RuntimeJob:
    job_id: str
    request_id: str
    kind: str
    status: str = "queued"
    provider: str = ""
    attempts: list[dict[str, Any]] = field(default_factory=list)
    asset: dict[str, Any] | None = None
    error: str | None = None
    created_at: str = field(default_factory=utc_now)
    updated_at: str = field(default_factory=utc_now)

class RuntimeJobStore:
    def __init__(self, path: str | Path | None = None, max_jobs: int = 5000):
        self.path = Path(path or os.getenv("WETU_JOB_STORE", ".wetu/jobs.json"))
        self.max_jobs = max(100, min(int(max_jobs), 100000))
        self._lock = threading.RLock()
        self.jobs: dict[str, RuntimeJob] = {}
        self._load()

    def _load(self):
        try:
            raw=json.loads(self.path.read_text(encoding="utf-8"))
            if isinstance(raw, dict):
                for key, value in raw.items():
                    if isinstance(value, dict):
                        self.jobs[key]=RuntimeJob(**value)
        except (OSError, ValueError, TypeError, json.JSONDecodeError):
            self.jobs={}

    def _save(self):
        self.path.parent.mkdir(parents=True, exist_ok=True)
        data={k: asdict(v) for k,v in list(self.jobs.items())[-self.max_jobs:]}
        fd,tmp=tempfile.mkstemp(prefix="wetu-jobs-",suffix=".json",dir=str(self.path.parent))
        try:
            with os.fdopen(fd,"w",encoding="utf-8") as f:
                json.dump(data,f,ensure_ascii=False,indent=2)
            os.replace(tmp,self.path)
            try: os.chmod(self.path,0o600)
            except OSError: pass
        finally:
            if os.path.exists(tmp): os.unlink(tmp)

    def put(self, job: RuntimeJob):
        with self._lock:
            job.updated_at=utc_now()
            self.jobs[job.job_id]=job
            self.jobs=dict(list(self.jobs.items())[-self.max_jobs:])
            self._save()

    def get(self, job_id: str) -> RuntimeJob | None:
        with self._lock:
            return self.jobs.get(job_id)

    def snapshot(self) -> dict[str, Any]:
        with self._lock:
            counts={}
            for job in self.jobs.values(): counts[job.status]=counts.get(job.status,0)+1
            return {"jobs_total":len(self.jobs),"by_status":counts,"store":str(self.path)}

class ProviderHealth:
    def __init__(self):
        self._lock=threading.RLock()
        self._data: dict[str,dict[str,Any]]={}

    def record(self, provider: str, ok: bool, error: str | None = None):
        with self._lock:
            item=self._data.setdefault(provider,{"attempts":0,"successes":0,"failures":0,"last_error":None,"last_at":None})
            item["attempts"]+=1
            item["last_at"]=utc_now()
            if ok: item["successes"]+=1
            else:
                item["failures"]+=1
                item["last_error"]=(error or "provider failure")[:500]

    def snapshot(self):
        with self._lock:
            out={}
            for name,item in self._data.items():
                attempts=item["attempts"]
                out[name]={**item,"success_rate":round(item["successes"]/attempts,4) if attempts else 0.0}
            return out

class RuntimeMetrics:
    def __init__(self):
        self._lock=threading.RLock()
        self.counters={}
    def inc(self,key:str,value:int=1):
        with self._lock: self.counters[key]=self.counters.get(key,0)+value
    def snapshot(self):
        with self._lock: return dict(self.counters)
