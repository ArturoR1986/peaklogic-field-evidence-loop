"""Bounded fresh-image evaluation using the existing PersistentJobLoop.

Original media stays outside Git. This creates an isolated derived evaluation,
not a new authoritative field record. It never dispatches an action or accepts work.
"""
from __future__ import annotations
import argparse
from dataclasses import asdict
import hashlib
import json
from pathlib import Path
import subprocess
import sys
from typing import Any

import cv2
from peaklogic_field_evidence.job_packet import JobEvidenceRecord
from peaklogic_field_evidence.job_progress import PersistentJobLoop
from peaklogic_field_evidence.job_progress_cli import render_report
from peaklogic_field_evidence.runtime import require_opencv5


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def json_bytes(value: Any) -> bytes:
    return (json.dumps(value, sort_keys=True, indent=2, ensure_ascii=False, allow_nan=False) + '\n').encode()


def write_json(path: Path, value: Any) -> None:
    path.write_bytes(json_bytes(value))


def check_runtime() -> dict:
    info = require_opencv5()
    if info.opencv_version != '5.0.0' or not info.has_dnn or not info.has_img_hash:
        raise RuntimeError('This experiment requires the pinned OpenCV 5.0.0 runtime and contrib modules.')
    return asdict(info)


def validate_inputs(case: dict, root: Path) -> dict[str, Path]:
    """Complete preflight before creating or touching a database/output directory."""
    root = root.resolve(strict=True)
    found: dict[str, Path] = {}
    names: set[str] = set()
    for item in case['inputs']:
        name, mid = item['filename'], item['media_id']
        relative = Path(name)
        if relative.is_absolute() or '..' in relative.parts or not mid:
            raise ValueError('Unsafe input path or empty media identity')
        if mid in found or name in names:
            raise ValueError('Duplicate input identity or filename')
        path = (root / relative).resolve(strict=True)
        if not path.is_relative_to(root) or not path.is_file():
            raise ValueError('Input escapes the authorized root or is not a file')
        if path.stat().st_size != item['bytes'] or path.stat().st_size > 10 * 1024 * 1024:
            raise ValueError('Input size mismatch or input exceeds 10 MiB')
        if digest(path.read_bytes()) != item['sha256']:
            raise ValueError('Input SHA-256 mismatch: ' + name)
        found[mid] = path
        names.add(name)
    if case['requirement']['source']['source_id'] not in found:
        raise ValueError('Work-order source is not bound')
    if not case.get('field_capture_closed'):
        raise ValueError('This bounded runner is for the preserved closed Trial 001 record')
    return found


def require(value: bool, message: str) -> None:
    if not value:
        raise AssertionError(message)


def invoke_report(db: Path, job_id: str, prefix: Path) -> dict:
    command = [sys.executable, '-m', 'peaklogic_field_evidence.job_progress_cli',
               'report', '--db', str(db), '--job-id', job_id, '--output', str(prefix)]
    result = subprocess.run(command, capture_output=True, text=True, check=False)
    prefix.with_suffix('.log').write_text('$ ' + ' '.join(command) + '\n' + result.stdout + result.stderr)
    require(result.returncode == 0, 'Separate-process report failed; see reload log')
    return json.loads(prefix.with_suffix('.json').read_text())


