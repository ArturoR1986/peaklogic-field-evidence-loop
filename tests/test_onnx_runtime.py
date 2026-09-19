import numpy as np
import onnx
from onnx import TensorProto, helper

from peaklogic_field_evidence.classifier import OpenCVDNNProofPointClassifier


def build_tiny_color_model(path):
    input_info = helper.make_tensor_value_info(
        "input", TensorProto.FLOAT, [1, 3, 16, 16]
    )
    output_info = helper.make_tensor_value_info(
        "output", TensorProto.FLOAT, [1, 3]
    )
    nodes = [
        helper.make_node("GlobalAveragePool", ["input"], ["pooled"]),
        helper.make_node("Flatten", ["pooled"], ["output"], axis=1),
    ]
    graph = helper.make_graph(nodes, "tiny_color_classifier", [input_info], [output_info])
    model = helper.make_model(
        graph,
        producer_name="peaklogic-ci-smoke",
        opset_imports=[helper.make_opsetid("", 13)],
        ir_version=8,
    )
    onnx.checker.check_model(model)
    onnx.save(model, path)


def test_real_onnx_model_loads_and_runs_through_opencv_dnn(tmp_path):
    model_path = tmp_path / "tiny.onnx"
    build_tiny_color_model(model_path)

    classifier = OpenCVDNNProofPointClassifier.from_onnx(
        model_path,
        labels=("channel_0", "channel_1", "channel_2"),
        input_size=(16, 16),
        confidence_threshold=0.0,
        swap_rb=False,
    )

    image = np.zeros((16, 16, 3), dtype=np.uint8)
    image[:, :, 0] = 255
    result = classifier.predict(image)

    assert result.source == "opencv_dnn"
    assert result.raw_label == "channel_0"
    assert result.label == "channel_0"
    assert result.confidence > 0.50
