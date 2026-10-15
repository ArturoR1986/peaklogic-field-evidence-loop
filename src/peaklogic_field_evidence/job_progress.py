"""Durable job history around the existing job/requirement/quality contracts.

SQLite is the sole store; reports are projections, never a second source of truth.
Day ordinals are explicitly not capture timestamps. Semantic observations are
attributed annotations; OpenCV supplies quality measurements, not acceptance.
"""
from __future__ import annotations

import hashlib
import json
import sqlite3
import uuid
from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import cv2

from .job_packet import JobEvidenceRecord
from .media import analyze_quality
from .requirement_resolver import (
    EvidenceRequirement, RequirementSource, SourceKind, VisualCheckability,
    RequirementEvidenceLink, RequirementEvidenceStatus, resolve_requirement,
)


def canonical(value: Any) -> str:
    return json.dumps(value, sort_keys=True, ensure_ascii=False, allow_nan=False)


def requirement_from_dict(value: dict) -> EvidenceRequirement:
    data = dict(value)
    source = dict(data.pop("source"))
    source["source_kind"] = SourceKind(source["source_kind"])
    data["source"] = RequirementSource(**source)
    data["visual_checkability"] = VisualCheckability(data["visual_checkability"])
    data["visual_limits"] = tuple(data.get("visual_limits", ()))
    result = EvidenceRequirement(**data)
    result.validate()
    return result


