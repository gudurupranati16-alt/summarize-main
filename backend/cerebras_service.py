from cerebras.cloud.sdk import Cerebras  # pyrefly: ignore[missing-import]
import os
import json
import re
from dotenv import load_dotenv  # pyrefly: ignore[missing-import]

load_dotenv()


def get_cerebras_client():
    api_key = os.getenv("CEREBRAS_API_KEY")

    if not api_key:
        raise ValueError(
            "CEREBRAS_API_KEY is not set. Please add it to backend/.env"
        )

    return Cerebras(api_key=api_key)


def generate_summary(article_text: str) -> dict:
    """
    Generate a single-paragraph summary and sentiment analysis.
    """

    if not article_text or not article_text.strip():
        raise ValueError("Input text is empty.")

    max_chars = 300000

    if len(article_text) > max_chars:
        article_text = (
            article_text[:max_chars]
            + "\n\n[Text truncated due to size]"
        )

    client = get_cerebras_client()

    model = os.getenv("CEREBRAS_MODEL", "gpt-oss-120b")

    print(f"Using model: {model}")

    prompt = f"""
You are an expert news analyst.

Analyze the following PDF article content.

Tasks:

1. Create ONE concise paragraph summary.
2. Determine overall sentiment:
   - Positive
   - Negative
   - Neutral
   - Mixed
3. Give a short explanation of the sentiment.

Return ONLY valid JSON.

{{
    "summary": "single paragraph summary",
    "sentiment": "Positive",
    "sentiment_explanation": "short explanation"
}}

ARTICLE CONTENT:
{article_text}
"""

    try:
        response = client.chat.completions.create(
            model=model,
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.3,
            max_completion_tokens=1500
        )

        if (
            not response.choices
            or not response.choices[0].message.content
        ):
            raise Exception("Empty response from Cerebras.")

        raw_content = response.choices[0].message.content.strip()

        print("\n===== RAW CEREBRAS RESPONSE =====")
        print(raw_content)
        print("=================================\n")

        try:
            result = json.loads(raw_content)

        except json.JSONDecodeError:

            # First attempt — JSON in code block
            json_match = re.search(
                r"```(?:json)?\s*(\{.*?\})\s*```",
                raw_content,
                re.DOTALL
            )

            if json_match:
                result = json.loads(json_match.group(1))

            else:
                # Second attempt — JSON object anywhere in plain text
                json_match = re.search(
                    r'\{[^{}]*"summary"[^{}]*\}',
                    raw_content,
                    re.DOTALL
                )

                if json_match:
                    result = json.loads(json_match.group(0))

                else:
                    result = {
                        "summary": raw_content,
                        "sentiment": "Neutral",
                        "sentiment_explanation": "Could not reliably parse sentiment."
                    }

        # Force summary into a single paragraph
        summary = result.get("summary", "").strip()
        summary = " ".join(
            line.strip()
            for line in summary.splitlines()
            if line.strip()
        )

        sentiment = result.get("sentiment", "Neutral").strip()

        valid_sentiments = {
            "Positive",
            "Negative",
            "Neutral",
            "Mixed"
        }

        if sentiment not in valid_sentiments:
            sentiment = "Neutral"

        sentiment_explanation = result.get(
            "sentiment_explanation",
            "No explanation provided."
        ).strip()

        return {
            "summary": summary,
            "sentiment": sentiment,
            "sentiment_explanation": sentiment_explanation
        }

    except Exception as e:
        raise RuntimeError(
            f"Cerebras API call failed: {str(e)}"
        )