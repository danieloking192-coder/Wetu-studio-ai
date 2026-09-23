"""Provider selection, fallback and job-state orchestration for WETU media generation."""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any
from .media_engine import MediaAsset, MediaRequest, MediaRegistry, utc_now
from .runtime_control import RuntimeJob, RuntimeJobStore, ProviderHealth, RuntimeMetrics

@dataclass
class MediaJob:
    job_id: str
    request_id: str
    status: str = "queued"
    provider: str = ""
    attempts: list[dict[str, Any]] = field(default_factory=list)
    asset: MediaAsset | None = None
    error: str | None = None
    created_at: str = field(default_factory=utc_now)
    updated_at: str = field(default_factory=utc_now)

class MediaOrchestrator:
    """Deterministic provider selection with explicit fallback and bounded attempts."""
    def __init__(self, registry: MediaRegistry, max_attempts: int = 3, job_store: RuntimeJobStore | None = None):
        self.registry = registry
        self.max_attempts = max(1, min(max_attempts, 8))
        self.jobs: dict[str, MediaJob] = {}
        self.job_store = job_store or RuntimeJobStore()
        self.provider_health = ProviderHealth()
        self.metrics = RuntimeMetrics()

    def candidate_providers(self, request: MediaRequest) -> list[str]:
        if request.provider and request.provider != "auto":
            candidates = [request.provider]
            configured = [name for name, p in self.registry.providers.items()
                          if request.kind in getattr(p, "capabilities", set()) and name != request.provider]
            return candidates + configured
        return [name for name, p in self.registry.providers.items()
                if request.kind in getattr(p, "capabilities", set())]

    def generate(self, request: MediaRequest, context: dict[str, Any], job_id: str | None = None) -> MediaJob:
        job_id = job_id or request.request_id
        job = MediaJob(job_id=job_id, request_id=request.request_id)
        self.jobs[job_id] = job
        self.job_store.put(RuntimeJob(job_id, request.request_id, request.kind, status=job.status))
        self.metrics.inc("media.queued")
        candidates = self.candidate_providers(request)
        if not candidates:
            job.status, job.error = "failed", f"no provider supports {request.kind}"
            job.updated_at = utc_now()
            self.metrics.inc("media.failed")
            self.job_store.put(RuntimeJob(job_id, request.request_id, request.kind, status=job.status, error=job.error))
            return job
        job.status = "generating"
        for provider_name in candidates[:self.max_attempts]:
            job.provider = provider_name
            attempt = {"provider": provider_name, "started_at": utc_now(), "status": "started"}
            try:
                effective = MediaRequest(request.request_id, request.project_id, request.scene_id,
                                         request.kind, request.prompt, provider_name,
                                         list(request.references), dict(request.options))
                asset = self.registry.generate(effective, context)
                attempt.update({"status": "completed", "finished_at": utc_now()})
                job.attempts.append(attempt)
                job.asset = asset
                job.status = "completed"
                job.updated_at = utc_now()
                self.provider_health.record(provider_name, True)
                self.metrics.inc("media.completed")
                self.job_store.put(RuntimeJob(job_id, request.request_id, request.kind, status=job.status, provider=provider_name, attempts=job.attempts, asset=vars(asset)))
                return job
            except Exception as exc:
                attempt.update({"status": "failed", "finished_at": utc_now(), "error": str(exc)[:2000]})
                job.attempts.append(attempt)
                self.provider_health.record(provider_name, False, str(exc))
                self.metrics.inc("media.attempt_failed")
        job.status = "failed"
        job.error = job.attempts[-1].get("error", "media generation failed")
        job.updated_at = utc_now()
        self.metrics.inc("media.failed")
        self.job_store.put(RuntimeJob(job_id, request.request_id, request.kind, status=job.status, provider=job.provider, attempts=job.attempts, error=job.error))
        return job

    def get(self, job_id: str) -> MediaJob | None:
        return self.jobs.get(job_id)
