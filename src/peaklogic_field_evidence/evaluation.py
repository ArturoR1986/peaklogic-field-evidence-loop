from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Sequence


@dataclass(frozen=True)
class ClassMetrics:
    precision: float
    recall: float
    f1: float
    support: int


@dataclass(frozen=True)
class ClassificationMetrics:
    labels: tuple[str, ...]
    confusion_matrix: tuple[tuple[int, ...], ...]
    per_class: dict[str, ClassMetrics]
    macro_f1: float
    accuracy: float


def classification_metrics(
    y_true: Sequence[str],
    y_pred: Sequence[str],
    *,
    labels: Sequence[str],
) -> ClassificationMetrics:
    if len(y_true) != len(y_pred):
        raise ValueError("y_true and y_pred must have equal length")
    labels = tuple(labels)
    if not labels:
        raise ValueError("labels are required")
    index = {label: i for i, label in enumerate(labels)}
    matrix = [[0 for _ in labels] for _ in labels]
    for truth, pred in zip(y_true, y_pred):
        if truth not in index or pred not in index:
            raise ValueError(f"unknown label pair: {truth!r}, {pred!r}")
        matrix[index[truth]][index[pred]] += 1

    per_class: dict[str, ClassMetrics] = {}
    for label, i in index.items():
        tp = matrix[i][i]
        fp = sum(matrix[row][i] for row in range(len(labels)) if row != i)
        fn = sum(matrix[i][col] for col in range(len(labels)) if col != i)
        support = sum(matrix[i])
        precision = tp / (tp + fp) if tp + fp else 0.0
        recall = tp / (tp + fn) if tp + fn else 0.0
        f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0.0
        per_class[label] = ClassMetrics(precision, recall, f1, support)

    total = len(y_true)
    correct = sum(matrix[i][i] for i in range(len(labels)))
    macro_f1 = sum(m.f1 for m in per_class.values()) / len(labels)
    return ClassificationMetrics(
        labels=labels,
        confusion_matrix=tuple(tuple(row) for row in matrix),
        per_class=per_class,
        macro_f1=float(macro_f1),
        accuracy=(correct / total if total else 0.0),
    )


def false_ready_rate(expected_complete: Sequence[bool], predicted_ready: Sequence[bool]) -> float:
    """Fraction of truly incomplete packets incorrectly marked ready."""
    if len(expected_complete) != len(predicted_ready):
        raise ValueError("inputs must have equal length")
    incomplete = [i for i, expected in enumerate(expected_complete) if not expected]
    if not incomplete:
        return 0.0
    false_ready = sum(1 for i in incomplete if predicted_ready[i])
    return false_ready / len(incomplete)


def missed_reminder_rate(expected_reminder: Sequence[bool], emitted_reminder: Sequence[bool]) -> float:
    """Fraction of situations needing a reminder where no reminder was emitted."""
    if len(expected_reminder) != len(emitted_reminder):
        raise ValueError("inputs must have equal length")
    required = [i for i, expected in enumerate(expected_reminder) if expected]
    if not required:
        return 0.0
    missed = sum(1 for i in required if not emitted_reminder[i])
    return missed / len(required)


def categorical_accuracy(expected: Sequence[str], actual: Sequence[str]) -> float:
    if len(expected) != len(actual):
        raise ValueError("inputs must have equal length")
    if not expected:
        return 0.0
    return sum(1 for a, b in zip(expected, actual) if a == b) / len(expected)
