import os
import requests
from typing import Optional


class CerebrasClient:
    """Client for interacting with Cerebras API for text summarization."""

    def __init__(self):
        self.api_key = os.getenv("CEREBRAS_API_KEY")
        self.api_url = "https://api.cerebras.ai/v1/chat/completions"
        self.model = "gpt-oss-120b"
        
        if not self.api_key:
            raise ValueError("CEREBRAS_API_KEY environment variable is not set")

    def estimate_tokens(self, text: str) -> int:
        """
        Rough estimate of token count.
        Approximation: 1 token ≈ 4 characters
        """
        return len(text) // 4

    def truncate_text(self, text: str, max_tokens: int = 150000) -> str:
        """
        Truncate text to approximately max_tokens.
        Leaves room for prompt and response.
        """
        max_chars = max_tokens * 4
        if len(text) > max_chars:
            return text[:max_chars] + "\n[... truncated due to length ...]"
        return text

    def summarize(self, text: str, timeout: int = 30) -> Optional[str]:
        """
        Call Cerebras API to generate a summary of the provided text.
        
        Args:
            text: The text to summarize
            timeout: Request timeout in seconds
            
        Returns:
            Summary text or None if error occurs
        """
        try:
            # Truncate text if it exceeds token limits
            truncated_text = self.truncate_text(text)
            
            prompt = f"""Please provide a comprehensive summary of the following text in paragraph format. 
The summary should capture the key points, main ideas, and important details.

Text to summarize:
{truncated_text}

Summary:"""

            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }

            payload = {
                "model": self.model,
                "messages": [
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                "temperature": 0.7,
                "max_tokens": 2000
            }

            response = requests.post(
                self.api_url,
                headers=headers,
                json=payload,
                timeout=timeout
            )

            if response.status_code == 200:
                result = response.json()
                summary = result.get("choices", [{}])[0].get("message", {}).get("content", "")
                return summary.strip()
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


def get_cerebras_client() -> CerebrasClient:
    """Factory function to get a Cerebras client instance."""
    return CerebrasClient()
