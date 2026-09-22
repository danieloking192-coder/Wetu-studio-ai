"""Provider-neutral asset/reference memory for WETU productions."""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any

@dataclass
class AssetRecord:
    asset_id: str
    project_id: str
    scene_id: str | None
    kind: str
    provider: str
    uri: str
    real_media: bool
    metadata: dict[str, Any] = field(default_factory=dict)

class AssetStore:
    def __init__(self):
        self.assets: dict[str, AssetRecord] = {}
    def remember(self, asset):
        record=AssetRecord(asset.asset_id,asset.project_id,asset.scene_id,asset.kind,
                           asset.provider,asset.uri,bool(asset.metadata.get("real_media",False)),
                           dict(asset.metadata))
        self.assets[record.asset_id]=record
        return record
    def get(self, asset_id):
        return self.assets.get(asset_id)
    def references_for_scene(self, scene_id):
        return [a.uri for a in self.assets.values() if a.scene_id == scene_id]
