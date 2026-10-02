"""Replay a frozen job event packet and derive reports from the durable store."""
import argparse
import json
from pathlib import Path

from .job_progress import PersistentJobLoop


def render_report(state: dict) -> str:
    job = state["job"]
    lines = [f"# {job['job_id']} — persistent job report", "",
        f"Work order: {job['work_order_id']} · Type: {job['task_type']}", "",
        f"Field record closed: {state['field_record_closed']}. Professional acceptance: {state['professional_acceptance']['status']}.", "",
        "Chronology uses attributed day ordinals. Unknown capture timestamps remain unknown.", "",
        "## Progress", ""]
    for component, progress in state["physical_progress"].items():
        lines.append(f"- {component}: {progress['status']} (Day {progress['day']}; {progress['method']}; sources: {', '.join(progress['source_ids'])}; event: {progress['event_id']}).")
    if not state["physical_progress"]:
        lines.append("Physical progress remains unresolved.")
    lines.extend(["", "## Evidence and actions", "",
        "| Component | Zone | Evidence state | Action | Requirement/source trace |",
        "| --- | --- | --- | --- | --- |"])
    for d in state["component_decisions"]:
        lines.append(f"| {d['component']} | {d['zone']} | {d['status']} | {d['next_action']['action']}: {d['next_action']['reason']} | {d['requirement_event_id']} → {d['source']} |")
    lines.extend(["", "## Problems", "",
        f"- {len(state['unresolved_bindings'])} observations retain unresolved component or zone binding.",
        f"- {len(state['unreviewed_media_ids'])} photo/frame entries await component-level semantic review; this is a partial semantic replay.",
        f"- {len(state['exception_history'])} historical proof exceptions retained.",
        "- No workmanship, safety, manufacturer compliance or completion acceptance is inferred.", "",
        "## OpenCV technical evidence", ""])
    q = state["quality"]
    lines.append(f"{len(q)} image/frame entries measured; {sum(x['decoded'] for x in q.values())} decoded; {sum(bool(x['duplicate_of']) for x in q.values())} duplicate byte streams beyond the canonical entry.")
    for mid, item in q.items():
        if not item["metrics"]["usable"] or item["next_action"] == "exclude_irrelevant":
            lines.append(f"- {mid}: {item['metrics']['reasons']}; action: {item['next_action']}; sharpness {item['metrics']['sharpness']:.2f}; trace {item['event_id']}.")
    lines.extend(["", "## Period observations", ""])
    for o in sorted(state["period_observations"], key=lambda o:(o["day"] is None, o["day"] or 0, o["event_id"])):
        lines.append(f"- Day {o['day']}: {o['statement']} Source: {o['media_id']}; method: {o['method']}; actor: {o['actor']}; trace: {o['event_id']}.")
    return "\n".join(lines) + "\n"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=["replay", "report"])
    parser.add_argument("--db", required=True)
    parser.add_argument("--job-id", required=True)
    parser.add_argument("--input", help="Frozen JSON event packet for replay")
    parser.add_argument("--output", required=True, help="Output prefix: .json, .md and .trace.jsonl")
    parser.add_argument("--through-day", type=int)
    parser.add_argument("--from-day", type=int)
    args = parser.parse_args()
    store = PersistentJobLoop(args.db)
    try:
        if args.command == "replay":
            if not args.input:
                parser.error("replay requires --input")
            packet = json.loads(Path(args.input).read_text())
            if packet["job_id"] != args.job_id:
                raise ValueError("packet belongs to another job")
            for event in packet["events"]:
                store.append(args.job_id, event["event_id"], event["kind"], event["payload"],
                    day=event.get("day"), captured_at=event.get("captured_at"))
        state = store.report(args.job_id, through_day=args.through_day, from_day=args.from_day)
        prefix = Path(args.output)
        prefix.parent.mkdir(parents=True, exist_ok=True)
        Path(str(prefix) + ".json").write_text(json.dumps(state, indent=2, ensure_ascii=False) + "\n")
        Path(str(prefix) + ".md").write_text(render_report(state))
        Path(str(prefix) + ".trace.jsonl").write_text("".join(json.dumps(e, ensure_ascii=False) + "\n" for e in store.events(args.job_id)))
    finally:
        store.close()


if __name__ == "__main__":
    main()
