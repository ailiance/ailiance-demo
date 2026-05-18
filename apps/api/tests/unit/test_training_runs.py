"""Tests for training_runs discovery."""
from datetime import datetime, UTC
from pathlib import Path

from ailiance_demo.models import TrainingRunStatus
from ailiance_demo.services.training_runs import discover_runs, summarize_run

# Inlined fixture: a real sample.log would be a *.log file, which the repo
# .gitignore excludes — so the sample lives here as a constant instead.
# Format mirrors mlx_lm training output parsed by services/log_tail.py.
SAMPLE_LOG = """\
Starting training run...
Iter 100: Train loss 0.812, Learning Rate 1.000e-05
Iter 200: Train loss 0.654, Learning Rate 1.000e-05
Iter 200: Val loss 0.701, Val took 12.300s
Iter 300: Train loss 0.531, Learning Rate 1.000e-05
Iter 400: Val loss 0.532, Val took 11.800s
Iter 400: Train loss 0.479, Learning Rate 1.000e-05
"""


def test_discover_runs_finds_log_files(tmp_path: Path) -> None:
    (tmp_path / "logs").mkdir()
    sample = SAMPLE_LOG
    (tmp_path / "logs" / "mistral-large-opus.log").write_text(sample)
    (tmp_path / "logs" / "qwen-35b.log").write_text(sample)

    runs = discover_runs(roots=[tmp_path / "logs"], machine_label="studio")

    assert len(runs) == 2
    ids = {r.id for r in runs}
    assert "mistral-large-opus" in ids
    assert "qwen-35b" in ids
    assert all(r.machine == "studio" for r in runs)


def test_summarize_run_extracts_last_metrics(tmp_path: Path) -> None:
    sample = SAMPLE_LOG
    log_path = tmp_path / "test.log"
    log_path.write_text(sample)

    run = summarize_run(log_path, machine_label="studio", active_threshold_seconds=60)

    assert run.id == "test"
    assert run.last_iter == 400
    assert run.last_train_loss == 0.479
    assert run.last_val_loss == 0.532
    # File was just written so it's "active" within threshold
    assert run.status == TrainingRunStatus.ACTIVE


def test_summarize_run_marks_old_files_completed(tmp_path: Path) -> None:
    import os
    import time
    sample = SAMPLE_LOG
    log_path = tmp_path / "old.log"
    log_path.write_text(sample)
    # Set mtime to 10 minutes ago
    old_time = time.time() - 600
    os.utime(log_path, (old_time, old_time))

    run = summarize_run(log_path, machine_label="studio", active_threshold_seconds=300)
    assert run.status == TrainingRunStatus.COMPLETED
