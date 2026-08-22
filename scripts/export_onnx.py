"""One-off export: all-MiniLM-L6-v2 -> ONNX int8 + tokenizer.json.

Run from repo root:  python scripts/export_onnx.py
"""

from __future__ import annotations

from pathlib import Path

import torch
from transformers import AutoModel, AutoTokenizer

OUT = Path(__file__).resolve().parents[1] / "rag" / "embeddings" / "onnx"
MODEL_ID = "sentence-transformers/all-MiniLM-L6-v2"


class Encoder(torch.nn.Module):
    def __init__(self, model) -> None:
        super().__init__()
        self.model = model

    def forward(self, input_ids, attention_mask):
        hidden = self.model(input_ids=input_ids, attention_mask=attention_mask, return_dict=False)[0]
        return hidden


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    tokenizer = AutoTokenizer.from_pretrained(MODEL_ID)
    model = AutoModel.from_pretrained(MODEL_ID).eval()
    encoder = Encoder(model).eval()

    dummy = tokenizer(["hello world"], return_tensors="pt")
    with torch.no_grad():
        torch.onnx.export(
            encoder,
            (dummy["input_ids"], dummy["attention_mask"]),
            str(OUT / "model_fp32.onnx"),
            input_names=["input_ids", "attention_mask"],
            output_names=["last_hidden_state"],
            dynamic_axes={
                "input_ids": {0: "batch", 1: "seq"},
                "attention_mask": {0: "batch", 1: "seq"},
                "last_hidden_state": {0: "batch", 1: "seq"},
            },
            opset_version=14,
            dynamo=False,
        )

    tokenizer.backend_tokenizer.save(str(OUT / "tokenizer.json"))

    from onnxruntime.quantization import QuantType, quantize_dynamic

    quantize_dynamic(
        str(OUT / "model_fp32.onnx"),
        str(OUT / "model.onnx"),
        weight_type=QuantType.QInt8,
    )
    (OUT / "model_fp32.onnx").unlink()

    sizes = {p.name: round(p.stat().st_size / 1e6, 1) for p in sorted(OUT.iterdir())}
    print("exported:", sizes)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
