import os
import requests
from typing import Optional


class CerebrasClient:
    """Client for interacting with Cerebras API for text summarization."""

    def __init__(self):
        self.api_key = os.getenv("CEREBRAS_API_KEY")
        self.api_url = "https://api.cerebras.ai/v1/chat/completions"
        self.model = "gpt-oss-120b"
        self.timeout = 30
        self.max_tokens = 150000
        self.response_tokens = 2000
        
        if not self.api_key:
            raise ValueError("CEREBRAS_API_KEY environment variable is not set")

    def estimate_tokens(self, text: str) -> int:
        """Rough estimate of token count. Approximation: 1 token ≈ 4 characters"""
        return len(text) // 4

    def truncate_text(self, text: str, max_tokens: int = None) -> str:
        """Truncate text to approximately max_tokens."""
        max_tokens = max_tokens or self.max_tokens
        max_chars = max_tokens * 4
        if len(text) > max_chars:
            return text[:max_chars] + "\n[... truncated due to length ...]"
        return text

    def _build_request_payload(self, prompt: str) -> dict:
        """Build the API request payload."""
        return {
            "model": self.model,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.7,
            "max_tokens": self.response_tokens
        }

    def _make_api_request(self, payload: dict, headers: dict) -> Optional[str]:
        """Make API request and handle response."""
        try:
            response = requests.post(
                self.api_url,
                headers=headers,
                json=payload,
                timeout=self.timeout
            )

            if response.status_code == 200:
                result = response.json()
                return result.get("choices", [{}])[0].get("message", {}).get("content", "").strip()
            else:
                print(f"Cerebras API error: {response.status_code} - {response.text}")
                return None

        except requests.exceptions.Timeout:
            print("Cerebras API request timed out")
            return None
        except requests.exceptions.RequestException as e:
            print(f"Cerebras API request failed: {str(e)}")
            return None
        except Exception as e:
            print(f"Error calling Cerebras API: {str(e)}")
            return None

    def summarize(self, text: str) -> Optional[str]:
        """Call Cerebras API to generate a summary of the provided text."""
        truncated_text = self.truncate_text(text)
        
        prompt = f"""Please provide a comprehensive summary of the following text in exactly one single paragraph. 
The summary must be a single cohesive paragraph, must capture the key points, main ideas, and important details, and must NOT contain any bullet points, lists, or multiple paragraphs.

Text to summarize:
{truncated_text}

Summary:"""

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        payload = self._build_request_payload(prompt)
        return self._make_api_request(payload, headers)


def get_cerebras_client() -> CerebrasClient:
    """Factory function to get a Cerebras client instance."""
    return CerebrasClient()
