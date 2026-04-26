"""Insights service: field-level distribution stats and AI-powered qualitative analysis."""

from __future__ import annotations

import json
import logging
import statistics
from datetime import datetime, timezone
from typing import Any

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from ..models import Answer, Form, Submission
from ..schemas import (
    FieldAIInsight,
    FieldCategoricalStats,
    FieldDistribution,
    FieldNumericStats,
    FieldTextStats,
    FieldValueCount,
    FormAIInsightsResponse,
    FormFieldDistributionsResponse,
)

logger = logging.getLogger(__name__)

MODEL = "groq/llama-3.3-70b-versatile"

_CATEGORICAL_TYPES = {"select", "boolean"}
_NUMERIC_TYPES = {"number"}
_TEXT_TYPES = {"text", "email", "phone", "url", "date"}

# Module-level cache keyed by (form_id, total_answer_count).
# Multi-worker deployments may miss the cache for concurrent requests, but that
# causes at most N redundant LLM calls — acceptable for this deployment model.
_insights_cache: dict[tuple[str, int], FormAIInsightsResponse] = {}


# ---------------------------------------------------------------------------
# Field distributions (pure DB, no LLM)
# ---------------------------------------------------------------------------

def compute_field_distributions(db: Session, form: Form) -> FormFieldDistributionsResponse:
    total_submissions = int(
        db.scalar(select(func.count()).select_from(Submission).where(Submission.form_id == form.id)) or 0
    )

    fields_schema: list[dict[str, Any]] = form.fields_schema or []
    result_fields: list[FieldDistribution] = []

    for f_def in fields_schema:
        field_key: str = f_def.get("name", "")
        field_name: str = f_def.get("description") or field_key
        field_type: str = f_def.get("type", "text")

        if not field_key:
            continue

        # Fetch value counts from DB
        rows = db.execute(
            select(Answer.value_text, func.count().label("cnt"))
            .where(Answer.form_id == form.id, Answer.field_key == field_key)
            .group_by(Answer.value_text)
        ).all()

        total_responses = sum(r.cnt for r in rows)

        if field_type in _NUMERIC_TYPES:
            stats = _build_numeric_stats(field_key, field_name, field_type, rows, total_responses)
        elif field_type in _CATEGORICAL_TYPES:
            stats = _build_categorical_stats(field_key, field_name, field_type, rows, total_responses)
        else:
            stats = _build_text_stats(field_key, field_name, field_type, rows, total_responses)

        result_fields.append(FieldDistribution(
            field_key=field_key,
            field_name=field_name,
            field_type=field_type,
            stats=stats,
        ))

    return FormFieldDistributionsResponse(
        form_id=form.id,
        total_submissions=total_submissions,
        fields=result_fields,
    )


def _build_numeric_stats(
    field_key: str, field_name: str, field_type: str, rows: list, total: int
) -> FieldNumericStats:
    values: list[float] = []
    for row in rows:
        try:
            values.extend([float(row.value_text)] * int(row.cnt))
        except (ValueError, TypeError):
            pass

    parseable = len(values)
    if not values:
        return FieldNumericStats(
            field_key=field_key, field_name=field_name, field_type=field_type,
            count=total, parseable_count=0,
            min_val=None, max_val=None, avg_val=None, median_val=None,
            histogram=[],
        )

    values.sort()
    min_v = values[0]
    max_v = values[-1]
    avg_v = sum(values) / len(values)
    median_v = statistics.median(values)

    histogram = _build_histogram(values, min_v, max_v, buckets=5)

    return FieldNumericStats(
        field_key=field_key, field_name=field_name, field_type=field_type,
        count=total, parseable_count=parseable,
        min_val=round(min_v, 4), max_val=round(max_v, 4),
        avg_val=round(avg_v, 4), median_val=round(median_v, 4),
        histogram=histogram,
    )


def _build_histogram(values: list[float], min_v: float, max_v: float, buckets: int = 5) -> list[dict]:
    if min_v == max_v:
        return [{"bucket_label": str(min_v), "count": len(values)}]

    bucket_size = (max_v - min_v) / buckets
    counts = [0] * buckets
    for v in values:
        idx = min(int((v - min_v) / bucket_size), buckets - 1)
        counts[idx] += 1

    result = []
    for i in range(buckets):
        lo = min_v + i * bucket_size
        hi = min_v + (i + 1) * bucket_size
        result.append({
            "bucket_label": f"{_fmt_num(lo)}–{_fmt_num(hi)}",
            "count": counts[i],
        })
    return result


def _fmt_num(v: float) -> str:
    return str(int(v)) if v == int(v) else f"{v:.2f}"


def _build_categorical_stats(
    field_key: str, field_name: str, field_type: str, rows: list, total: int
) -> FieldCategoricalStats:
    sorted_rows = sorted(rows, key=lambda r: r.cnt, reverse=True)
    value_counts = [
        FieldValueCount(
            value=str(r.value_text),
            count=int(r.cnt),
            pct=round(100 * r.cnt / total, 1) if total else 0,
        )
        for r in sorted_rows
    ]
    return FieldCategoricalStats(
        field_key=field_key, field_name=field_name, field_type=field_type,
        total_responses=total,
        value_counts=value_counts,
    )


