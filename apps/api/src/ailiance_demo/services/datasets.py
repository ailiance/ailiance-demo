"""Read dataset manifests laid out as <root>/<domain>/MANIFEST.json."""
from __future__ import annotations

import json
from pathlib import Path

from ailiance_demo.models.dataset import DatasetDetail, DatasetSample, DatasetSummary


class DatasetsService:
    def __init__(self, roots: list[Path]) -> None:
        self.roots = roots

    def list(self) -> list[DatasetSummary]:
        out: list[DatasetSummary] = []
        for root in self.roots:
            if not root.exists():
                continue
            for manifest_path in sorted(root.glob("*/MANIFEST.json")):
                summary = self._read_summary(manifest_path)
                if summary is not None:
                    out.append(summary)
        return out

    def get(self, domain: str, max_samples: int = 3) -> DatasetDetail | None:
        for root in self.roots:
            manifest_path = root / domain / "MANIFEST.json"
            if not manifest_path.exists():
                continue
            summary = self._read_summary(manifest_path)
            if summary is None:
                continue
            samples = self._read_samples(manifest_path.parent / "train.jsonl", max_samples)
            return DatasetDetail(**summary.model_dump(exclude={"size_mb"}), samples=samples)
        return None

    def _read_summary(self, manifest_path: Path) -> DatasetSummary | None:
        try:
            data = json.loads(manifest_path.read_text())
        except (OSError, json.JSONDecodeError):
            return None
        domain = manifest_path.parent.name
        train_path = manifest_path.parent / "train.jsonl"
        size_bytes = train_path.stat().st_size if train_path.exists() else 0
        return DatasetSummary(
            domain=domain,
            name=data.get("hf_dataset_id", domain).split("/")[-1],
            n_rows=int(data.get("n_used") or data.get("n_source_rows") or 0),
            license=str(data.get("license", "unknown")),
            hf_dataset_id=str(data.get("hf_dataset_id", "")),
            download_date=str(data.get("download_date", "")),
            size_bytes=size_bytes,
            notes=data.get("notes"),
        )

    def _read_samples(self, jsonl_path: Path, limit: int) -> list[DatasetSample]:
        if not jsonl_path.exists() or limit <= 0:
            return []
        out: list[DatasetSample] = []
        with jsonl_path.open() as f:
            for line in f:
                if len(out) >= limit:
                    break
                line = line.strip()
                if not line:
                    continue
                try:
                    row = json.loads(line)
                except json.JSONDecodeError:
                    continue
                msgs = row.get("messages", [])
                user = next((m["content"] for m in msgs if m.get("role") == "user"), "")
                assistant = next((m["content"] for m in msgs if m.get("role") == "assistant"), "")
                if user and assistant:
                    out.append(DatasetSample(user=user, assistant=assistant))
        return out
