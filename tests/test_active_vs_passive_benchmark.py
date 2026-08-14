import json

import benchmarks.active_vs_passive as active_vs_passive


def test_run_writes_results_json_with_expected_shape(tmp_path, monkeypatch):
    # Shrink the protocol constants so the full benchmark entrypoint
    # stays fast while still exercising the real code path.
    monkeypatch.setattr(active_vs_passive, "SEEDS", (3,))
    monkeypatch.setattr(active_vs_passive, "TARGETS", active_vs_passive.TARGETS[:2])
    monkeypatch.setattr(active_vs_passive, "ROUNDS", 5)
    monkeypatch.setattr(active_vs_passive, "POPULATION", 10)
    monkeypatch.setattr(active_vs_passive, "CANDIDATE_BUDGET", 5)

    monkeypatch.chdir(tmp_path)

    active_vs_passive.run()

    output = tmp_path / "benchmarks" / "active_vs_passive" / "results.json"
    assert output.exists()

    data = json.loads(output.read_text())

    assert data["version"] == "0.9.2"
    assert data["protocol"] == {
        "seeds": [3],
        "rounds": 5,
        "population": 10,
        "candidate_budget": 5,
    }

    # One row per (seed, target) combination.
    assert len(data["rows"]) == 1 * 2

    for row in data["rows"]:
        assert row["seed"] == 3
        assert row["target"] in (0, 1)
        assert 0 <= row["active_survivors"] <= 10
        assert 0 <= row["passive_survivors"] <= 10
        assert row["active_eliminations"] >= 0
        assert row["passive_eliminations"] >= 0

    summary = data["summary"]
    expected_summary_keys = {
        "active_mean_eliminations",
        "passive_mean_eliminations",
        "active_mean_survivors",
        "passive_mean_survivors",
        "active_elimination_per_query",
        "passive_elimination_per_query",
        "active_passive_efficiency_ratio",
    }

    assert set(summary.keys()) == expected_summary_keys
    assert summary["active_passive_efficiency_ratio"] >= 0.0


def test_run_creates_output_directory_when_missing(tmp_path, monkeypatch):
    monkeypatch.setattr(active_vs_passive, "SEEDS", (3,))
    monkeypatch.setattr(active_vs_passive, "TARGETS", active_vs_passive.TARGETS[:1])
    monkeypatch.setattr(active_vs_passive, "ROUNDS", 3)
    monkeypatch.setattr(active_vs_passive, "POPULATION", 8)
    monkeypatch.setattr(active_vs_passive, "CANDIDATE_BUDGET", 4)

    monkeypatch.chdir(tmp_path)

    # The output directory does not exist yet; run() must create it.
    assert not (tmp_path / "benchmarks").exists()

    active_vs_passive.run()

    assert (
        tmp_path / "benchmarks" / "active_vs_passive" / "results.json"
    ).exists()