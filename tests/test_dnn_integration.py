import numpy as np

from peaklogic_field_evidence.classifier import Classification, ProofPointClassifier
from peaklogic_field_evidence.orchestrator import EvidenceLoop
from peaklogic_field_evidence.schemas import ActionType
from peaklogic_field_evidence.templates import registry


class FixedClassifier(ProofPointClassifier):
    def __init__(self, label: str, confidence: float):
        self.result = Classification(
            label=label,
            confidence=confidence,
            raw_label=label,
            source="opencv_dnn",
        )

    def predict(self, image):
        return self.result


def usable_image():
    image = np.zeros((600, 800, 3), dtype=np.uint8)
    image[::2, ::2] = 255
    return image


def test_classifier_output_is_recorded_with_model_provenance():
    t = registry()[0]
    loop = EvidenceLoop(
        t,
        classifier=FixedClassifier("location_context", 0.98),
    )
    observation, action = loop.process_image(usable_image(), media_id="model-1")
    assert observation.proof_point_label == "location_context"
    assert observation.proof_point_source == "opencv_dnn"
    assert "location_context" in loop.state.accepted_proof_points
    assert action.action in {ActionType.CONTINUE, ActionType.REMIND_CRITICAL_PROOF}


def test_unsupported_classifier_output_cannot_satisfy_proof():
    t = registry()[0]
    loop = EvidenceLoop(
        t,
        classifier=FixedClassifier("unsupported", 0.99),
    )
    observation, action = loop.process_image(usable_image(), media_id="unknown-1")
    assert observation.proof_point_label == "unsupported"
    assert "unsupported" not in loop.state.accepted_proof_points
    assert action.action == ActionType.REQUEST_TARGETED_PROOF


def test_controlled_input_is_marked_as_controlled_not_model():
    t = registry()[0]
    loop = EvidenceLoop(t)
    observation, _ = loop.process_image(
        usable_image(),
        media_id="controlled-1",
        proof_point_label="location_context",
        proof_point_confidence=0.99,
    )
    assert observation.proof_point_source == "controlled_input"