def run_case(case_path: Path, input_dir: Path, output_dir: Path) -> dict:
    runtime = check_runtime()
    case_raw = case_path.read_bytes()
    case = json.loads(case_raw)
    paths = validate_inputs(case, input_dir)
    # A new directory is mandatory: never append experimental events to live state.
    output_dir.mkdir(parents=True, exist_ok=False)
    write_json(output_dir / 'case.json', case)
    job_id = 'EVAL-' + case['case_id']
    record = JobEvidenceRecord(job_id, case['work_order_id'], 'field-readiness-evaluation', '1',
        'installation', [case['requirement']['source']['source_id']],
        extracted_context={'source_job_id': case['source_job_id'], 'evaluation_only': True,
            'case_sha256': digest(case_raw), 'historical_job_mutated': False,
            'chronology': 'Attributed day ordinals, not verified timestamps; current record is closed.'})
    manifest = [{**item, 'job_id': job_id, 'name': item['filename'],
                 'provenance': item['source_url']} for item in case['inputs']]
    manifest.append({'media_id': 'case-source', 'job_id': job_id, 'media_type': 'document',
                     'provenance': 'Derived case.json and its documented closure basis',
                     'sha256': digest(case_raw), 'day': 0})
    db = output_dir / 'job.sqlite'
    result: dict[str, Any] = {'status': 'RUNNING', 'case_id': case['case_id'], 'job_id': job_id,
        'source_job_id': case['source_job_id'], 'base_commit': case['base_commit'],
        'basis': 'Fresh OpenCV 5 on original field bytes; attributed requirement and observations; isolated retrospective evaluation.',
        'runtime': runtime, 'case_sha256': digest(case_raw),
        'runner_sha256': digest(Path(__file__).read_bytes()),
        'fresh_field_cv': True, 'aws_executed': False, 'historical_job_mutated': False,
        'checks': {}}
    store = PersistentJobLoop(db)
    try:
        store.create(record, manifest)
        store.append(job_id, 'requirement:P-07', 'requirement',
            {'requirement': case['requirement'], 'component': 'predeparture_photo_package',
             'zone': 'job-wide', 'authority': 'work_order'}, day=0)
        for obs in case['observations']:
            item = next(i for i in case['inputs'] if i['media_id'] == obs['media_id'])
            oid = 'observation:' + obs['media_id']
            store.append(job_id, oid, 'observation',
                {**obs, 'actor': 'Main Evidence Steward', 'component': 'predeparture_photo_package'},
                day=item['day'])
            store.append(job_id, 'link:' + obs['media_id'], 'link',
                {'requirement_id': 'P-07', 'observation_id': oid, 'status': 'uncertain',
                 'modality': 'visual', 'human_confirmed': False}, day=item['day'])
        store.append(job_id, 'record-closed', 'close_record',
            {'source_ids': ['case-source'], 'reason': case['closure_basis']}, day=6)
        write_json(output_dir / 'before_quality.json', store.report(job_id))
        for item in case['inputs']:
            if item['media_type'] == 'photo':
                store.measure_image(job_id, item['media_id'], paths[item['media_id']])
        state = store.report(job_id)
        photos = [i for i in case['inputs'] if i['media_type'] == 'photo']
        require(len(photos) == 2, 'This case expects two original candidate photos')
        clear, blurred = photos[0]['media_id'], photos[1]['media_id']
        require(state['quality'][clear]['next_action'] == 'continue_review', 'Clear-photo expectation failed')
        require(state['quality'][blurred]['next_action'] == 'record_quality_exception', 'Blurred closed-record expectation failed')
        require(state['component_decisions'][0]['next_action']['action'] == 'escalate_human', 'Missing transmission proof must escalate')
        require(state['component_decisions'][0]['status'] != 'supported', 'Image quality cannot establish dispatch')
        require(state['professional_acceptance']['status'] == 'pending', 'Acceptance must remain pending')
        result['checks']['quality_action_and_nonacceptance'] = 'PASS'
        before = store.events(job_id)
        # Same-source remeasurement must not duplicate events.
        for item in photos:
            store.measure_image(job_id, item['media_id'], paths[item['media_id']])
        require(store.events(job_id) == before, 'Remeasurement duplicated or changed events')
        result['checks']['idempotent_remeasurement'] = 'PASS'
        for label, mid, path in [('unbound', 'foreign-id', paths[clear]),
                                 ('wrong_hash', clear, paths[blurred])]:
            try:
                store.measure_image(job_id, mid, path)
            except ValueError:
                require(store.events(job_id) == before, label + ' failure mutated the record')
            else:
                raise AssertionError(label + ' was accepted')
            result['checks'][label + '_no_write'] = 'PASS'
        events = store.events(job_id)
        write_json(output_dir / 'state.json', state)
        trace = ''.join(json.dumps(e, ensure_ascii=False) + '\n' for e in events).encode()
        (output_dir / 'events.trace.jsonl').write_bytes(trace)
        revision = {'event_count': len(events), 'last_event_id': events[-1]['event_id'],
                    'state_sha256': digest(json_bytes(state)), 'trace_sha256': digest(trace)}
        result['revision'] = revision
        (output_dir / 'report.md').write_text(
            '# F02 derived evaluation — not the authoritative field report\n\n'
            + 'Source job: ' + case['source_job_id'] + '\n\n'
            + 'Saved state SHA-256: `' + revision['state_sha256'] + '`\n\n'
            + 'No action was dispatched. This does not prove the required photo set was sent.\n\n'
            + render_report(state), encoding='utf-8')
        result['photo_results'] = {i['filename']: state['quality'][i['media_id']] for i in photos}
        store.export_database(output_dir / 'job_export.sqlite')
    except Exception as exc:
        result.update(status='FAIL', error=type(exc).__name__ + ': ' + str(exc))
        raise
    finally:
        store.close()
        write_json(output_dir / 'result.json', result)
    try:
        reloaded = invoke_report(db, job_id, output_dir / 'reopened')
        exported = invoke_report(output_dir / 'job_export.sqlite', job_id, output_dir / 'export_reopened')
        expected = json.loads((output_dir / 'state.json').read_text())
        require(reloaded == expected == exported, 'Restart/export changed persisted state')
        result['checks']['separate_process_reopen'] = 'PASS'
        result['checks']['export_reopen'] = 'PASS'
        result['status'] = 'PASS'
    except Exception as exc:
        result.update(status='FAIL', error=type(exc).__name__ + ': ' + str(exc))
        raise
    finally:
        write_json(output_dir / 'result.json', result)
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--case', type=Path, required=True)
    parser.add_argument('--input-dir', type=Path, required=True)
    parser.add_argument('--output-dir', type=Path, required=True, help='New directory on durable storage')
    args = parser.parse_args()
    print(json.dumps(run_case(args.case, args.input_dir, args.output_dir), indent=2))


if __name__ == '__main__':
    main()
