import json
import hashlib
from datetime import date, datetime, timezone

from typer.testing import CliRunner

from astock import capabilities
from astock.market_desk import RestrictedListAttestation, RestrictedListStore
from astock.portfolio import portfolio_cli
from astock.research import ResearchEntry, ResearchLedger, ResearchObservation, ResearchStatus


def _active_assured_strategy_entry(ledger_path, *, code="600460"):
    plan = {
        "plan_id": f"short-{code}-20260728",
        "horizon": "short_term",
        "state": "active",
        "target": code,
        "thesis": "Test paper strategy.",
        "as_of": "2026-07-28T15:00:00+08:00",
        "entry_condition": "Condition is verified.",
        "invalidation_condition": "Risk condition breaks.",
        "review_at": "2026-07-29T15:00:00+08:00",
        "time_stop_at": "2026-08-07T15:00:00+08:00",
        "evidence_refs": ["snapshot:2026-07-28"],
    }
    entry = ResearchEntry(
        title="governed plan",
        thesis="test",
        targets=[code],
        target_type="strategy_plan",
        status=ResearchStatus.ACTIVE,
        metadata={"strategy_plan": plan},
    )
    entry.record_observation(
        ResearchObservation(
            observation_type="strategy_lifecycle_transition",
            note="released",
            observed_at=datetime.now(timezone.utc),
            evidence={
                "strategy_plan": plan,
                "release_assurance": {
                    "verdict": "pass",
                    "schema_version": "market-desk-paper-assurance.v1",
                },
            },
        )
    )
    return ResearchLedger(ledger_path).create(entry)


def _write_entry_observation_archive(tmp_path, *, code="600460"):
    raw_source_records = {
        code: {
            "code": code,
            "observed_at": "2026-07-28T15:30:00+08:00",
            "entry_condition": "confirmed",
        }
    }
    digest = hashlib.sha256(
        json.dumps(
            {
                "schema_version": "market_data_frozen_archive.v1",
                "source": "tushare_pro",
                "raw_source_records": raw_source_records,
            },
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
        ).encode("utf-8")
    ).hexdigest()
    archive_id = f"sha256:{digest}"
    archive_path = tmp_path / f"{digest}.json"
    archive_path.write_text(
        json.dumps(
            {
                "schema_version": "market_data_frozen_archive.v1",
                "source": "tushare_pro",
                "archive_id": archive_id,
                "raw_source_records": raw_source_records,
            },
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
        ),
        encoding="utf-8",
    )
    return archive_path, archive_id


def _attest_restricted_list(monkeypatch, tmp_path):
    monkeypatch.setenv("RESTRICTED_LIST_SIGNING_KEY", "test-compliance-key")
    monkeypatch.setenv("RESTRICTED_LIST_SIGNING_KEY_ID", "test-compliance-authority")
    path = tmp_path / "restricted-list.json"
    RestrictedListStore(path).attest_signed(
        RestrictedListAttestation(
            source_type="compliance-source",
            source_ref="test-clearance",
            reviewed_by="compliance-officer",
            reviewed_at="2026-07-28T15:00:00+08:00",
            expires_at="2099-12-31T15:00:00+08:00",
        ),
        key_id="test-compliance-authority",
        signing_key="test-compliance-key",
    )
    return path


def _entry_options(archive_path, archive_id, restricted_list_path):
    return [
        "--entry-observed-at",
        "2026-07-28T15:30:00+08:00",
        "--entry-evidence-ref",
        f"entry-observation:{archive_id}",
        "--entry-observation-archive-path",
        str(archive_path),
        "--restricted-list-path",
        str(restricted_list_path),
    ]


def test_portfolio_cli_uses_canonical_project_data_paths():
    assert portfolio_cli.DB_PATH == capabilities.DEFAULT_DB_PATH
    assert portfolio_cli.DEFAULT_RESEARCH_LEDGER_PATH == capabilities.DEFAULT_RESEARCH_LEDGER_PATH


