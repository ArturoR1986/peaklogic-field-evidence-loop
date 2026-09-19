import numpy as np

from peaklogic_field_evidence.classifier import OpenCVDNNProofPointClassifier


class FakeNet:
    def __init__(self, output):
        self.output = np.asarray(output, dtype=np.float32)
        self.input_blob = None

    def setInput(self, blob):
        self.input_blob = blob

    def forward(self):
        return self.output


def test_dnn_adapter_returns_highest_softmax_label():
    net = FakeNet([[0.1, 4.0, -1.0]])
    classifier = OpenCVDNNProofPointClassifier(
        net=net,
        labels=("location_context", "critical_attachment", "unsupported"),
        input_size=(32, 32),
        confidence_threshold=0.60,
    )
    image = np.zeros((64, 64, 3), dtype=np.uint8)
    result = classifier.predict(image)
    assert result.label == "critical_attachment"
    assert result.raw_label == "critical_attachment"
    assert result.confidence > 0.90
    assert net.input_blob.shape == (1, 3, 32, 32)


def test_dnn_adapter_routes_low_confidence_to_unsupported():
    net = FakeNet([[0.0, 0.0]])
    classifier = OpenCVDNNProofPointClassifier(
        net=net,
        labels=("critical_attachment", "finished_context"),
        confidence_threshold=0.80,
    )
    result = classifier.predict(np.zeros((32, 32, 3), dtype=np.uint8))
    assert result.label == "unsupported"
    assert result.raw_label == "critical_attachment"
    assert 0.49 <= result.confidence <= 0.51


def test_dnn_adapter_rejects_output_shape_mismatch():
    net = FakeNet([[1.0, 2.0, 3.0]])
    classifier = OpenCVDNNProofPointClassifier(
        net=net,
        labels=("a", "b"),
    )
    try:
        classifier.predict(np.zeros((32, 32, 3), dtype=np.uint8))
    except ValueError as exc:
        assert "class count" in str(exc)
    else:
        raise AssertionError("shape mismatch should fail")
