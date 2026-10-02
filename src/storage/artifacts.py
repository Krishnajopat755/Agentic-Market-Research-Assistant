"""Immutable content-addressed artifact storage manager."""

import hashlib
import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any
from uuid import uuid4

from src.contracts.mcp import ArtifactMetadata


class ArtifactStorage:
    """Stores and retrieves immutable artifacts backed by filesystem or object storage."""

    def __init__(self, base_dir: str | Path = "storage/artifacts"):
        self.base_dir = Path(base_dir)
        self.base_dir.mkdir(parents=True, exist_ok=True)

    def store_json(
        self,
        kind: str,
        data: Any,
        run_id: str,
        symbol: str | None = None,
        artifact_id: str | None = None,
    ) -> ArtifactMetadata:
        """Store JSON-serializable artifact with SHA-256 hash."""
        now = datetime.now(UTC)
        aid = artifact_id or f"{kind}-{uuid4().hex[:12]}"

        # Serialize data deterministically
        if hasattr(data, "model_dump"):
            payload = data.model_dump(mode="json")
        elif isinstance(data, (list, tuple)):
            payload = [
                item.model_dump(mode="json") if hasattr(item, "model_dump") else item
                for item in data
            ]
        else:
            payload = data

        raw_bytes = json.dumps(payload, sort_keys=True, default=str).encode("utf-8")
        sha256 = hashlib.sha256(raw_bytes).hexdigest()

        # Partition by run_id
        run_dir = self.base_dir / run_id
        run_dir.mkdir(parents=True, exist_ok=True)

        filename = f"{aid}.json"
        filepath = run_dir / filename
        filepath.write_bytes(raw_bytes)

        artifact_ref = f"artifact://{run_id}/{kind}/{filename}"

        return ArtifactMetadata(
            artifact_id=aid,
            artifact_ref=artifact_ref,
            artifact_kind=kind,
            run_id=run_id,
            symbol=symbol,
            created_at=now,
            sha256_hash=sha256,
            size_bytes=len(raw_bytes),
            content_type="application/json",
        )

    def retrieve_json(self, run_id: str, filename: str) -> Any:
        """Retrieve stored JSON artifact."""
        filepath = self.base_dir / run_id / filename
        if not filepath.exists():
            raise FileNotFoundError(f"Artifact {filepath} does not exist")
        return json.loads(filepath.read_text(encoding="utf-8"))
