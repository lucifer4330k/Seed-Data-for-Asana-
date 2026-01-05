import os
import google.generativeai as genai
import logging
import time
import random
from typing import Optional

# Simple in-memory cache to save money/time during dev
_cache = {}

def configure_genai(api_key: str):
    if not api_key:
        logging.warning("No GOOGLE_API_KEY provided. LLM features will be disabled/mocked.")
        return
    genai.configure(api_key=api_key)

def generate_text(prompt: str, temperature: float = 0.7, model_name: str = "gemini-pro") -> str:
    """
    Generates text using Google Gemini API.
    """
    if prompt in _cache:
        return _cache[prompt]

    if not os.getenv("GOOGLE_API_KEY"):
        # Fallback for when no key is present - Use realistic pre-canned data
        p_lower = prompt.lower()
        if "task name" in p_lower:
            options = ["Fix race condition", "Update docs", "Client meeting", "Budget review", "Refactor API", "Design Review", "Deploy to prod", "Write tests"]
            return random.choice(options)
        elif "comment" in p_lower:
             return random.choice(["Looking into it.", "Done.", "Can you review?", "Blocked.", "Nice work!"])
        elif "description" in p_lower:
            return random.choice(["Detailed description here.", "See attached doc.", "", "Priority fix."])
        return f"Task related to: {prompt[:30]}"

    try:
        model = genai.GenerativeModel(model_name)
        response = model.generate_content(
            prompt,
            generation_config=genai.types.GenerationConfig(
                temperature=temperature
            )
        )
        text = response.text
        _cache[prompt] = text
        time.sleep(1) # Rate limiting politeness
        return text
    except Exception as e:
        logging.error(f"LLM Generation failed: {e}")
        return f"[ERROR generating content] {str(e)}"
