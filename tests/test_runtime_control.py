from pathlib import Path
from wetu_studio.runtime_control import RuntimeJob, RuntimeJobStore, ProviderHealth, RuntimeMetrics

def test_job_store_persists(tmp_path: Path):
    path=tmp_path/"jobs.json"
    store=RuntimeJobStore(path)
    store.put(RuntimeJob("j1","r1","image",status="completed"))
    restored=RuntimeJobStore(path)
    assert restored.get("j1").status=="completed"

def test_provider_health_and_metrics():
    health=ProviderHealth()
    health.record("demo",True)
    health.record("demo",False,"timeout")
    assert health.snapshot()["demo"]["success_rate"]==0.5
    metrics=RuntimeMetrics()
    metrics.inc("media.completed")
    metrics.inc("media.completed",2)
    assert metrics.snapshot()["media.completed"]==3