class PersistentJobLoop:
    """Append-only, transactional events, with deterministic reload/replay.

    event_id is an idempotency key, scoped to job. Conflicting reuse is rejected.
    No event is committed until the entire prospective history validates.
    """

    def __init__(self, path: str | Path):
        self.db = sqlite3.connect(str(path))
        # Keep the committed record in one file. WAL sidecars are unsuitable for
        # copied review bundles and workspace snapshot boundaries.
        self.db.execute("PRAGMA journal_mode=DELETE")
        self.db.execute("PRAGMA synchronous=FULL")
        self.db.execute("""CREATE TABLE IF NOT EXISTS events (
            seq INTEGER PRIMARY KEY AUTOINCREMENT, job_id TEXT NOT NULL,
            event_id TEXT NOT NULL, kind TEXT NOT NULL, day INTEGER,
            captured_at TEXT, ingested_at TEXT NOT NULL, payload TEXT NOT NULL,
            UNIQUE(job_id,event_id))""")
        self.db.commit()

    def close(self):
        self.db.close()

    def export_database(self, destination: str | Path) -> None:
        """Atomically export the complete committed database, never copy sidecars."""
        target = Path(destination)
        target.parent.mkdir(parents=True, exist_ok=True)
        temporary = target.with_name(target.name + "." + uuid.uuid4().hex + ".tmp")
        try:
            backup = sqlite3.connect(str(temporary))
            try:
                self.db.backup(backup)
            finally:
                backup.close()
            temporary.replace(target)
        finally:
            temporary.unlink(missing_ok=True)

    def events(self, job_id: str) -> list[dict]:
        rows = self.db.execute(
            "SELECT seq,event_id,kind,day,captured_at,ingested_at,payload FROM events "
            "WHERE job_id=? ORDER BY seq", (job_id,)).fetchall()
        return [dict(seq=r[0], event_id=r[1], kind=r[2], day=r[3],
                     captured_at=r[4], ingested_at=r[5], payload=json.loads(r[6])) for r in rows]

    def append(self, job_id: str, event_id: str, kind: str, payload: dict,
               *, day: int | None = None, captured_at: str | None = None) -> dict:
        if not job_id or not event_id or (day is not None and (type(day) is not int or day < 0)):
            raise ValueError("job/event identity and nonnegative day ordinal required")
        if captured_at:
            stamp = datetime.fromisoformat(captured_at.replace("Z", "+00:00"))
            if stamp.tzinfo is None:
                raise ValueError("capture timestamp requires timezone")
        body = canonical(payload)
        # BEGIN IMMEDIATE serializes writers; read/validate/write is one transaction.
        with self.db:
            self.db.execute("BEGIN IMMEDIATE")
            existing = self.db.execute(
                "SELECT kind,day,captured_at,payload FROM events WHERE job_id=? AND event_id=?",
                (job_id, event_id)).fetchone()
            if existing:
                if existing != (kind, day, captured_at, body):
                    raise ValueError("conflicting idempotency key; append an amendment")
                return self.report(job_id)
            self.db.execute(
                "INSERT INTO events(job_id,event_id,kind,day,captured_at,ingested_at,payload) "
                "VALUES(?,?,?,?,?,?,?)", (job_id, event_id, kind, day, captured_at,
                datetime.now(timezone.utc).isoformat(), body))
            return self.report(job_id)  # exceptions roll back the inserted event

    def create(self, record: JobEvidenceRecord, manifest: list[dict]) -> dict:
        return self.append(record.job_id, "job-created", "create", {
            "record": record.to_dict(), "manifest": manifest}, day=0)

    def measure_image(self, job_id: str, media_id: str, path: str | Path) -> dict:
        """Reuse OpenCV quality implementation; retain decode failure as an event."""
        raw = Path(path).read_bytes()
        image = cv2.imread(str(path))
        metrics = asdict(analyze_quality(image))
        manifest = {m["media_id"]: m for m in self.report(job_id)["manifest"]}
        if media_id not in manifest:
            raise ValueError("quality media not bound to this job")
        return self.append(job_id, "quality:" + media_id, "quality", {
            "media_id": media_id, "sha256": hashlib.sha256(raw).hexdigest(),
            "opencv_version": cv2.__version__, "metrics": metrics,
            "decoded": image is not None}, day=manifest[media_id].get("day"),
            captured_at=manifest[media_id].get("captured_at"))

    def report(self, job_id: str, *, through_day: int | None = None,
               from_day: int | None = None) -> dict:
        all_events = self.events(job_id)
        if not all_events or all_events[0]["kind"] != "create":
            raise ValueError("job must be created before events")
        creation = all_events[0]["payload"]
        record = creation["record"]
        if record["job_id"] != job_id or record["task_type"] not in {"installation", "service_inspection"}:
            raise ValueError("work-order job identity/classification required")
        manifest = {m["media_id"]: m for m in creation["manifest"]}
        if len(manifest) != len(creation["manifest"]):
            raise ValueError("manifest media identities must be unique")
        for m in manifest.values():
            if m.get("job_id") != job_id or not m.get("provenance"):
                raise ValueError("manifest requires matching job and provenance")
        if any(mid not in manifest for mid in record["work_order_artifacts"]):
            raise ValueError("work-order artifacts must be bound in the frozen manifest")
        state = dict(job=record, manifest=list(manifest.values()), expected_work_map={},
                     observations={}, quality={}, concealments={}, physical_progress={},
                     exception_history=[], professional_acceptance={"status": "pending"},
                     field_record_closed=False, trace_event_ids=[], corrections=[])
        links = {}
        for event in all_events[1:]:
            # Intake/quality is metadata for the frozen manifest, not a later capture.
            if through_day is not None and event["day"] is not None and event["day"] > through_day:
                continue
            p, kind, eid = event["payload"], event["kind"], event["event_id"]
            state["trace_event_ids"].append(eid)
            if kind == "requirement":
                req = requirement_from_dict(p["requirement"])
                if req.source.source_id not in manifest:
                    raise ValueError("requirement source not bound in frozen manifest")
                if req.requirement_id in state["expected_work_map"]:
                    raise ValueError("duplicate requirement; use an amendment")
                if p["component"] == "unresolved" or not p.get("authority"):
                    raise ValueError("requirement needs component and authority provenance")
                state["expected_work_map"][req.requirement_id] = {**p, "event_id": eid}
            elif kind == "quality":
                if p["media_id"] not in manifest:
                    raise ValueError("quality media not bound to this job")
                expected_hash = manifest[p["media_id"]].get("sha256")
                if expected_hash and expected_hash != p["sha256"]:
                    raise ValueError("media bytes do not match the frozen source hash")
                state["quality"][p["media_id"]] = {**p, "event_id": eid}
            elif kind == "observation":
                if p["media_id"] not in manifest or not p.get("actor") or not p.get("method"):
                    raise ValueError("observation requires bound source and attribution")
                if not p.get("statement"):
                    raise ValueError("observation statement required")
                state["observations"][eid] = {**p, "day": event["day"], "event_id": eid,
                    "captured_at": event["captured_at"], "ingested_at": event["ingested_at"]}
            elif kind == "link":
                if p["requirement_id"] not in state["expected_work_map"] or p["observation_id"] not in state["observations"]:
                    if through_day is not None:
                        continue  # dependency falls outside this effective-day projection
                    raise ValueError("link requires existing requirement and observation")
                if p.get("modality") not in {"visual", "nonvisual"}:
                    raise ValueError("link modality required")
                RequirementEvidenceStatus(p["status"])
                links[eid] = {**p, "event_id": eid, "active": True}
            elif kind == "concealment":
                if event["day"] is None or not p.get("source_ids") or not p.get("actor"):
                    raise ValueError("concealment requires known day and source attribution")
                if any(mid not in manifest for mid in p["source_ids"]):
                    raise ValueError("concealment sources not bound")
                old = state["concealments"].get(p["component"])
                if old and old["day"] > event["day"]:
                    raise ValueError("use correction for earlier concealment")
                state["concealments"][p["component"]] = {**p, "day": event["day"], "event_id": eid}
                # Historical exception exists even if later evidence resolves it.
                for rid, r in state["expected_work_map"].items():
                    req = requirement_from_dict(r["requirement"])
                    if r["component"] == p["component"] and req.capture_before_stage:
                        supported = self._eligible(rid, r, links, state, manifest)
                        if not supported:
                            state["exception_history"].append(dict(requirement_id=rid,
                                event_id=eid, day=event["day"], reason="before_cover_proof_missing"))
            elif kind == "progress":
                if not p.get("source_ids") or any(mid not in manifest for mid in p["source_ids"]):
                    raise ValueError("physical progress requires bound sources")
                if not p.get("actor") or not p.get("method") or not p.get("status"):
                    raise ValueError("physical progress requires attributed status")
                # Arrival order cannot overwrite a later effective state with an older one.
                progress_key = p["component"] + ("@" + p["zone"] if p.get("zone") else "")
                previous = state["physical_progress"].get(progress_key)
                if previous is None or (event["day"] is not None and
                        (previous["day"] is None or event["day"] >= previous["day"])):
                    state["physical_progress"][progress_key] = {**p, "day": event["day"], "event_id": eid}
            elif kind == "correction":
                if p.get("target_event_id") not in links or not p.get("reason") or not p.get("actor"):
                    raise ValueError("correction requires link target, actor and reason")
                links[p["target_event_id"]]["active"] = False
                state["corrections"].append({**p, "event_id": eid})
            elif kind == "requirement_amendment":
                rid = p["requirement"]["requirement_id"]
                previous = state["expected_work_map"].get(rid)
                if not previous or p.get("target_event_id") != previous["event_id"] or not p.get("reason") or not p.get("actor"):
                    raise ValueError("requirement amendment requires current target, reason and actor")
                amended = requirement_from_dict(p["requirement"])
                if amended.source.source_id not in manifest:
                    raise ValueError("amended requirement source not bound")
                if not p.get("authority") or not p.get("component"):
                    raise ValueError("amendment requires component and authority")
                state["corrections"].append({**p, "previous": previous, "event_id": eid})
                state["expected_work_map"][rid] = {**p, "event_id": eid}
                # Existing links addressed the earlier statement; relink explicitly.
                for link in links.values():
                    if link["requirement_id"] == rid:
                        link["active"] = False
            elif kind == "close_record":
                if not p.get("source_ids") or any(mid not in manifest for mid in p["source_ids"]):
                    raise ValueError("closure requires bound source")
                state["field_record_closed"] = True
                for rid, r in state["expected_work_map"].items():
                    if r["requirement"].get("required", True) and not self._eligible(rid, r, links, state, manifest):
                        state["exception_history"].append(dict(requirement_id=rid,
                            event_id=eid, day=event["day"], reason="closed_record_required_proof_unresolved"))
            elif kind == "human_review":
                if not p.get("actor") or not p.get("qualification") or not p.get("source_ids") or not p.get("scope"):
                    raise ValueError("review requires qualified actor, scope and source")
                if any(mid not in manifest for mid in p["source_ids"]):
                    raise ValueError("review sources not bound")
                if p.get("status") not in {"accepted", "rejected", "pending"}:
                    raise ValueError("unknown review status")
                state["professional_acceptance"] = {**p, "event_id": eid}
            else:
                raise ValueError("unknown event kind: " + kind)
        # Canonical duplicate attribution, independent of arrival order.
        hashes = {}
        for mid in sorted(state["quality"]):
            q = state["quality"][mid]
            q["duplicate_of"] = hashes.get(q["sha256"])
            hashes.setdefault(q["sha256"], mid)
            q["next_action"] = ("reject_duplicate" if q["duplicate_of"] else
                "exclude_irrelevant" if manifest[mid].get("relevant") is False else
                "continue_review" if q["metrics"]["usable"] else
                "record_quality_exception" if state["field_record_closed"] else "retake")
        state["component_decisions"] = []
        for rid, r in state["expected_work_map"].items():
            req = requirement_from_dict(r["requirement"])
            eligible = self._eligible(rid, r, links, state, manifest)
            accepted_links = [RequirementEvidenceLink(rid, mid, RequirementEvidenceStatus.SUPPORTED)
                              for mid in eligible]
            for link in links.values():
                if link["active"] and link["requirement_id"] == rid:
                    o = state["observations"][link["observation_id"]]
                    if req.visual_checkability == VisualCheckability.NONVISUAL and link["modality"] == "visual":
                        continue
                    if o["media_id"] not in eligible:
                        unusable = link["modality"] == "visual" and not state["quality"].get(o["media_id"], {}).get("metrics", {}).get("usable", False)
                        accepted_links.append(RequirementEvidenceLink(rid, o["media_id"],
                            RequirementEvidenceStatus.REJECTED if link["status"] == "rejected" or unusable
                            else RequirementEvidenceStatus.UNCERTAIN))
            concealed = r["component"] in state["concealments"]
            resolution = resolve_requirement(req, accepted_links,
                current_stage="covering_started" if concealed else "installation").to_dict()
            if state["field_record_closed"] and resolution["status"] != "supported":
                resolution["next_action"] = dict(action="escalate_human", proof_point_id=rid,
                    reason="Closed record: reconcile preserved evidence or record an exception. " + req.evidence_question)
            else:
                resolution["next_action"]["reason"] += " " + req.evidence_question
            resolution.update(component=r["component"], zone=r.get("zone", "unresolved"),
                physical_progress=state["physical_progress"].get(r["component"], {"status": "unresolved"}),
                observed_zone_progress=[p for p in state["physical_progress"].values() if p["component"] == r["component"]],
                source=req.source.source_id, requirement_event_id=r["event_id"],
                evidence_trace=[l["event_id"] for l in links.values() if l["requirement_id"] == rid],
                historical_exceptions=[e for e in state["exception_history"] if e["requirement_id"] == rid])
            state["component_decisions"].append(resolution)
        state["unresolved_bindings"] = [o for o in state["observations"].values()
            if o.get("component", "unresolved") == "unresolved" or o.get("zone", "unresolved") == "unresolved"]
        state["binding_actions"] = [dict(observation_id=o["event_id"], media_id=o["media_id"],
            action="escalate_human", reason="Resolve the work-order component and project zone before crediting this observation.")
            for o in state["unresolved_bindings"]]
        observed_media = {o["media_id"] for o in state["observations"].values()}
        state["unreviewed_media_ids"] = [m["media_id"] for m in manifest.values()
            if m.get("media_type") in {"photo", "video_frame"} and m["media_id"] not in observed_media and m.get("relevant") is not False]
        state["pending_review_actions"] = [dict(media_id=mid, action="escalate_human",
            reason="Component-level observation and project-zone binding remain unreviewed; do not credit required proof.")
            for mid in state["unreviewed_media_ids"]]
        state["period_observations"] = [o for o in state["observations"].values()
            if from_day is None or (o["day"] is not None and o["day"] >= from_day)]
        state["chronology_basis"] = "attributed day ordinal; unknown capture timestamps stay unknown"
        state["report_period"] = {"from_day": from_day, "through_day": through_day}
        return state

    @staticmethod
    def _eligible(rid, r, links, state, manifest):
        req = requirement_from_dict(r["requirement"])
        accepted = set()
        for link in links.values():
            if not link["active"] or link["requirement_id"] != rid or link["status"] != "supported":
                continue
            o = state["observations"][link["observation_id"]]
            if o.get("component") != r["component"] or o.get("zone", "unresolved") == "unresolved":
                continue
            if r.get("zone", "unresolved") not in {"unresolved", o["zone"]}:
                continue
            if not link.get("human_confirmed") or r["authority"] == "unresolved":
                continue
            mid = o["media_id"]
            if manifest[mid].get("relevant") is False:
                continue
            if link["modality"] == "visual":
                q = state["quality"].get(mid)
                if req.visual_checkability != VisualCheckability.VISUAL or not q or not q["metrics"]["usable"]:
                    continue
            elif not link.get("nonvisual_confirmation"):
                continue
            concealment = state["concealments"].get(r["component"])
            if req.capture_before_stage and concealment:
                # Same-day ordering unknown: do not assume a pre-cover capture.
                if o["day"] is None or o["day"] >= concealment["day"] or not link.get("capture_provenance_verified"):
                    continue
            digest = state["quality"].get(mid, {}).get("sha256", mid)
            accepted.add((digest, mid))
        unique = {}
        for digest, mid in sorted(accepted):
            unique.setdefault(digest, mid)
        return tuple(unique.values())
