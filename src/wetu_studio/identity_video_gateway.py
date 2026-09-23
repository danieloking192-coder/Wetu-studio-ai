"""Real photo-to-video gateway using fal.ai private upload + server-side inference."""
from __future__ import annotations
import json, os
from pathlib import Path
from typing import Any

from .character_identity import CharacterIdentity
from .media_acceptance import MediaAcceptancePipeline, ProviderUrlPolicy


class FalIdentityVideoGateway:
    def __init__(self, *, model: str, api_key: str, client: Any | None = None,
                 timeout: float = 300.0, argument_template: dict[str, Any] | None = None,
                 acceptance: MediaAcceptancePipeline | None = None, accept_output: bool = False):
        if not model.strip():
            raise ValueError("FAL_VIDEO_MODEL is required")
        if not api_key.strip():
            raise ValueError("FAL_KEY is required")
        self.model, self.api_key, self.timeout = model.strip(), api_key.strip(), timeout
        self.argument_template = argument_template or {}
        self.acceptance = acceptance
        self.accept_output = accept_output
        self.client = client or self._load_client(self.api_key)

    @staticmethod
    def _load_client(api_key: str) -> Any:
        try:
            import fal_client
        except ImportError as exc:
            raise RuntimeError("fal-client is not installed; install the WETU fal optional dependency") from exc
        os.environ.setdefault("FAL_KEY", api_key)
        return fal_client

    @classmethod
    def from_environment(cls) -> "FalIdentityVideoGateway | None":
        key, model = os.getenv("FAL_KEY", "").strip(), os.getenv("FAL_VIDEO_MODEL", "").strip()
        if not key or not model:
            return None
        raw = os.getenv("FAL_VIDEO_ARGUMENTS_JSON", "").strip()
        template = {}
        if raw:
            parsed = json.loads(raw)
            if not isinstance(parsed, dict):
                raise ValueError("FAL_VIDEO_ARGUMENTS_JSON must be a JSON object")
            template = parsed
        allowed = {x.strip() for x in os.getenv("WETU_PROVIDER_ALLOWED_HOSTS", "").split(",") if x.strip()}
        acceptance = MediaAcceptancePipeline(url_policy=ProviderUrlPolicy(allowed))
        accept_output = os.getenv("WETU_ACCEPT_PROVIDER_MEDIA", "1").lower() in {"1", "true", "yes"}
        return cls(model=model, api_key=key, timeout=float(os.getenv("FAL_VIDEO_TIMEOUT", "300")),
                   argument_template=template, acceptance=acceptance, accept_output=accept_output)

    @staticmethod
    def _replace(value: Any, values: dict[str, str]) -> Any:
        if isinstance(value, str):
            return value.format_map(values)
        if isinstance(value, list):
            return [FalIdentityVideoGateway._replace(x, values) for x in value]
        if isinstance(value, dict):
            return {k: FalIdentityVideoGateway._replace(v, values) for k, v in value.items()}
        return value

    def _arguments(self, *, image_url: str, prompt: str, duration: int, resolution: str,
                   options: dict[str, Any]) -> dict[str, Any]:
        values = {"image_url": image_url, "prompt": prompt,
                  "duration": str(duration), "resolution": resolution}
        args = self._replace(self.argument_template, values) if self.argument_template else {
            "image_url": image_url, "prompt": prompt, "duration": duration, "resolution": resolution}
        for key, value in options.items():
            if key not in {"image_url", "prompt", "references"}:
                args[key] = value
        args["image_url"], args["prompt"] = image_url, prompt
        return args

    @staticmethod
    def _extract_url(value: Any) -> str | None:
        if isinstance(value, str) and value.startswith(("https://", "http://")):
            return value
        if isinstance(value, dict):
            for key in ("video", "video_url", "url", "uri"):
                found = FalIdentityVideoGateway._extract_url(value.get(key))
                if found:
                    return found
            for item in value.values():
                found = FalIdentityVideoGateway._extract_url(item)
                if found:
                    return found
        if isinstance(value, list):
            for item in value:
                found = FalIdentityVideoGateway._extract_url(item)
                if found:
                    return found
        return None

    def generate(self, identity: CharacterIdentity, *, prompt: str, duration: int = 5,
                 resolution: str = "720p", options: dict[str, Any] | None = None) -> dict[str, Any]:
        if not identity.consent_confirmed:
            raise PermissionError("consent_confirmed is required for real-person video generation")
        if not Path(identity.path).exists():
            raise FileNotFoundError("identity image is not available")
        if not prompt or len(prompt) > 5000:
            raise ValueError("prompt is required and must be <= 5000 characters")
        if duration not in range(2, 11):
            raise ValueError("duration must be between 2 and 10 seconds")
        if resolution not in {"480p", "720p", "1080p"}:
            raise ValueError("unsupported resolution")
        upload, subscribe = getattr(self.client, "upload_file", None), getattr(self.client, "subscribe", None)
        if upload is None or subscribe is None:
            raise RuntimeError("fal client does not expose upload_file/subscribe")
        image_url = upload(identity.path, lifecycle="1h")
        arguments = self._arguments(image_url=image_url, prompt=prompt, duration=duration,
                                    resolution=resolution, options=options or {})
        result = subscribe(self.model, arguments=arguments)
        output_url = self._extract_url(result)
        if not output_url:
            raise ValueError("fal response did not contain a video URL")
        accepted_path = None
        acceptance_report = None
        if self.accept_output:
            if self.acceptance is None:
                raise RuntimeError("provider media acceptance pipeline is not configured")
            accepted_path, acceptance_report = self.acceptance.accept(output_url)
        return {"ok": True, "provider": "fal", "model": self.model, "uri": output_url,
                "real_media": True, "identity_character_id": identity.character_id,
                "identity_sha256": identity.sha256, "uploaded_source_url": image_url,
                "duration_seconds": duration, "resolution": resolution,
                "source_image_exposure": "fal_temporary_storage_only",
                "accepted_local_path": str(accepted_path) if accepted_path else None,
                "acceptance": acceptance_report.__dict__ if acceptance_report else None,
                "provider_result": result}