def test_portfolio_cli_reads_legacy_portfolio_only_when_canonical_file_is_absent(monkeypatch, tmp_path):
    canonical_path = tmp_path / "data" / "portfolio.json"
    legacy_path = tmp_path / "src" / "data" / "portfolio.json"
    legacy_path.parent.mkdir(parents=True)
    legacy_path.write_text(
        json.dumps({"name": "legacy", "positions": {}, "trades": []}),
        encoding="utf-8",
    )
    monkeypatch.setattr(portfolio_cli, "PORTFOLIO_PATH", canonical_path)
    monkeypatch.setattr(portfolio_cli, "LEGACY_PORTFOLIO_PATH", legacy_path)

    assert portfolio_cli._load_portfolio()["name"] == "legacy"

    canonical_path.parent.mkdir(parents=True)
    canonical_path.write_text(
        json.dumps({"name": "canonical", "positions": {}, "trades": []}),
        encoding="utf-8",
    )
    assert portfolio_cli._load_portfolio()["name"] == "canonical"


def test_paper_buy_blocks_risk_limit_and_persists_explicit_stop(monkeypatch, tmp_path):
    portfolio_path = tmp_path / "portfolio.json"
    ledger_path = tmp_path / "research-ledger.json"
    entry = _active_assured_strategy_entry(ledger_path)
    archive_path, archive_id = _write_entry_observation_archive(tmp_path)
    restricted_list_path = _attest_restricted_list(monkeypatch, tmp_path)
    entry_options = _entry_options(archive_path, archive_id, restricted_list_path)
    monkeypatch.setattr(portfolio_cli, "PORTFOLIO_PATH", portfolio_path)
    monkeypatch.setattr(portfolio_cli, "_exchange_trading_days", lambda: frozenset({date(2026, 7, 28), date(2026, 7, 29)}))
    runner = CliRunner()

    ungoverned = runner.invoke(
        portfolio_cli.app,
        ["buy", "600460", "100", "--price", "100", "--trade-date", "2026-07-28", "--json"],
    )

    assert ungoverned.exit_code == 1
    assert "require an active, independently assured" in json.loads(ungoverned.stdout)["error"]
    assert not portfolio_path.exists()

    blocked = runner.invoke(
        portfolio_cli.app,
        [
            "buy", "600460", "300", "--price", "100", "--trade-date", "2026-07-28",
            "--strategy-entry-id", entry.entry_id, "--ledger-path", str(ledger_path), *entry_options, "--json",
        ],
    )

    assert blocked.exit_code == 1
    assert json.loads(blocked.stdout)["error"] == "Paper buy blocked by risk limits"
    assert not portfolio_path.exists()

    approved = runner.invoke(
        portfolio_cli.app,
        [
            "buy",
            "600460",
            "100",
            "--price",
            "100",
            "--trade-date",
            "2026-07-28",
            "--stop-distance-pct",
            "0.05",
            "--strategy-entry-id",
            entry.entry_id,
            "--ledger-path",
            str(ledger_path),
            *entry_options,
            "--json",
        ],
    )

    assert approved.exit_code == 0
    saved = json.loads(portfolio_path.read_text(encoding="utf-8"))
    assert saved["positions"]["600460"]["stop_distance_pct"] == 0.05
    assert saved["positions"]["600460"]["governance_status"] == "governed"
    assert saved["positions"]["600460"]["strategy_entry_id"] == entry.entry_id
    assert saved["trades"][0]["entry_evidence"]["observation_archive"]["archive_id"] == archive_id
    assert saved["trades"][0]["amount"] == 10_000
    governance = runner.invoke(
        portfolio_cli.app,
        ["governance", "--ledger-path", str(ledger_path), "--json"],
    )
    assert governance.exit_code == 0
    assert json.loads(governance.stdout)["governance_status"] == "pass"


def test_paper_portfolio_governance_cli_marks_unlinked_positions(monkeypatch, tmp_path):
    portfolio_path = tmp_path / "portfolio.json"
    portfolio_path.write_text(
        json.dumps({"positions": {"600460": {"code": "600460"}}, "cash": 90_000, "trades": []}),
        encoding="utf-8",
    )
    monkeypatch.setattr(portfolio_cli, "PORTFOLIO_PATH", portfolio_path)

    result = CliRunner().invoke(portfolio_cli.app, ["governance", "--json"])

    assert result.exit_code == 0
    payload = json.loads(result.stdout)
    assert payload["governance_status"] == "blocked"
    assert payload["unlinked_legacy_count"] == 1


