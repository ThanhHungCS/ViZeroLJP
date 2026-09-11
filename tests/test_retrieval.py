from alqac_agent.retrieval import BM25Index, LawRetriever


def test_bm25_prefers_matching_document():
    index = BM25Index(
        [
            {"id": 1, "text": "bồi thường thiệt hại do súc vật gây ra"},
            {"id": 2, "text": "hợp đồng chuyển nhượng quyền sử dụng đất"},
        ],
        text_key="text",
    )
    assert index.search("trách nhiệm bồi thường do chó", 1)[0]["id"] == 1


def test_zero_match_returns_empty():
    index = BM25Index([{"id": 1, "text": "đất đai"}], text_key="text")
    assert index.search("xyzabc", 3) == []


def test_law_retriever_returns_law_payload():
    retriever = LawRetriever(
        [
            {"law_id": "L1", "aid": 1, "content": "bồi thường thiệt hại do súc vật gây ra"},
            {"law_id": "L2", "aid": 2, "content": "hợp đồng chuyển nhượng quyền sử dụng đất"},
        ]
    )
    results = retriever.search("trách nhiệm bồi thường do chó", 1)
    assert results[0]["law_id"] == "L1"
    assert results[0]["aid"] == 1
