"""Build real trial packets using explicit input paths and preserved Drive IDs.

This is a controlled replay fixture, not a learned semantic detector. All semantic
labels below are explicit manual annotations; source authority stays separate.
"""
import argparse
from dataclasses import asdict
import hashlib
import json
from pathlib import Path

import cv2

from peaklogic_field_evidence.job_packet import JobEvidenceRecord
from peaklogic_field_evidence.job_progress import PersistentJobLoop
from peaklogic_field_evidence.job_progress_cli import render_report
from peaklogic_field_evidence.media import sample_video
from peaklogic_field_evidence.scene import analyze_scene_association


def write_json(path, value):
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--workspace", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--media-index", type=Path, required=True,
        help="Local JSON [{id,name,path}] matching the frozen Drive inventory")
    args = parser.parse_args()
    root, out = args.workspace, args.output
    out.mkdir(parents=True, exist_ok=True)
    repo = Path(__file__).resolve().parents[1]
    inventory = json.loads((repo / "docs/trials/persistent_source_inventory_v2.json").read_text())
    downloads = {r["id"]: r for r in json.loads(args.media_index.read_text())}
    local_files = {p.name: p for p in sorted((root / "attachments").rglob("*.jpg"))}
    jobs = ["Trial-001-Kissling-6956", "Trial-002-BMW-Thoma-20266878"]
    manifests, paths = [[], []], [{}, {}]
    day_folders = {"1Zkh1cwmQEW0CBR7ack-TeGh9tW4aAYXF": 6,
                   "1KHEVwuH7s451tPC5SfMctxjLCATHK5rb": 5,
                   "1c9tBrZClM7S3bcHthIN9i8HKkV9b1Lku": 4,
                   "1M_dXoC4EI6NUasgb4_btjYh1awbHMSev": 0}
    seen = set()
    for folder in inventory:
        for f in folder["files"]:
            if f["mime_type"] != "image/jpeg" or f["id"] in seen:
                continue
            seen.add(f["id"])
            name = f["title"]
            if folder.get("day"):
                day = folder["day"]
            elif folder["id"] in day_folders:
                day = day_folders[folder["id"]]
            else:
                # These preserved intake batches were assigned in the archived day reviews.
                day = 1 if name.startswith("10000513") else 3 if name.startswith("10000515") else 4
            mid = f["id"]
            manifests[0].append(dict(media_id=mid, job_id=jobs[0], name=name, day=day,
                captured_at=None, media_type="document_scan" if day == 0 else "photo",
                provenance=f["url"], day_provenance="preserved folder + archived day reviews; manual batch binding",
                relevant=name != "1000051903.jpg", availability="downloaded",
                relevance_provenance="archived manual review 1bE5qi5OrSiagZWUHJ67Chjxmkt6qx92V7q7EOPdKT24 / Day 5" if name == "1000051903.jpg" else "not yet semantically screened",
                provider_modified_at=f["modified_time"], provider_size=f["size"]))
            paths[0][mid] = Path(downloads[mid]["path"])
    ids2 = json.loads((root / "trial2_drive_ids.json").read_text())
    ids2.update({"1000052052.jpg": "1dbbq8MiRvgR-m_o4O6lcJrA2vF3G2-8w",
                 "1000052053.jpg": "19ka-UD4ZTw7RzrPeYOBLeIJBQrDcOY6g",
                 "1000052054.jpg": "155mXmltl5aYQaGLBQBEEPYILAUHrKygn"})
    for name, mid in sorted(ids2.items()):
        if not name.endswith(".jpg"):
            continue
        manifests[1].append(dict(media_id=mid, job_id=jobs[1], name=name,
            day=0 if name in {"1000052052.jpg", "1000052053.jpg", "1000052054.jpg"} else 1,
            captured_at=None, media_type="document_scan" if name in {"1000052052.jpg", "1000052053.jpg", "1000052054.jpg"} else "photo",
            provenance="https://drive.google.com/file/d/" + mid,
            day_provenance="Trial 002 Day 01 closed intake manifest", availability="downloaded"))
        paths[1][mid] = local_files[name]
    source_ids = ["1DPRRqgwYz6BK0x2Atxp8Bmu8UZE8O9kuIdQdfWKvNzw",
        "1KODeaTQfdmSsyHC_uwMlBy6-LLJXGxoBAqintKG9CEs",
        "1bE5qi5OrSiagZWUHJ67Chjxmkt6qx92V7q7EOPdKT24",
        "1Nlvd2-q6XBFlrGoi3_eFMYRv8WmvBMjVvUsb3lVokwg"]
    for mid in source_ids:
        manifests[0].append(dict(media_id=mid, job_id=jobs[0], name="archived source report",
            day=0, media_type="document", captured_at=None,
            provenance="https://drive.google.com/file/d/" + mid, availability="read_text"))
    manifests[0].append(dict(media_id="day1-walkthrough-raw-unavailable", job_id=jobs[0],
        name="Day 1 approximately 98-second walkthrough", day=1, captured_at=None,
        media_type="video", availability="raw_not_located", provenance="Day 1 log " + source_ids[0]))
    videos = [(0, "11e99r1dRgGenkPkrh-UlqS-pUZHqWqj5", root / "1000051514.mp4", None),
              (0, "1pjxVi2Xau53fy5CrUCJgM-2A91HxHgqg", root / "1000051889.mp4", 5),
              (1, "1L2YlLrmXZSItlggfb-i5i6jah9XzbA_N", root / "trial2_1000052062.mp4", 1)]
    video_metrics = []
    for index, mid, path, day in videos:
        cap = cv2.VideoCapture(str(path))
        fps, frames = cap.get(cv2.CAP_PROP_FPS), int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        cap.release()
        samples = sample_video(path, sample_fps=1.5, max_candidates=120)
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        manifests[index].append(dict(media_id=mid, job_id=jobs[index], name=path.name,
            day=day, captured_at=None, media_type="video", provenance="https://drive.google.com/file/d/" + mid,
            availability="downloaded", sha256=digest,
            day_provenance="preserved Day 05/Day 01 folder" if day else "day binding unresolved"))
        video_metrics.append(dict(job_id=jobs[index], media_id=mid, source_sha256=digest,
            fps=fps, declared_frame_count=frames, duration_seconds=frames/fps,
            retained_frames=len(samples), sample_fps=1.5, max_candidates=120,
            method="existing OpenCV quality/novelty sampler; full-duration traversal",
            day=day, sample_timestamps=[s.timestamp_seconds for s in samples]))
        for sample in samples:
            fid = f"{mid}:frame:{sample.frame_index}"
            frame_path = out / "sampled_frames" / (mid + "_" + str(sample.frame_index) + ".png")
            frame_path.parent.mkdir(exist_ok=True)
            cv2.imwrite(str(frame_path), sample.frame)
            manifests[index].append(dict(media_id=fid, job_id=jobs[index], name=frame_path.name,
                day=day, captured_at=None, media_type="video_frame", provenance="derived from " + mid,
                parent_media_id=mid, source_sha256=digest, frame_index=sample.frame_index,
                source_timestamp_seconds=sample.timestamp_seconds, availability="derived"))
            paths[index][fid] = frame_path
    for index in (0, 1):
        for m in manifests[index]:
            if m["media_id"] in paths[index]:
                m["sha256"] = hashlib.sha256(paths[index][m["media_id"]].read_bytes()).hexdigest()
    write_json(out / "video_sampling.json", video_metrics)
    # Explicit controlled manual annotations. No inferred component totals/acceptance.
    annotations = {
        "1000051368.jpg": ("roof_baseline", "main_upper_roof", "Exposed pre-install roof baseline and staged materials."),
        "1000051465.jpg": ("insulation", "main_upper_roof", "Insulation boards visibly placed across the roof field; exact plan reconciliation unresolved."),
        "1000051505.jpg": ("membrane", "main_upper_roof", "White membrane field visibly covers the previously exposed upper-roof area; hidden layers not established."),
        "1000051512.jpg": ("wall_connection", "main_upper_roof_perimeter", "Metal restraint profile and visible fasteners along roof-side upstand; governing detail unresolved."),
        "1000051522.jpg": ("drain", "main_upper_roof", "Drain opening and loose ring/fitting visible during detail integration."),
        "1000051531.jpg": ("drain", "main_upper_roof", "Circular drain/interface visible in membrane; final recess geometry unresolved."),
        "1000051975.jpg": ("membrane", "lower_wallside_roof", "Membrane coverage visible along lower wall-side roof zone."),
        "1000051985.jpg": ("wall_connection", "lower_wallside_roof", "Wall-base termination profiles visible; concealed fixation and sealing unresolved."),
        "1000051988.jpg": ("overflow", "lower_courtyard_roof", "Rectangular wall outlet visible; project component identity and exact trim unresolved."),
        "1000051989.jpg": ("drain", "lower_courtyard_roof", "Circular opening and surrounding membrane/detail visible; dimensional acceptance unresolved."),
        "1000051994.jpg": ("penetration", "exterior_wall", "Pipe protrudes through wall opening; identity and final seal unresolved."),
        "1000052001.jpg": ("threshold", "lower_wallside_roof", "Coated threshold/interface visible at door; material identity and final workmanship require review."),
        "1000052097.jpg": ("roof_patch", "unresolved", "Suspected water entry point: central split/dark line in irregular patch. Actual leakage and work-order zone unresolved."),
        "1000052094.jpg": ("roof_patch", "unresolved", "Lifted/prepared edge near hand tool; conflict candidate, repair stage and zone unresolved."),
    }
    definitions = [
        [("anchor_arrow", "anchor", "visual", "Dokumentation der ASP muss auf dem Bild der Pfeil erkennbar sein welcher die Einschlagtiefe vorgibt", "Find job-bound anchor photo with arrow and component identity before concealment.", "covering_started"),
         ("anchor_material", "anchor", "partial", "Anschlagpunkte mit Alutrix eindichten, nicht Eurasol", "Reconcile sealing material and process against the exact anchor source.", None),
         ("drain", "drain", "partial", "Gullis bis OK Loos-Flansch vertiefen", "Bind drain before/during/after evidence and governing flange geometry.", None),
         ("overflow", "overflow", "partial", "Notüberläufe einritzen und auf 5cm abschneiden", "Verify outlet identity, trim detail and governing geometry using stored evidence.", None),
         ("wall", "wall_connection", "partial", "Wandanschluss gemäß beigefügtem Detail!", "Bind wall-interface evidence to the attached project detail.", None),
         ("seam", "seam_control", "nonvisual", "Nahtkontrolle!", "Reconcile the recorded seam inspection, operator and result; a seam photo cannot replace the check.", None),
         ("pv", "penetration", "partial", "Sind die PV Durchführungen gemacht? Sind die Leerrohre lang genug?", "Resolve penetration identity and conduit adequacy from project detail and human confirmation.", None),
         ("photo_delivery", "documentation", "nonvisual", "Vor Abfahrt und bevor die Baustelle beräumt wird müssen Fotos an den Bauleiter gesendet werden.", "Locate a delivery receipt/site-manager acknowledgement in the preserved record.", "completion")],
        [("gutter", "workshop_gutter", "partial", "Rinne zur Werkstatt abdichten und 2cm PU einsetzen und auf Blech hochziehen (Vorab prüfen, ob überhaupt Wasserspuren vorhanden sind)", "Bind workshop-gutter views; reconcile prior water-trace check, PU placement and sealed turn-up.", None),
         ("workshop_ridge", "workshop_ridge", "nonvisual", "Stöße in Verbundblech First auf Werkstatt prüfen", "Locate zone-bound joint-check outcome and responsible human record.", None),
         ("sales_ridge", "sales_ridge", "partial", "Blechstöße First auf Trapezblechdach über Verkaufsraum mit FLK abdichten", "Bind sales-room ridge patches to before/after evidence and exact FLK identity.", None),
         ("entrance", "entrance_connections", "partial", "Anschlüsse hinter Eingangsdach abdichten mit FLK", "Bind entrance-roof connection evidence to the annotated project area.", None)] ]
    store = PersistentJobLoop(out / "annotation_build.sqlite")
    chronological = PersistentJobLoop(out / "job_progress.sqlite")
    summaries = []
    for index, job in enumerate(jobs):
        name_to_id = {m["name"]: m["media_id"] for m in manifests[index]}
        primary_name = "stage0_prejob_001_1000051280.jpg" if index == 0 else "1000052052.jpg"
        primary_id = name_to_id[primary_name]
        record = JobEvidenceRecord(job, "6956" if index == 0 else "20266878", "persistent-job-contract", "0.2",
            "installation" if index == 0 else "service_inspection", [primary_id],
            {"classification_method": "manual_original_work_order_review", "component_quantities": "unresolved",
             "governing_installed_variant": "unresolved", "professional_acceptance": "pending"})
        frozen = sorted(manifests[index], key=lambda m:(m["day"] is None, m["day"] or 0, m["media_id"]))
        write_json(out / (f"trial00{index+1}_manifest.json"), frozen)
        store.create(record, frozen)
        for rid, component, checkability, excerpt, question, deadline in definitions[index]:
            req = dict(requirement_id=rid, name=component, requirement_statement=excerpt,
                source=dict(source_id=primary_id, source_kind="work_order", document_name=primary_name,
                    locator="highlighted task/instruction line", excerpt=excerpt),
                evidence_question=question, visual_checkability=checkability, required=True,
                capture_before_stage=deadline)
            store.append(job, "requirement:" + rid, "requirement", dict(requirement=req,
                component=component, zone="unresolved", authority="work_order"), day=0)
        for m in frozen:
            mid, name = m["media_id"], m["name"]
            if mid in paths[index]:
                store.measure_image(job, mid, paths[index][mid])
            if name in annotations:
                component, zone, statement = annotations[name]
                oid = "observation:" + mid
                store.append(job, oid, "observation", dict(media_id=mid, actor="PeakLogic",
                    method="manual_visual_annotation", component=component, zone=zone, statement=statement), day=m["day"])
                store.append(job, "progress:" + mid, "progress", dict(component=component,
                    zone=zone, status="visible_progress_observed" if index == 0 else "conflict_candidate_observed",
                    actor="PeakLogic", method="manual_visual_annotation", source_ids=[mid]), day=m["day"])
                for rid, req_component, *_ in definitions[index]:
                    if component == req_component:
                        store.append(job, "link:" + rid + ":" + mid, "link", dict(requirement_id=rid,
                            observation_id=oid, status="uncertain", modality="visual", human_confirmed=False), day=m["day"])
        if index == 0:
            # This concern is an unresolved field-review evidence question, not a new manufacturer rule.
            r = dict(requirement_id="substrate_readiness_review", name="substrate readiness review",
                requirement_statement="Archived field review records unresolved readiness/dryness before later membrane concealment; governing criterion unresolved.",
                source=dict(source_id=source_ids[2], source_kind="human_confirmation", document_name="Running field review",
                    locator="DAY 1 / DAY 2", excerpt="Surface readiness / objective dryness was not conclusively documented before later concealment."),
                evidence_question="Reconcile any preserved pre-cover readiness record; otherwise retain the review gap.",
                visual_checkability="nonvisual", required=False, capture_before_stage="covering_started")
            store.append(job, "requirement:substrate_readiness_review", "requirement", dict(requirement=r,
                component="substrate", zone="main_upper_roof", authority="unresolved"), day=0)
            # Replay an attributed chronology from the preserved daily review, separately from fresh CV.
            stories = [(1, "setup", "mobilization_and_preinstall_baseline", source_ids[0]),
                (2, "insulation", "installation_in_progress", source_ids[1]),
                (3, "membrane", "upper_roof_field_coverage_observed", source_ids[2]),
                (4, "perimeter", "detail_and_exterior_work_in_progress", source_ids[2]),
                (5, "membrane", "secondary_roof_installation_in_progress", source_ids[2]),
                (6, "interfaces", "lower_roof_threshold_drain_wall_work_in_progress", source_ids[2])]
            for day, component, status, source in stories:
                store.append(job, "day-summary:" + str(day), "observation", dict(media_id=source,
                    actor="PeakLogic archived field review", method="source_report_annotation",
                    component=component, zone="reported_zone_not_surveyed", statement=status), day=day)
                store.append(job, "day-progress:" + str(day), "progress", dict(component=component,
                    status=status, actor="PeakLogic archived field review", method="source_report_annotation",
                    source_ids=[source]), day=day)
                if day == 3:
                    store.append(job, "concealment:substrate", "concealment", dict(component="substrate",
                        actor="PeakLogic manual day/scene comparison", source_ids=[name_to_id["1000051505.jpg"], name_to_id["1000051465.jpg"]]), day=3)
            store.append(job, "field-record-closed", "close_record", dict(source_ids=[source_ids[3]]), day=6)
        ordered = sorted(store.events(job), key=lambda e:(e["day"] is None, e["day"] or 0, e["seq"]))
        for e in ordered:
            chronological.append(job, e["event_id"], e["kind"], e["payload"], day=e["day"], captured_at=e["captured_at"])
        state = chronological.report(job)
        prefix = f"trial00{index+1}"
        write_json(out / (prefix + "_state.json"), state)
        (out / (prefix + "_report.md")).write_text(render_report(state))
        events = chronological.events(job)
        write_json(out / (prefix + "_events.json"), {"job_id": job, "events": events})
        (out / (prefix + "_trace.jsonl")).write_text("".join(json.dumps(e, ensure_ascii=False) + "\n" for e in events))
        for day in range(1, 7 if index == 0 else 2):
            daily = chronological.report(job, through_day=day, from_day=day)
            (out / (prefix + f"_day{day:02d}.md")).write_text(render_report(daily))
        (out / (prefix + "_week01.md")).write_text(render_report(chronological.report(job, from_day=1, through_day=6 if index == 0 else 1)))
        photos = [m for m in frozen if m["media_type"] == "photo"]
        hashes = {state["quality"][m["media_id"]]["sha256"] for m in photos}
        summaries.append(dict(job_id=job, original_photo_entries=len(photos), unique_photo_bytes=len(hashes),
            decoded_photos=sum(state["quality"][m["media_id"]]["decoded"] for m in photos),
            quality_failures=[dict(name=m["name"], **state["quality"][m["media_id"]]) for m in photos if not state["quality"][m["media_id"]]["metrics"]["usable"]],
            excluded_irrelevant=[m["name"] for m in photos if m.get("relevant") is False],
            exception_history=state["exception_history"], event_count=len(events),
            unavailable_sources=[m for m in frozen if m["availability"] == "raw_not_located"]))
    a = next(paths[0][m["media_id"]] for m in manifests[0] if m["name"] == "1000051368.jpg")
    b = next(paths[0][m["media_id"]] for m in manifests[0] if m["name"] == "1000051465.jpg")
    scene = analyze_scene_association(cv2.imread(str(a)), cv2.imread(str(b))).to_dict()
    write_json(out / "scene_continuity.json", dict(pair=["1000051368.jpg", "1000051465.jpg"],
        opencv_version=cv2.__version__, metrics=scene, conclusion="uncalibrated scene-continuity support; no automatic zone binding"))
    write_json(out / "execution_summary.json", dict(opencv_version=cv2.__version__, jobs=summaries))
    store.close()
    chronological.close()
    # Independently reopen and replay into another database, comparing logical state.
    verify = PersistentJobLoop(out / "replay_check.sqlite")
    checks = []
    for index, job in enumerate(jobs):
        packet = json.loads((out / f"trial00{index+1}_events.json").read_text())
        for e in packet["events"]:
            verify.append(job, e["event_id"], e["kind"], e["payload"], day=e["day"], captured_at=e["captured_at"])
        expected = json.loads((out / f"trial00{index+1}_state.json").read_text())
        actual = verify.report(job)
        # Ingest timestamps document this replay, and cannot be identical to original ingestion.
        for s in (expected, actual):
            for o in s["observations"].values(): o.pop("ingested_at", None)
            for group in (s["period_observations"], s["unresolved_bindings"]):
                for o in group: o.pop("ingested_at", None)
        assert json.dumps(actual, sort_keys=True) == json.dumps(expected, sort_keys=True)
        checks.append(dict(job_id=job, reload_and_fresh_replay_equal=True, event_count=len(packet["events"])))
    verify.close()
    write_json(out / "replay_verification.json", checks)


if __name__ == "__main__":
    main()
