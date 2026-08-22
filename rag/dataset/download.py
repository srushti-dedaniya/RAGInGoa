"""Reproducible MSMARCO-XI download and normalization pipeline."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Iterable


LANGUAGE_CODES = {
    "as": "asm_Beng",
    "bn": "ben_Beng",
    "gu": "guj_Gujr",
    "hi": "hin_Deva",
    "kn": "kan_Knda",
    "ml": "mal_Mlym",
    "mr": "mar_Deva",
    "or": "ory_Orya",
    "pa": "pan_Guru",
    "ta": "tam_Taml",
    "te": "tel_Telu",
}

LANGUAGE_FILES = {
    "as": "asm", "bn": "ben", "gu": "guj", "hi": "hin", "kn": "kan",
    "ml": "mal", "mr": "mar", "ne": "nep", "or": "ori", "pa": "pan",
    "sa": "san", "ta": "tam", "te": "tel", "ur": "urd",
}


def normalize_msmarco(
    records: Iterable[dict], language: str, split: str, limit: int | None = None,
    source_target_language: str | None = None,
):
    seen: set[str] = set()
    emitted = 0
    target_language = source_target_language or LANGUAGE_CODES.get(language, language)
    for row in records:
        if row.get("target_lang") != target_language:
            continue
        passages = row.get("passages") or {}
        translated = passages.get("Translated_passages") or []
        english = passages.get("English_passages") or []
        selected = passages.get("is_selected") or []
        for position, (translated_text, english_text) in enumerate(zip(translated, english)):
            content = str(english_text if language == "en" else (translated_text or english_text or "")).strip()
            if len(content) < 40 or content in seen:
                continue
            seen.add(content)
            qid = str(row.get("query_id", "unknown"))
            yield {"content": content, "metadata": {
                "id": f"msmarco-xi-{language}-{qid}-{position}", "source": "ai4bharat/MSMARCO-XI",
                "dataset": "MSMARCO-XI", "language": language, "split": split,
                "query_id": qid,
                "query": row.get("Eng_Query", "") if language == "en" else row.get("query", ""),
                "english_query": row.get("Eng_Query", ""),
                "answer": row.get("Eng_Answer", "") if language == "en" else row.get("Answer", ""),
                "english_answer": row.get("Eng_Answer", ""),
                "query_type": row.get("query_type", ""), "passage_position": position,
                "is_selected": bool(selected[position]) if position < len(selected) else False,
                "english_passage": english_text, "source_lang": row.get("source_lang", ""),
                "target_lang": row.get("target_lang", ""),
            }}
            emitted += 1
            if limit and emitted >= limit:
                return


def download_msmarco(out_file: Path, language: str, split: str, limit: int | None) -> int:
    try:
        from datasets import load_dataset
    except ImportError as exc:
        raise RuntimeError("Install the 'datasets' package to download MSMARCO-XI") from exc
    # XI is an Indic translation corpus. Its aligned English source is
    # materialized from the Hindi shard into a distinct English corpus/index.
    source_language = "hi" if language == "en" else language
    file_code = LANGUAGE_FILES.get(source_language)
    if not file_code:
        raise ValueError(f"Unsupported MSMARCO-XI language: {language}")
    split_suffix = "val" if split == "validation" else split
    data_file = (
        f"hf://datasets/ai4bharat/MSMARCO-XI/{split}/"
        f"{file_code}{split_suffix}.parquet"
    )
    dataset = load_dataset("parquet", data_files={split: data_file}, split=split, streaming=True)
    out_file.parent.mkdir(parents=True, exist_ok=True)
    count = 0
    with out_file.open("w", encoding="utf-8") as handle:
        source_target = LANGUAGE_CODES[source_language] if language == "en" else None
        for doc in normalize_msmarco(
            dataset, language, split, limit, source_target_language=source_target
        ):
            handle.write(json.dumps(doc, ensure_ascii=False) + "\n")
            count += 1
    if count == 0:
        raise RuntimeError("MSMARCO-XI produced no usable passages")
    return count


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Download and normalize ai4bharat/MSMARCO-XI")
    parser.add_argument("--language", default="en")
    parser.add_argument("--split", default="validation")
    parser.add_argument("--limit", type=int, default=5000, help="0 means all passages")
    parser.add_argument("--out", default=None)
    args = parser.parse_args(argv)
    out = args.out or f"rag/data/processed/msmarco_xi_{args.language}.jsonl"
    count = download_msmarco(Path(out), args.language, args.split, args.limit or None)
    print(f"normalized {count} MSMARCO-XI passages -> {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
