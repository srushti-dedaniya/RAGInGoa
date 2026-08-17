from rag.chunking.chunk_manager import ChunkManager


def test_fixed_size_splitter_bounds():
    docs = [{"content": "word " * 400, "metadata": {"id": "d1"}}]
    chunks = ChunkManager("fixed", {"size": 200, "overlap": 40}).split(docs)
    assert len(chunks) > 1
    assert all(len(c.text) <= 200 for c in chunks)
    assert all(c.chunk_id.startswith("d1-") for c in chunks)


def test_sentence_splitter_keeps_sentences_whole():
    text = (
        "Palolem is a crescent bay. The best time to visit is between November "
        "and February. The sea stays calm and swimmable. "
        "Dudhsagar Falls is reachable by jeep. "
    )
    docs = [{"content": text, "metadata": {"id": "d1"}}]
    chunks = ChunkManager("sentence", {"size": 120}).split(docs)
    assert len(chunks) >= 2
    assert all(c.text.strip().endswith((".", "!")) for c in chunks)


def test_semantic_splitter_breaks_on_coherence():
    docs = [
        {
            "content": (
                "Palolem is a crescent bay in South Goa. The water is calm and "
                "clean through winter. Electric scooters cost about 400 rupees a day. "
                "Buses connect the major towns and beaches."
            ),
            "metadata": {"id": "d1"},
        }
    ]
    chunks = ChunkManager("semantic", {"size": 500}).split(docs)
    assert len(chunks) >= 2


def test_metadata_aware_prefixes_titles():
    docs = [{"content": "A beach shack meal is a signature Goa experience.", "metadata": {"id": "d1", "title": "Goa Food Primer"}}]
    chunks = ChunkManager("metadata", {"inner": "sentence"}).split(docs)
    assert len(chunks) == 1
    assert "Goa Food Primer" in chunks[0].text
    assert chunks[0].metadata.get("prefixed") is True


def test_unknown_strategy_raises():
    try:
        ChunkManager("does-not-exist")
    except ValueError:
        return
    raise AssertionError("expected ValueError for unknown strategy")