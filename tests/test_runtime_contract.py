import pytest
from peaklogic_field_evidence.runtime import runtime_info, require_opencv5


def test_runtime_info_is_readable():
    info = runtime_info()
    assert info.opencv_major >= 4
    assert info.has_dnn


def test_competition_gate_matches_installed_major():
    info = runtime_info()
    if info.opencv_major == 5:
        assert require_opencv5().opencv_major == 5
    else:
        with pytest.raises(RuntimeError, match="requires OpenCV 5"):
            require_opencv5()
