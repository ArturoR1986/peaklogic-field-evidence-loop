"""Synthetic preflight checks; these are not representative field-vision tests."""
from __future__ import annotations
import hashlib
import importlib.util
import json
from pathlib import Path

import pytest

MODULE_PATH = Path(__file__).resolve().parents[1] / 'scripts/run_field_readiness.py'
spec = importlib.util.spec_from_file_location('field_readiness_runner', MODULE_PATH)
runner = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(runner)


def make_case(tmp_path):
    path = tmp_path / 'synthetic_source.txt'
    path.write_bytes(b'synthetic preflight fixture; not field imagery')
    return {'field_capture_closed': True, 'inputs': [{'filename': path.name,
        'media_id': 'source', 'bytes': path.stat().st_size,
        'sha256': hashlib.sha256(path.read_bytes()).hexdigest()}],
        'requirement': {'source': {'source_id': 'source'}}}


def test_valid_input_preflight(tmp_path):
    case = make_case(tmp_path)
    assert runner.validate_inputs(case, tmp_path) == {'source': tmp_path / 'synthetic_source.txt'}


def test_hash_mismatch_is_rejected(tmp_path):
    case = make_case(tmp_path)
    case['inputs'][0]['sha256'] = '0' * 64
    with pytest.raises(ValueError, match='SHA-256'):
        runner.validate_inputs(case, tmp_path)


def test_size_mismatch_is_rejected(tmp_path):
    case = make_case(tmp_path)
    case['inputs'][0]['bytes'] += 1
    with pytest.raises(ValueError, match='size'):
        runner.validate_inputs(case, tmp_path)


@pytest.mark.parametrize('name', ['../escape.jpg', '/tmp/escape.jpg'])
def test_escaping_path_is_rejected(tmp_path, name):
    case = make_case(tmp_path)
    case['inputs'][0]['filename'] = name
    with pytest.raises(ValueError, match='Unsafe'):
        runner.validate_inputs(case, tmp_path)


def test_duplicate_media_identity_is_rejected(tmp_path):
    case = make_case(tmp_path)
    case['inputs'].append(dict(case['inputs'][0]))
    with pytest.raises(ValueError, match='Duplicate'):
        runner.validate_inputs(case, tmp_path)


def test_work_order_source_must_be_bound(tmp_path):
    case = make_case(tmp_path)
    case['requirement']['source']['source_id'] = 'unbound'
    with pytest.raises(ValueError, match='source is not bound'):
        runner.validate_inputs(case, tmp_path)


def test_closed_record_boundary_is_required(tmp_path):
    case = make_case(tmp_path)
    case['field_capture_closed'] = False
    with pytest.raises(ValueError, match='closed Trial'):
        runner.validate_inputs(case, tmp_path)


def test_missing_file_does_not_create_output(tmp_path):
    case = make_case(tmp_path)
    case['inputs'][0]['filename'] = 'missing.jpg'
    cp = tmp_path / 'case.json'
    cp.write_text(json.dumps(case))
    out = tmp_path / 'output'
    with pytest.raises(FileNotFoundError):
        runner.run_case(cp, tmp_path, out)
    assert not out.exists()


def test_symlink_outside_input_root_is_rejected(tmp_path):
    case = make_case(tmp_path)
    root = tmp_path / 'inputs'
    root.mkdir()
    (root / 'synthetic_source.txt').symlink_to(tmp_path / 'synthetic_source.txt')
    with pytest.raises(ValueError, match='escapes'):
        runner.validate_inputs(case, root)
