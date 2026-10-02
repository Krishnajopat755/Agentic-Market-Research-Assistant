"""Lineage tracking and MLflow-compatible metadata logger."""

import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


class LineageTracker:
    """Tracks code version, configuration hash, model artifacts, and evaluation parameters."""

    def __init__(self, tracking_dir: str | Path = "storage/mlflow_runs"):
        self.tracking_dir = Path(tracking_dir)
        self.tracking_dir.mkdir(parents=True, exist_ok=True)

    def log_run_lineage(
        self,
        run_id: str,
        parameters: dict[str, Any],
        metrics: dict[str, float],
        tags: dict[str, str],
        model_version: str | None = None,
    ) -> Path:
        """Persist structured run lineage artifact."""
        run_folder = self.tracking_dir / run_id
        run_folder.mkdir(parents=True, exist_ok=True)

        meta = {
            "run_id": run_id,
            "timestamp": datetime.now(UTC).isoformat(),
            "model_version": model_version or "default",
            "parameters": parameters,
            "metrics": metrics,
            "tags": tags,
        }

        meta_path = run_folder / "lineage_meta.json"
        meta_path.write_text(json.dumps(meta, indent=2), encoding="utf-8")
        return meta_path