def test_paper_portfolio_enforces_t_plus_one_sellability(monkeypatch, tmp_path):
    portfolio_path = tmp_path / "portfolio.json"
    ledger_path = tmp_path / "research-ledger.json"
    entry = _active_assured_strategy_entry(ledger_path)
    archive_path, archive_id = _write_entry_observation_archive(tmp_path)
    restricted_list_path = _attest_restricted_list(monkeypatch, tmp_path)
    entry_options = _entry_options(archive_path, archive_id, restricted_list_path)
    exit_options = [
        "--exit-reason",
        "risk_reduce",
        "--exit-observed-at",
        "2026-07-29T10:00:00+08:00",
        "--exit-evidence-ref",
        f"exit-observation:{archive_id}",
        "--exit-observation-archive-path",
        str(archive_path),
        "--ledger-path",
        str(ledger_path),
    ]
    monkeypatch.setattr(portfolio_cli, "PORTFOLIO_PATH", portfolio_path)
    monkeypatch.setattr(portfolio_cli, "_exchange_trading_days", lambda: frozenset({date(2026, 7, 28), date(2026, 7, 29)}))
    runner = CliRunner()

    buy = runner.invoke(
        portfolio_cli.app,
        [
            "buy", "600460", "100", "--price", "100", "--trade-date", "2026-07-28",
            "--strategy-entry-id", entry.entry_id, "--ledger-path", str(ledger_path), *entry_options, "--json",
        ],
    )
    same_day_sell = runner.invoke(
        portfolio_cli.app,
        ["sell", "600460", "100", "--price", "100", "--trade-date", "2026-07-28", "--json"],
    )
    missing_evidence_sell = runner.invoke(
        portfolio_cli.app,
        [
            "sell", "600460", "100", "--price", "100", "--trade-date", "2026-07-29",
            "--ledger-path", str(ledger_path), "--json",
        ],
    )
    next_day_sell = runner.invoke(
        portfolio_cli.app,
        [
            "sell", "600460", "100", "--price", "100", "--trade-date", "2026-07-29",
            *exit_options, "--json",
        ],
    )

    assert buy.exit_code == 0
    assert same_day_sell.exit_code == 1
    assert "T+1 restriction" in json.loads(same_day_sell.stdout)["error"]
    assert missing_evidence_sell.exit_code == 1
    assert "exit-reason" in json.loads(missing_evidence_sell.stdout)["error"]
    assert next_day_sell.exit_code == 0
    assert json.loads(next_day_sell.stdout)["exit_evidence"]["reason"] == "risk_reduce"
    assert json.loads(next_day_sell.stdout)["position_closed"] is True
    governance = runner.invoke(
        portfolio_cli.app,
        ["governance", "--ledger-path", str(ledger_path), "--json"],
    )
    governance_payload = json.loads(governance.stdout)
    assert governance.exit_code == 0
    assert governance_payload["governance_status"] == "blocked"
    assert governance_payload["exit_review_required_count"] == 1
    exit_id = governance_payload["exit_review_queue"][0]["exit_id"]
    assert exit_id.startswith("paper-exit:sha256:")
    capabilities.record_market_desk_strategy_review(
        entry.entry_id,
        reviewer="portfolio-manager",
        reason="Paper exit was reviewed after risk reduction.",
        evidence_refs=[exit_id],
        observed_at="2026-07-29T12:00:00+08:00",
        next_review_at="2026-07-30T15:00:00+08:00",
        ledger_path=ledger_path,
    )
    resolved = runner.invoke(
        portfolio_cli.app,
        ["governance", "--ledger-path", str(ledger_path), "--json"],
    )
    resolved_payload = json.loads(resolved.stdout)
    assert resolved_payload["exit_review_required_count"] == 0
    assert resolved_payload["resolved_exit_review_count"] == 1


