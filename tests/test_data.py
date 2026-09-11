import json

import pytest

from alqac_agent.data import load_cases, load_law_articles
from alqac_agent.schemas import DispositionAssessment, LJPLabelPrediction


def test_duplicate_cases_rejected(tmp_path):
    path = tmp_path / "cases.json"
    path.write_text(
        json.dumps(
            [
                {"case_id": "x", "case_fact": "q"},
                {"case_id": "x", "case_fact": "q2"},
            ]
        ),
        encoding="utf-8",
    )
    with pytest.raises(ValueError, match="trùng"):
        load_cases(path)


def test_law_schema(tmp_path):
    path = tmp_path / "laws.json"
    path.write_text(
        json.dumps(
            [{"law_id": "L", "content": [{"aid": 7, "content_Article": "Nội dung"}]}]
        ),
        encoding="utf-8",
    )
    assert load_law_articles(path) == [{"law_id": "L", "aid": 7, "content": "Nội dung"}]


def test_confidence_percentage_is_normalized():
    disposition = DispositionAssessment(
        claim_scope="ALL",
        confidence=98,
    )
    prediction = LJPLabelPrediction(
        prediction="A_WIN",
        explanation="Kết luận",
        confidence="85%",
    )
    assert disposition.confidence == 0.98
    assert prediction.confidence == 0.85


def test_confidence_can_be_omitted_by_model():
    disposition = DispositionAssessment(claim_scope="NONE")
    prediction = LJPLabelPrediction(
        prediction="B_WIN",
        explanation="Bác yêu cầu",
    )
    assert disposition.confidence == 0.5
    assert prediction.confidence == 0.5
