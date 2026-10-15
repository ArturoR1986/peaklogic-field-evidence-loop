import json

from peaklogic_field_evidence.job_progress_cli import main
from test_job_progress import setup_job


def test_cli_replay_is_portable_and_reports_derive_from_store(tmp_path, monkeypatch):
    original = setup_job(tmp_path)
    packet = {"job_id": "job", "events": original.events("job")}
    packet_path = tmp_path / "packet.json"
    packet_path.write_text(json.dumps(packet))
    out = tmp_path / "report"
    argv = ["peaklogic-job-loop", "replay", "--db", str(tmp_path / "copy.db"),
        "--job-id", "job", "--input", str(packet_path), "--output", str(out)]
    monkeypatch.setattr("sys.argv", argv)
    main()
    first = out.with_suffix(".json").read_text()
    main()
    assert out.with_suffix(".json").read_text() == first
    assert "Work order: wo" in out.with_suffix(".md").read_text()
    assert len((tmp_path / "report.trace.jsonl").read_text().splitlines()) == 2


def test_requirement_amendment_preserves_previous_source_and_invalidates_links(tmp_path):
    store = setup_job(tmp_path)
    req = store.report("job")["expected_work_map"]["anchor"]["requirement"]
    req["requirement_statement"] = "Record the correct anchor arrow and identity"
    store.append("job", "amend", "requirement_amendment", dict(requirement=req,
        component="anchor", zone="roof", authority="work_order", target_event_id="req",
        actor="reviewer", reason="Clarify component identity"), day=2)
    report = store.report("job")
    assert report["corrections"][0]["previous"]["requirement"]["requirement_statement"] == "Record arrow"
    assert report["component_decisions"][0]["requirement_event_id"] == "amend"
