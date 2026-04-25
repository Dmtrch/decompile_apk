import httpx
import os
import json
import logging

logger = logging.getLogger(__name__)

class AIAnalyzer:
    def __init__(self):
        self.ollama_host = os.getenv("OLLAMA_HOST", "http://host.docker.internal:11434")
        self.model = os.getenv("OLLAMA_MODEL", "qwen3.6:latest")

    async def explain_vulnerability(self, code_snippet: str, issue_description: str):
        """Запрашивает у локальной LLM объяснение уязвимости и способ исправления"""
        prompt = f"""
You are a Senior Android Security Expert. Analyze the following code snippet and its security issue.
Provide a clear explanation and a secure code patch.

ISSUE: {issue_description}
CODE:
```java
{code_snippet}
```

Format your response exactly as JSON with these keys:
"is_false_positive": boolean,
"explanation": "string",
"patch": "string"
"""
        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(
                    f"{self.ollama_host}/api/generate",
                    json={
                        "model": self.model,
                        "prompt": prompt,
                        "stream": False,
                        "format": "json"
                    }
                )
                response.raise_for_status()
                data = response.json()
                return json.loads(data["response"])
        except Exception as e:
            logger.error(f"Ollama request failed: {str(e)}")
            return {
                "error": f"Failed to reach AI Analyzer: {str(e)}",
                "is_false_positive": False,
                "explanation": "AI service is currently unavailable.",
                "patch": "// No patch available"
            }