def _build_text_stats(
    field_key: str, field_name: str, field_type: str, rows: list, total: int
) -> FieldTextStats:
    sorted_rows = sorted(rows, key=lambda r: r.cnt, reverse=True)[:10]
    top_values = [
        FieldValueCount(
            value=str(r.value_text),
            count=int(r.cnt),
            pct=round(100 * r.cnt / total, 1) if total else 0,
        )
        for r in sorted_rows
    ]
    return FieldTextStats(
        field_key=field_key, field_name=field_name, field_type=field_type,
        total_responses=total,
        top_values=top_values,
    )


# ---------------------------------------------------------------------------
# AI insights (on-demand, cached)
# ---------------------------------------------------------------------------

def generate_ai_insights(db: Session, form: Form) -> FormAIInsightsResponse:
    total_answers = int(
        db.scalar(select(func.count()).select_from(Answer).where(Answer.form_id == form.id)) or 0
    )
    cache_key = (form.id, total_answers)
    if cache_key in _insights_cache:
        cached = _insights_cache[cache_key]
        return FormAIInsightsResponse(
            form_id=cached.form_id,
            generated_at=cached.generated_at,
            cached=True,
            field_insights=cached.field_insights,
            overall_summary=cached.overall_summary,
        )

    fields_schema: list[dict[str, Any]] = form.fields_schema or []
    text_fields = [f for f in fields_schema if f.get("type", "text") in {"text", "url"}]

    field_insights: list[FieldAIInsight] = []

    for f_def in text_fields:
        field_key = f_def.get("name", "")
        field_name = f_def.get("description") or field_key
        if not field_key:
            continue

        responses = db.execute(
            select(Answer.value_text)
            .where(Answer.form_id == form.id, Answer.field_key == field_key)
            .order_by(Answer.created_at.desc())
            .limit(50)
        ).scalars().all()

        if len(responses) < 3:
            continue

        insight = _call_llm_for_field(field_key, field_name, list(responses))
        field_insights.append(insight)

    overall_summary = _call_llm_for_overall(form.title, field_insights) if field_insights else (
        "Not enough text responses to generate an AI summary."
    )

    result = FormAIInsightsResponse(
        form_id=form.id,
        generated_at=datetime.now(timezone.utc).isoformat(),
        cached=False,
        field_insights=field_insights,
        overall_summary=overall_summary,
    )
    _insights_cache[cache_key] = result
    return result


def _call_llm_for_field(field_key: str, field_name: str, responses: list[str]) -> FieldAIInsight:
    sentinel = FieldAIInsight(
        field_key=field_key, field_name=field_name,
        summary="Unable to generate insight for this field.",
        themes=[], sentiment="neutral", notable_responses=[],
    )
    try:
        from litellm import completion  # type: ignore[import]

        joined = "\n".join(f"- {r}" for r in responses)
        prompt = (
            f'Field: "{field_name}" ({len(responses)} responses, showing up to 50)\n\n'
            f"{joined}\n\n"
            'Return JSON only: {"summary": "2-3 sentence summary", '
            '"themes": ["theme1", "theme2"], '
            '"sentiment": "positive|mixed|negative|neutral", '
            '"notable_responses": ["quote1", "quote2"]}'
        )
        resp = completion(
            model=MODEL,
            messages=[
                {"role": "system", "content": "You analyze qualitative form responses. Return valid JSON only, no markdown."},
                {"role": "user", "content": prompt},
            ],
            temperature=0.3,
            max_tokens=600,
        )
        raw = resp.choices[0].message.content or ""
        raw = raw.strip().removeprefix("```json").removeprefix("```").removesuffix("```").strip()
        data = json.loads(raw)
        return FieldAIInsight(
            field_key=field_key,
            field_name=field_name,
            summary=str(data.get("summary", "")),
            themes=[str(t) for t in data.get("themes", [])],
            sentiment=str(data.get("sentiment", "neutral")),
            notable_responses=[str(r) for r in data.get("notable_responses", [])[:3]],
        )
    except Exception as exc:
        logger.warning("AI insight generation failed for field %s: %s", field_key, exc)
        return sentinel


def _call_llm_for_overall(form_title: str, field_insights: list[FieldAIInsight]) -> str:
    try:
        from litellm import completion  # type: ignore[import]

        summaries = "\n".join(
            f'- {ins.field_name}: {ins.summary}' for ins in field_insights
        )
        prompt = (
            f'Form: "{form_title}"\n\nPer-field summaries:\n{summaries}\n\n'
            "Write a single cohesive paragraph (3-5 sentences) summarizing the overall "
            "patterns and insights across all responses. Return plain text only, no JSON."
        )
        resp = completion(
            model=MODEL,
            messages=[
                {"role": "system", "content": "You synthesize qualitative survey insights into clear, actionable summaries."},
                {"role": "user", "content": prompt},
            ],
            temperature=0.4,
            max_tokens=300,
        )
        return (resp.choices[0].message.content or "").strip()
    except Exception as exc:
        logger.warning("Overall AI summary generation failed: %s", exc)
        return "Unable to generate an overall summary at this time."
