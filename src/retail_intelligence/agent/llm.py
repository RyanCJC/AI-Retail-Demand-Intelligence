
import json
import os
from pathlib import Path

from dotenv import load_dotenv
from openai import OpenAI


PROJECT_ROOT = Path(__file__).resolve().parents[3]

load_dotenv(PROJECT_ROOT / ".env")

GEMINI_BASE_URL = (
    "https://generativelanguage.googleapis.com/v1beta/openai/"
)

GEMINI_MODEL = os.getenv(
    "GEMINI_MODEL",
    "gemini-3.5-flash-lite",
)


def get_gemini_client() -> OpenAI:
    api_key = os.getenv("GEMINI_API_KEY")

    if not api_key:
        raise RuntimeError(
            "GEMINI_API_KEY was not found in the project .env "
            "file or environment variables."
        )

    return OpenAI(
        api_key=api_key,
        base_url=GEMINI_BASE_URL,
        timeout=60.0,
        max_retries=2,
    )


def generate_decision_explanation(
    assessment_context: dict,
) -> str:
    client = get_gemini_client()

    system_prompt = """
You are an AI retail inventory decision-support analyst.

Your task is to explain inventory assessment results to a retail
operations manager.

Rules:
1. Use only the supplied assessment data.
2. Never invent inventory figures, forecasts, risk levels or quantities.
3. Never change or override calculated recommendations.
4. Explain why products were prioritised using their supplied risk levels.
5. Clearly identify exceptions requiring human investigation.
6. Mention when safety stock uses a pooled fallback.
7. Distinguish simulated inventory data from actual business inventory.
8. Do not claim that recommendations guarantee stock availability.
9. Use concise, professional business language.
10. If information is missing, explicitly state that it is unavailable.

Structure your response with these sections:

## Portfolio Overview
## Highest-Priority Inventory Items
## Recommended Actions
## Exceptions and Limitations
"""

    response = client.chat.completions.create(
        model=GEMINI_MODEL,
        messages=[
            {
                "role": "system",
                "content": system_prompt,
            },
            {
                "role": "user",
                "content": (
                    "Analyse the following inventory assessment data:\n\n"
                    + json.dumps(
                        assessment_context,
                        indent=2,
                        default=str,
                    )
                ),
            },
        ],
    )

    explanation = response.choices[0].message.content

    if not explanation or not explanation.strip():
        raise RuntimeError(
            "Gemini returned an empty decision explanation."
        )

    return explanation.strip()
