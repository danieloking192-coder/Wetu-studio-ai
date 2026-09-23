"""Final WETU release-readiness contract: verify the integrated product spine exists together."""
from pathlib import Path

from wetu_studio.economic_core import EconomicLedger
from wetu_studio.postproduction import PostProductionEngine
from wetu_studio.product_studio import ProductStudio
from wetu_studio.runtime_control import RuntimeJobStore
from wetu_studio.storekit_entitlements import StoreKitEntitlementService


def test_release_readiness_product_spine():
    root = Path(__file__).resolve().parents[1]
    required = [
        root / "prototype" / "creator" / "index.html",
        root / "media-transcoding" / "TRANSCODING_CONTRACT.md",
        root / "docs" / "ECONOMIC_CORE.md",
        root / "docs" / "STOREKIT_ENTITLEMENTS.md",
        root / "docs" / "RUNTIME_PRODUCTION_BOUNDARY.md",
    ]
    assert all(path.exists() for path in required)

    studios = ProductStudio()
    assert {x.studio_id for x in studios.templates()} >= {"advertising", "film", "series"}

    economy = EconomicLedger(promotional_units=30, purchased_units=0)
    store = StoreKitEntitlementService(economy)
    assert len(store.catalog()) >= 3

    post = PostProductionEngine()
    assert post is not None
    jobs = RuntimeJobStore(root / ".wetu" / "release-readiness-runtime.json")
    assert jobs.max_jobs > 0
