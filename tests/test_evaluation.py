import pytest

from peaklogic_field_evidence.evaluation import (
    categorical_accuracy,
    classification_metrics,
    false_ready_rate,
    missed_reminder_rate,
)


def test_classification_metrics_known_confusion_matrix():
    result = classification_metrics(
        ["a", "a", "b", "b"],
        ["a", "b", "b", "b"],
        labels=("a", "b"),
    )
    assert result.confusion_matrix == ((1, 1), (0, 2))
    assert result.accuracy == pytest.approx(0.75)
    assert result.per_class["a"].recall == pytest.approx(0.5)
    assert result.per_class["b"].precision == pytest.approx(2 / 3)
    assert 0.0 <= result.macro_f1 <= 1.0


def test_false_ready_rate_only_uses_incomplete_packets():
    assert false_ready_rate(
        [False, False, True, False],
        [True, False, True, True],
    ) == pytest.approx(2 / 3)


def test_missed_reminder_rate():
    assert missed_reminder_rate(
        [True, True, False, True],
        [True, False, False, True],
    ) == pytest.approx(1 / 3)


def test_categorical_accuracy():
    assert categorical_accuracy(["retake", "continue"], ["retake", "wrong"]) == 0.5
