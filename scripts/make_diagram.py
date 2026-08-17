"""Generate the architecture pipeline diagram (docs/architecture/pipeline-diagram.png)."""

from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "docs" / "architecture" / "pipeline-diagram.png"

FONT = "libs"  # placeholder
FONT_PATH = "C:/Windows/Fonts/calibrib.ttf"
FONT_PATH_REG = "C:/Windows/Fonts/calibri.ttf"

BG = (253, 248, 248)
PRIMARY = (0, 81, 44)
PRIMARY_CONTAINER = (8, 107, 61)
TERTIARY = (140, 0, 70)
SURFACE = (255, 255, 255)
MUTED = (95, 101, 94)
YELLOW = (255, 214, 0)

STAGES = [
    ("VOICE IN", None, YELLOW),
    ("STT", "transcribe", SURFACE),
    ("QUERY WORKSPACE", "normalize", SURFACE),
    ("RETRIEVAL", "embed + top-k", SURFACE),
    ("RERANK", "re-order", SURFACE),
    ("GENERATION", "grounded answer", SURFACE),
    ("GUARDRAILS", "safety · relevance\n· grounding · refusal", SURFACE),
    ("GROUNDED\nANSWER", None, PRIMARY_CONTAINER),
]


def _font(size: int, bold: bool = True):
    path = FONT_PATH if bold else FONT_PATH_REG
    try:
        return ImageFont.truetype(path, size)
    except OSError:
        return ImageFont.load_default()


def main() -> int:
    OUT.parent.mkdir(parents=True, exist_ok=True)
    stage_w, stage_h = 150, 84
    gap = 26
    arrow_w = 40
    box_h = stage_h + 60
    n = len(STAGES)
    width = n * stage_w + (n - 1) * (gap + arrow_w) + 160
    height = box_h + 90

    img = Image.new("RGB", (width, height), BG)
    draw = ImageDraw.Draw(img)
    font_t = _font(16, True)
    font_s = _font(12, False)
    font_title = _font(26, True)

    text = "RAGInGoa Pipeline — Voice → RAG → Answer"
    draw.text((40, 18), text, fill=PRIMARY, font=font_title)

    x0 = 40
    y0 = 60
    for i, (label, sub, fill) in enumerate(STAGES):
        x = x0 + i * (stage_w + gap + arrow_w)
        color = PRIMARY_CONTAINER if fill == PRIMARY_CONTAINER else (
            YELLOW if fill == YELLOW else (0, 0, 0, 0)
        )
        if fill == SURFACE:
            draw.rounded_rectangle((x, y0, x + stage_w, y0 + stage_h), radius=10, fill=SURFACE, outline=PRIMARY, width=2)
        else:
            draw.rounded_rectangle((x, y0, x + stage_w, y0 + stage_h), radius=10, fill=(fill[0], fill[1], fill[2]), outline=PRIMARY, width=2)

        # label (multi-line safe)
        lx = x + stage_w / 2
        lines = label.split("\n")
        for li, line in enumerate(lines):
            w = draw.textlength(line, font=font_t)
            draw.text((lx - w / 2, y0 + stage_h / 2 - (8 if sub else 0) - 9 + li * 18), line, fill=PRIMARY if fill == SURFACE else (255, 255, 255), font=font_t)

        if sub:
            lw = draw.textlength(sub.replace("\n", " "), font=font_s)
            draw.text((lx - lw / 2, y0 + stage_h - 24), sub, fill=TERTIARY, font=font_s)

        # arrow
        if i < n - 1:
            ax = x + stage_w + 8
            ay = y0 + stage_h / 2
            draw.line((ax, ay, ax + arrow_w - 8, ay), fill=PRIMARY, width=3)
            draw.polygon([(ax + arrow_w, ay), (ax + arrow_w - 10, ay - 6), (ax + arrow_w - 10, ay + 6)], fill=PRIMARY)

    # annotation footer
    footer = "EVERY STAGE REPORTS ITS OWN LATENCY  ·  FAILURES DEGRADE GRACEFULLY  ·  LESS NOISE. MORE SIGNAL."
    fw = draw.textlength(footer, font=font_s)
    draw.text(((width - fw) / 2, y0 + stage_h + 34), footer, fill=MUTED, font=font_s)

    img.save(OUT)
    print(f"wrote {OUT}  ({width}x{height})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())