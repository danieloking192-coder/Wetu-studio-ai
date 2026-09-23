"""Optional fal.ai adapter behind WETU's provider contract."""
from __future__ import annotations
import os
from .media_engine import HttpMediaProvider

class FalMediaProvider(HttpMediaProvider):
    def __init__(self, name="fal", endpoint=None, api_key=None, model=None, timeout=120.0):
        self.model = model or os.getenv("FAL_MODEL", "")
        resolved_endpoint = endpoint or os.getenv("FAL_ENDPOINT", "")
        resolved_key = api_key if api_key is not None else os.getenv("FAL_KEY", "")
        if not resolved_endpoint:
            raise ValueError("FAL_ENDPOINT is required; choose the fal model endpoint explicitly")
        super().__init__(name, resolved_endpoint, resolved_key, timeout)
        self.capabilities = {"image", "video", "audio"}

    def generate(self, request, context):
        request.options = dict(request.options)
        if self.model and "model" not in request.options:
            request.options["model"] = self.model
        result = super().generate(request, context)
        result["provider"] = "fal"
        return result

def fal_from_environment():
    if not os.getenv("FAL_ENDPOINT", "").strip():
        return None
    return FalMediaProvider()
