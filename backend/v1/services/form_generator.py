"""Form generation service — parses admin natural language prompt into
a structured form definition using OpenRouter (meta-llama/llama-3.3-70b-instruct).

This does NOT use the Agents SDK (no tools needed). It's a simple
LLM call that returns structured JSON.
"""

from __future__ import annotations

import json
import logging
import os
from dataclasses import dataclass

import litellm

logger = logging.getLogger(__name__)

# Bridge env var: our .env uses OPEN_ROUTER_API_KEY but LiteLLM expects OPENROUTER_API_KEY
if os.getenv("OPEN_ROUTER_API_KEY") and not os.getenv("OPENROUTER_API_KEY"):
    os.environ["OPENROUTER_API_KEY"] = os.getenv("OPEN_ROUTER_API_KEY", "")

GENERATION_SYSTEM_PROMPT = """You are an AI form architect. Given a user's description of what information they want to collect, you produce a structured form definition as JSON.

Your output must be valid JSON with this exact structure:
{
  "title": "Short form title",
  "description": "One-sentence description of the form's purpose",
  "system_prompt": "Instructions for the conversational agent that will conduct this form. Describe WHAT to collect, the TONE to use, any VALIDATION rules, and HOW to handle edge cases. Be specific and detailed.",
  "fields": [
    {
      "name": "field_name_snake_case",
      "type": "text|email|number|phone|url|date|select|boolean",
      "required": true,
      "description": "Human-readable description of this field"
    }
  ]
}

Rules:
1. Field names must be in snake_case (e.g. full_name, email_address).
2. Include 'type' based on the data (email for emails, phone for phone numbers, number for numeric values, etc.).
3. Mark fields as required=true unless the user explicitly says they're optional.
4. The system_prompt should be detailed instructions for a conversational AI agent — it should describe the persona, tone, what to collect, and any special handling.
5. Generate sensible defaults if the user's description is vague.
6. Output ONLY the JSON object, no markdown formatting, no explanation.
"""


@dataclass
class GeneratedFormField:
    name: str
    type: str
    required: bool
    description: str


@dataclass
class GeneratedForm:
    title: str
    description: str
    system_prompt: str
    fields: list[GeneratedFormField]


async def generate_form_from_prompt(prompt: str) -> GeneratedForm:
    """Use OpenRouter LLM to generate a structured form definition from a natural language prompt.

    Args:
        prompt: Admin's natural language description of what to collect.

    Returns:
        GeneratedForm with title, description, system_prompt, and fields.

    Raises:
        ValueError: If the LLM response cannot be parsed.
    """
    api_key = os.getenv("OPEN_ROUTER_API_KEY", "")

    response = await litellm.acompletion(
        model="openrouter/meta-llama/llama-3.3-70b-instruct",
        api_key=api_key,
        messages=[
            {"role": "system", "content": GENERATION_SYSTEM_PROMPT},
            {"role": "user", "content": prompt},
        ],
        temperature=0.3,  # Lower temp for more structured output
        max_tokens=2000,
    )

    raw = response.choices[0].message.content or ""
    raw = raw.strip()

    # Strip markdown code fences if present
    if raw.startswith("```"):
        lines = raw.split("\n")
        # Remove first and last lines (code fence markers)
        lines = [l for l in lines if not l.strip().startswith("```")]
        raw = "\n".join(lines)

    try:
        data = json.loads(raw)
    except json.JSONDecodeError as exc:
        logger.error("Failed to parse LLM response as JSON: %s\nRaw: %s", exc, raw[:500])
        raise ValueError(f"Failed to parse form generation response: {exc}") from exc

    fields = []
    for f in data.get("fields", []):
        fields.append(
            GeneratedFormField(
                name=f.get("name", "unknown"),
                type=f.get("type", "text"),
                required=f.get("required", True),
                description=f.get("description", ""),
            )
        )

    return GeneratedForm(
        title=data.get("title", "Untitled Form"),
        description=data.get("description", ""),
        system_prompt=data.get("system_prompt", ""),
        fields=fields,
    )
