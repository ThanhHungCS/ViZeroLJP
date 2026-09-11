from __future__ import annotations

import math
import re
from collections import Counter
from dataclasses import dataclass
from typing import Iterable

TOKEN_PATTERN = re.compile(r"[0-9a-zA-ZÀ-ỹĐđ]+", re.UNICODE)


def tokenize(text: str) -> list[str]:
    return TOKEN_PATTERN.findall(text.casefold())


@dataclass(slots=True)
class _Document:
    payload: dict[str, object]
    frequencies: Counter[str]
    length: int


class BM25Index:
    """Small dependency-free BM25 index suitable for the 3,352 law articles."""

    def __init__(
        self,
        payloads: Iterable[dict[str, object]],
        *,
        text_key: str,
        k1: float = 1.5,
        b: float = 0.75,
    ) -> None:
        self.k1 = k1
        self.b = b
        self.documents: list[_Document] = []
        document_frequency: Counter[str] = Counter()
        for payload in payloads:
            frequencies = Counter(tokenize(str(payload[text_key])))
            self.documents.append(
                _Document(payload=dict(payload), frequencies=frequencies, length=sum(frequencies.values()))
            )
            document_frequency.update(frequencies.keys())
        self.average_length = (
            sum(document.length for document in self.documents) / len(self.documents)
            if self.documents
            else 1.0
        )
        total = len(self.documents)
        self.idf = {
            token: math.log(1.0 + (total - frequency + 0.5) / (frequency + 0.5))
            for token, frequency in document_frequency.items()
        }

    def search(self, query: str, top_k: int) -> list[dict[str, object]]:
        query_terms = Counter(tokenize(query))
        scored: list[tuple[float, dict[str, object]]] = []
        for document in self.documents:
            score = 0.0
            normalization = self.k1 * (
                1 - self.b + self.b * document.length / self.average_length
            )
            for token, query_frequency in query_terms.items():
                term_frequency = document.frequencies.get(token, 0)
                if not term_frequency:
                    continue
                score += (
                    self.idf.get(token, 0.0)
                    * (term_frequency * (self.k1 + 1))
                    / (term_frequency + normalization)
                    * min(query_frequency, 2)
                )
            if score > 0:
                payload = dict(document.payload)
                payload["score"] = round(score, 6)
                scored.append((score, payload))
        scored.sort(key=lambda item: item[0], reverse=True)
        return [payload for _, payload in scored[:top_k]]


class LawRetriever:
    def __init__(self, articles: list[dict[str, object]]) -> None:
        self.index = BM25Index(articles, text_key="content")

    def search(self, query: str, top_k: int = 18) -> list[dict[str, object]]:
        return self.index.search(query, top_k)
