from rag.evaluation.metrics import hit_at_k, mrrt, precision_at_k, recall_at_k


def test_precision_at_k():
    assert precision_at_k([True, False, True], 2) == 0.5
    assert precision_at_k([], 3) == 0.0


def test_recall_at_k():
    assert recall_at_k([True, False, False], 1, total_relevant=3) == 1 / 3
    assert recall_at_k([True, False, True], 3, total_relevant=2) == 1.0


def test_mrrt():
    assert mrrt([True, False]) == 1.0
    assert mrrt([False, True]) == 0.5
    assert mrrt([False, False]) == 0.0


def test_hit_at_k():
    assert hit_at_k([False, True], 2) is True
    assert hit_at_k([False, True], 1) is False


def test_answer_eval_grounded():
    from rag.evaluation.answer_eval import eval_answer

    answer = "Palolem is best visited between November and February. [Source: Palolem Beach Guide]"
    context = [
        {"text": "The best time to visit Palolem is between November and February.", "metadata": {"title": "Palolem Beach Guide"}}
    ]
    result = eval_answer(answer, context)
    assert result["passed"] is True
    assert result["cited_sources"] == ["Palolem Beach Guide"]