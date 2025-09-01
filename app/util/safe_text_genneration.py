import json, re

def safe_json_loads(text: str):
        """Cleans common formatting issues and parses JSON safely."""
        if not text or not text.strip():
            raise ValueError("Empty response received from LLM")
        
        # Remove Markdown fences (```json ... ```)
        text = re.sub(r"^```(?:json)?", "", text.strip(), flags=re.MULTILINE)
        text = re.sub(r"```$", "", text.strip(), flags=re.MULTILINE)
        
        # Try parsing
        try:
            return json.loads(text)
        except json.JSONDecodeError as e:
            raise ValueError(f"Failed to parse JSON: {e}\nRaw content:\n{text[:500]}")