def test_paper_sell_rejects_nonpositive_share_count_without_mutating_portfolio(monkeypatch, tmp_path):
    portfolio_path = tmp_path / "portfolio.json"
    initial = {
        "cash": 90_000,
        "positions": {
            "600460": {
                "code": "600460",
                "shares": 100,
                "available_shares": 100,
                "cost_price": 100,
                "current_price": 100,
            }
        },
        "trades": [],
    }
    portfolio_path.write_text(json.dumps(initial), encoding="utf-8")
    monkeypatch.setattr(portfolio_cli, "PORTFOLIO_PATH", portfolio_path)
    monkeypatch.setattr(
        portfolio_cli,
        "_exchange_trading_days",
        lambda: frozenset({date(2026, 7, 28), date(2026, 7, 29)}),
    )

    result = CliRunner().invoke(
        portfolio_cli.app,
        ["sell", "600460", "0", "--price", "100", "--trade-date", "2026-07-28", "--json"],
    )

    assert result.exit_code == 1
    assert "positive" in json.loads(result.stdout)["error"]
    assert json.loads(portfolio_path.read_text(encoding="utf-8")) == initial


def test_short_horizon_paper_buy_requires_a_share_stress_inputs(monkeypatch, tmp_path):
    monkeypatch.setattr(portfolio_cli, "PORTFOLIO_PATH", tmp_path / "portfolio.json")

    result = CliRunner().invoke(
        portfolio_cli.app,
        ["buy", "600460", "100", "--price", "100", "--horizon", "short_term", "--json"],
    )

    assert result.exit_code == 1
    assert "require overnight-stress-pct" in json.loads(result.stdout)["error"]


def test_portfolio_risk_accepts_auditable_structural_context(monkeypatch, tmp_path):
    portfolio_path = tmp_path / "portfolio.json"
    portfolio_path.write_text(
        json.dumps(
            {
                "cash": 80_000,
                "positions": {
                    "600460": {
                        "shares": 100,
                        "current_price": 100,
                        "stop_distance_pct": 0.03,
                    },
                    "688001": {
                        "shares": 100,
                        "current_price": 100,
                        "stop_distance_pct": 0.03,
                    },
                },
                "trades": [],
            }
        ),
        encoding="utf-8",
    )
    context_path = tmp_path / "risk-context.json"
    context_path.write_text(
        json.dumps(
            {
                "schema_version": "portfolio-factor-risk-context.v1",
                "taxonomy_version": "factor-taxonomy.v1",
                "approved_by": "quant-risk-modeler",
                "approved_at": "2026-07-28T15:00:00+08:00",
                "valid_until": "2099-12-31T15:00:00+08:00",
                "classifications": {
                    "600460": {
                        "taxonomy_version": "factor-taxonomy.v1",
                        "as_of": "2026-07-28T15:00:00+08:00",
                        "source_refs": ["taxonomy:600460"],
                        "factor_exposures": {"growth": 1.0},
                    },
                    "688001": {
                        "taxonomy_version": "factor-taxonomy.v1",
                        "as_of": "2026-07-28T15:00:00+08:00",
                        "source_refs": ["taxonomy:688001"],
                        "factor_exposures": {"growth": 0.5},
                    },
                },
                "positions": {
                    "600460": {
                        "average_daily_turnover": 1_000_000,
                    },
                    "688001": {
                        "average_daily_turnover": 1_000_000,
                    },
                },
                "correlations": {"600460|688001": 0.6},
                "stress_scenarios": {
                    "growth_down": {
                        "as_of": "2026-07-28T15:00:00+08:00",
                        "source_refs": ["stress:base"],
                        "shocks": {"growth": -0.1},
                    }
                },
            }
        ),
        encoding="utf-8",
    )
    monkeypatch.setattr(portfolio_cli, "PORTFOLIO_PATH", portfolio_path)

    result = CliRunner().invoke(
        portfolio_cli.app, ["risk", "--context", str(context_path), "--json"]
    )

    assert result.exit_code == 0
    payload = json.loads(result.stdout)
    assert payload["structural_risk"]["factor_exposure"]["growth"] == 0.15
    assert payload["structural_risk"]["scenario_losses"]["growth_down"] == 0.015
    assert payload["structural_risk"]["blockers"] == []
