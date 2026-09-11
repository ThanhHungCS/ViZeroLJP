from __future__ import annotations

import json
import re
from typing import TypeVar

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_ollama import ChatOllama
from langchain_openai import ChatOpenAI
from pydantic import BaseModel

from .config import Settings
from .schemas import DispositionAssessment, LJPLabelPrediction

T = TypeVar("T", bound=BaseModel)


def _json(value: object) -> str:
    return json.dumps(value, ensure_ascii=False, indent=2)


class LegalAgents:
    """Structured-output LLM calls used by ViZeroLJP."""

    def __init__(self, settings: Settings) -> None:
        self.structured_method = settings.llm_structured_method
        self.provider = settings.llm_provider
        if self.provider == "ollama":
            ollama_url = settings.llm_base_url.removesuffix("/v1").rstrip("/")
            self.chat = ChatOllama(
                model=settings.llm_model,
                base_url=ollama_url,
                temperature=settings.llm_temperature,
                reasoning=False,
                num_predict=settings.llm_max_tokens,
                client_kwargs={"timeout": settings.llm_timeout_seconds},
            )
        elif self.provider == "groq":
            self.chat = ChatOpenAI(
                model=settings.llm_model,
                base_url="https://api.groq.com/openai/v1",
                api_key=settings.groq_api_key,
                temperature=settings.llm_temperature,
                timeout=settings.llm_timeout_seconds,
                max_tokens=settings.llm_max_tokens,
                max_retries=2,
            )
        else:
            self.chat = ChatOpenAI(
                model=settings.llm_model,
                base_url=settings.llm_base_url,
                api_key=settings.llm_api_key,
                temperature=settings.llm_temperature,
                timeout=settings.llm_timeout_seconds,
                max_tokens=settings.llm_max_tokens,
                max_retries=2,
            )

    def _invoke(self, schema: type[T], system: str, payload: object) -> T:
        system = (
            "Luôn phân tích và viết nội dung bằng tiếng Việt. Chỉ giữ nguyên tiếng Anh "
            "cho identifier hoặc nhãn bắt buộc như A_WIN/B_WIN.\n\n" + system
        )
        if self.provider == "ollama":
            runnable = self.chat.with_structured_output(schema, method="json_schema")
            result = runnable.invoke(
                [SystemMessage(content=system), HumanMessage(content=_json(payload))]
            )
            return result if isinstance(result, schema) else schema.model_validate(result)

        if self.structured_method == "json_schema":
            runnable = self.chat.with_structured_output(schema, method="json_schema")
            result = runnable.invoke(
                [SystemMessage(content=system), HumanMessage(content=_json(payload))]
            )
            return result if isinstance(result, schema) else schema.model_validate(result)

        schema_json = _json(schema.model_json_schema())
        instruction = f"""{system}

QUAN TRỌNG: Chỉ trả về đúng MỘT JSON object, không markdown, không giải thích ngoài
JSON. JSON phải tuân thủ chính xác schema sau; không đổi tên field và không thêm field:
{schema_json}"""
        messages = [
            SystemMessage(content=instruction),
            HumanMessage(content=_json(payload)),
        ]
        last_error: Exception | None = None
        for _ in range(3):
            response = self.chat.invoke(
                messages,
                response_format={"type": "json_object"},
            )
            content = response.content
            if isinstance(content, list):
                content = "".join(
                    str(part.get("text", "")) if isinstance(part, dict) else str(part)
                    for part in content
                )
            text = str(content).strip()
            fenced = re.search(r"```(?:json)?\s*(\{.*\})\s*```", text, re.DOTALL)
            if fenced:
                text = fenced.group(1)
            try:
                return schema.model_validate(json.loads(text))
            except (json.JSONDecodeError, ValueError) as error:
                last_error = error
                messages.extend(
                    [
                        response,
                        HumanMessage(
                            content=(
                                "Output trước sai schema. Hãy sửa và chỉ trả JSON đúng schema. "
                                f"Validation error: {error}"
                            )
                        ),
                    ]
                )
        raise ValueError(f"LLM không trả được {schema.__name__} hợp lệ: {last_error}")

    def extract_disposition(
        self,
        case_description: str,
        evidence: list[dict[str, object]],
        laws: list[dict[str, object]] | None = None,
    ) -> DispositionAssessment:
        compact_laws = [
            {**item, "content": str(item.get("content", ""))[:500]}
            for item in (laws or [])[:5]
        ]
        return self._invoke(
            DispositionAssessment,
            """Bạn là agent trích xuất PHÁN QUYẾT, không phải luật sư tranh luận.
Chỉ xét yêu cầu chính được mô tả trong case_description và ưu tiên các đoạn
processed_case_segments được tách từ case_fact. Law
context chỉ dùng để hiểu quan hệ pháp luật, căn cứ và phạm vi yêu cầu; không dùng
law context để đoán kết quả nếu processed_case_segments không cho biết Tòa thực tế
xử thế nào. Phân biệt quyết định của Tòa với lời khai đương sự hoặc đề nghị của Viện kiểm
sát. Nếu có cả quyết định sơ thẩm và phúc thẩm, ưu tiên quyết định cuối cùng.

So sánh cụ thể phần nguyên đơn yêu cầu với phần Tòa thực tế chấp nhận, gồm số tiền,
diện tích, tài sản và các yêu cầu thành phần. ALL chỉ khi chấp nhận đúng 100%;
MAJORITY khi trên 50% nhưng dưới 100%; MINORITY khi trên 0% đến 50%; NONE khi bác
toàn bộ. Nếu evidence không đủ để so sánh, claim_scope=UNCLEAR và tạo tối đa 2
followup_queries bằng cụm từ tiếng Việt có thể xuất hiện trong phần QUYẾT ĐỊNH.

decisive_chunk_ids chỉ được chứa ID có trong evidence. Không dự đoán theo luật hoặc
theo bên nào có vẻ hợp lý. Trả đúng schema JSON.""",
            {
                "case_description": case_description,
                "processed_case_segments": evidence,
                "law_context": compact_laws,
            },
        )

    def predict_ljp_label(
        self,
        case_fact: str,
        laws: list[dict[str, object]] | None = None,
        processed_input: dict[str, object] | None = None,
    ) -> LJPLabelPrediction:
        compact_laws = [
            {**item, "content": str(item.get("content", ""))[:700]}
            for item in (laws or [])[:8]
        ]
        return self._invoke(
            LJPLabelPrediction,
            """Bạn là hệ thống dự đoán kết quả vụ án dân sự Việt Nam theo thiết lập
zero-shot. Không dùng ví dụ có nhãn và không được giả định thông tin ngoài input.

Quy ước nhãn:
- A_WIN: Tòa chấp nhận toàn bộ yêu cầu chính của phía nguyên đơn A.
- PARTIAL_A_WIN: Tòa chấp nhận một phần lớn hơn 50% yêu cầu chính của A.
- PARTIAL_B_WIN: Tòa chỉ chấp nhận một phần không quá 50% yêu cầu chính của A.
- B_WIN: Tòa bác toàn bộ yêu cầu chính của A, tức phía bị đơn B thắng.

Nếu có legal_context, chỉ dùng nó để hiểu căn cứ pháp lý, không dùng để bịa kết quả.
Không trình bày suy luận từng bước. explanation tối đa 160 ký tự.
Trả đúng schema JSON.""",
            {
                "case_fact": case_fact,
                "legal_context": compact_laws,
                "processed_input": processed_input or {},
            },
        )
