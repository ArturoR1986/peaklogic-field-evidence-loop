from test_job_progress import setup_job, observation, quality, link
import pytest
import numpy as np
import cv2
from peaklogic_field_evidence.job_progress import PersistentJobLoop
from peaklogic_field_evidence.job_packet import JobEvidenceRecord
import json
import subprocess
import sys


def test_exported_database_reloads_in_separate_process(tmp_path):
    store = setup_job(tmp_path)
    quality(store, tmp_path)
    observation(store)
    link(store)
    expected = json.loads(json.dumps(store.report("job")))
    target = tmp_path / "exported.sqlite"
    store.export_database(target)
    store.close()
    process = subprocess.run([sys.executable, "-c",
        "import json,sys;from peaklogic_field_evidence.job_progress import PersistentJobLoop;"
        "s=PersistentJobLoop(sys.argv[1]);print(json.dumps(s.report('job')));s.close()",
        str(target)], capture_output=True, text=True, check=True)
    assert json.loads(process.stdout) == expected


def test_changed_source_bytes_fail_frozen_manifest_hash(tmp_path):
    store = PersistentJobLoop(tmp_path / "frozen.db")
    store.create(JobEvidenceRecord("job", "wo", "persistent", "0.2", "installation"),
        [dict(media_id="a", job_id="job", provenance="source", sha256="0" * 64)])
    path = tmp_path / "a.png"
    cv2.imwrite(str(path), np.full((400, 400, 3), 120, dtype=np.uint8))
    with pytest.raises(ValueError, match="frozen source hash"):
        store.measure_image("job", "a", path)
    assert len(store.events("job")) == 1
    assert not store.report("job")["quality"]


def test_zone_states_survive_later_work_in_other_zone(tmp_path):
    store = setup_job(tmp_path)
    for day, zone in [(2, "upper_roof"), (5, "lower_roof")]:
        store.append("job", "progress:" + zone, "progress", dict(component="membrane", zone=zone,
            status="installed_observed", actor="reviewer", method="manual_annotation", source_ids=["a"]), day=day)
    progress = store.report("job")["physical_progress"]
    assert progress["membrane@upper_roof"]["day"] == 2
    assert progress["membrane@lower_roof"]["day"] == 5


def test_retrospective_period_excludes_later_capture_and_holds_binding(tmp_path):
    store = setup_job(tmp_path)
    quality(store, tmp_path)
    observation(store, day=4, zone="unresolved")
    report = link(store)
    assert report["binding_actions"][0]["action"] == "escalate_human"
    assert not store.report("job", through_day=1)["observations"]


def test_out_of_order_physical_update_does_not_regress_progress(tmp_path):
    store = setup_job(tmp_path)
    for day, status in [(5, "installed_observed"), (2, "preparation_observed")]:
        store.append("job", "progress:" + str(day), "progress", dict(component="membrane", zone="roof",
            status=status, actor="reviewer", method="manual_annotation", source_ids=["a"]), day=day)
    assert store.report("job")["physical_progress"]["membrane@roof"]["day"] == 5
