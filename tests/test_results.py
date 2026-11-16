import importlib.util
import json
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("check_results", ROOT / "scripts" / "check_results.py")
cr = importlib.util.module_from_spec(spec)
spec.loader.exec_module(cr)


def test_checker_catches_nan_and_bad_interval():
    res = {"claim1": {"diff": 0.5, "ci95": [0.0, 0.2]}, "x": float("nan")}
    errs = cr.check(res)
    assert any("NaN" in e for e in errs)
    assert any("does not contain" in e for e in errs)
    assert any("missing generated_utc" in e for e in errs)


@pytest.mark.skipif(not (ROOT / "app" / "data" / "results.json").exists(), reason="results.json not written yet")
def test_results_json_valid():
    res = json.loads((ROOT / "app" / "data" / "results.json").read_text())
    assert cr.check(res) == []
