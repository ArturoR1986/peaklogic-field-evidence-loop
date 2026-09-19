from pathlib import Path

from peaklogic_field_evidence.templates import TEMPLATE_DIR, registry


def test_template_json_exists_in_installed_package():
    assert TEMPLATE_DIR.is_dir()
    assert list(Path(TEMPLATE_DIR).glob("*.json"))
    assert registry()
