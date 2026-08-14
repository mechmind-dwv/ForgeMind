"""
Schema/consistency checks for the benchmark result artifacts committed
to the repository.

These are regression tests: they guard against accidental corruption
or structural drift of the checked-in JSON results, and document the
expected shape of each benchmark's output.
"""

import json
import math
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent


def _load(relative_path):
    return json.loads((REPO_ROOT / relative_path).read_text())


# ---------------------------------------------------------------------------
# benchmarks/active_vs_passive/results.json
# ---------------------------------------------------------------------------


def test_active_vs_passive_results_has_expected_top_level_shape():
    data = _load("benchmarks/active_vs_passive/results.json")

    assert set(data.keys()) == {"version", "protocol", "rows", "summary"}
    assert isinstance(data["rows"], list)
    assert len(data["rows"]) == len(data["protocol"]["seeds"]) * 10


def test_active_vs_passive_rows_have_expected_fields():
    data = _load("benchmarks/active_vs_passive/results.json")

    expected_keys = {
        "seed",
        "target",
        "target_complexity",
        "active_survivors",
        "active_eliminations",
        "active_queries",
        "active_complexity",
        "passive_survivors",
        "passive_eliminations",
        "passive_queries",
        "passive_complexity",
        "active_program",
        "passive_program",
    }

    for row in data["rows"]:
        assert set(row.keys()) == expected_keys
        assert row["seed"] in data["protocol"]["seeds"]
        assert 0 <= row["target"] < 10
        assert row["active_eliminations"] >= 0
        assert row["passive_eliminations"] >= 0


def test_active_vs_passive_summary_is_internally_consistent():
    data = _load("benchmarks/active_vs_passive/results.json")

    rows = data["rows"]
    summary = data["summary"]

    active_elim = [r["active_eliminations"] for r in rows]
    passive_elim = [r["passive_eliminations"] for r in rows]

    assert summary["active_mean_eliminations"] == sum(active_elim) / len(rows)
    assert summary["passive_mean_eliminations"] == sum(passive_elim) / len(rows)
    assert summary["active_passive_efficiency_ratio"] > 0


# ---------------------------------------------------------------------------
# benchmarks/adversarial/results.json
# ---------------------------------------------------------------------------


def test_adversarial_results_has_expected_top_level_shape():
    data = _load("benchmarks/adversarial/results.json")

    assert data["version"] == "0.9.1-adversarial"
    assert data["cases"] == len(data["results"])


def test_adversarial_results_case_fields_are_well_formed():
    data = _load("benchmarks/adversarial/results.json")

    expected_keys = {
        "seed",
        "target",
        "random_accuracy",
        "adversarial_accuracy",
        "random_mismatches",
        "adversarial_mismatches",
        "first_counterexample",
        "discovery_tested",
        "discovery_found",
        "discovery_rate",
    }

    for case in data["results"]:
        assert set(case.keys()) == expected_keys
        assert 0.0 <= case["random_accuracy"] <= 1.0
        assert 0.0 <= case["adversarial_accuracy"] <= 1.0
        assert 0 <= case["discovery_found"] <= case["discovery_tested"]


def test_adversarial_results_summary_matches_recorded_cases():
    data = _load("benchmarks/adversarial/results.json")

    random_scores = [c["random_accuracy"] for c in data["results"]]
    adversarial_scores = [c["adversarial_accuracy"] for c in data["results"]]

    assert data["random_mean"] == sum(random_scores) / len(random_scores)
    assert data["adversarial_mean"] == sum(adversarial_scores) / len(
        adversarial_scores
    )
    assert math.isclose(
        data["equivalence_gap"],
        data["random_mean"] - data["adversarial_mean"],
        abs_tol=1e-9,
    )
    assert data["discovery_found"] == sum(
        c["discovery_found"] for c in data["results"]
    )
    assert data["discovery_tested"] == sum(
        c["discovery_tested"] for c in data["results"]
    )


# ---------------------------------------------------------------------------
# benchmarks/discovery/results.json
# ---------------------------------------------------------------------------


def test_discovery_results_is_a_non_empty_list_of_trials():
    data = _load("benchmarks/discovery/results.json")

    assert isinstance(data, list)
    assert len(data) > 0


def test_discovery_results_trials_have_expected_fields_and_bounds():
    data = _load("benchmarks/discovery/results.json")

    expected_keys = {
        "seed",
        "target",
        "budget",
        "initial_hypotheses",
        "active_survivors",
        "passive_survivors",
        "active_eliminations",
        "passive_eliminations",
        "active_isolated",
        "passive_isolated",
        "active_trace",
        "passive_trace",
    }

    # Checking every trial keeps this test proportional to a benchmark
    # rerun; sampling would silently miss corruption in most rows.
    for trial in data:
        assert set(trial.keys()) == expected_keys
        assert 0 <= trial["active_survivors"] <= trial["initial_hypotheses"]
        assert 0 <= trial["passive_survivors"] <= trial["initial_hypotheses"]
        assert trial["active_isolated"] == (trial["active_survivors"] == 1)
        assert trial["passive_isolated"] == (trial["passive_survivors"] == 1)


# ---------------------------------------------------------------------------
# backups/0.9.1-active-baseline/*.json
#
# These are frozen historical snapshots referenced by the README as the
# reproducible 0.9.1 baseline. They should remain valid, parseable JSON
# with the same shape as their live benchmarks/ counterparts.
# ---------------------------------------------------------------------------


def test_backup_active_vs_passive_results_round_trips_and_matches_live_shape():
    backup = _load("backups/0.9.1-active-baseline/results.json")
    live = _load("benchmarks/active_vs_passive/results.json")

    assert set(backup.keys()) == set(live.keys())
    assert backup["version"] == live["version"]
    assert len(backup["rows"]) == len(live["rows"])


def test_backup_adversarial_results_round_trips_and_matches_live_shape():
    backup = _load("backups/0.9.1-active-baseline/adversarial-results.json")
    live = _load("benchmarks/adversarial/results.json")

    assert set(backup.keys()) == set(live.keys())
    assert backup["cases"] == live["cases"]
    assert backup["discovery_rate"] == live["discovery_rate"]