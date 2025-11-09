"""
AI service for generating course recommendations
"""
import json
from typing import Dict, Any, List
from openai import OpenAI
from anthropic import Anthropic
from app.core.config import settings
from app.services.prompts import SYSTEM_PROMPT, create_user_prompt


class AIService:
    def __init__(self):
        self.openai_client = OpenAI(api_key=settings.OPENAI_API_KEY)
        self.anthropic_client = Anthropic(api_key=settings.ANTHROPIC_API_KEY)

    def generate_recommendations(
        self,
        university: str,
        program_id: str,
        degree: str,
        major: str,
        completed: List[str],
        credits_target: int,
        track: str = None,
        preferences: dict = None,
        context_snippets: List[str] = None
    ) -> Dict[str, Any]:
        """
        Generate course recommendations using GPT-4o

        Returns:
            Dictionary with recommendations, notes, assumptions, and warnings
        """

        # Create user prompt
        user_prompt = create_user_prompt(
            university=university,
            program_id=program_id,
            degree=degree,
            major=major,
            completed=completed,
            credits_target=credits_target,
            track=track,
            preferences=preferences,
            context_snippets=context_snippets
        )

        # Call GPT-4o
        try:
            response = self.openai_client.chat.completions.create(
                model=settings.OPENAI_MODEL,
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.3,  # Lower temperature for more consistent outputs
                response_format={"type": "json_object"}
            )

            # Parse JSON response
            result = json.loads(response.choices[0].message.content)

            # Validate required fields
            if "recommendations" not in result:
                result["recommendations"] = []

            for key in ["notes", "assumptions", "warnings"]:
                if key not in result:
                    result[key] = []

            return result

        except Exception as e:
            print(f"Error generating recommendations: {e}")
            return {
                "recommendations": [],
                "notes": [],
                "assumptions": [],
                "warnings": [f"Error generating recommendations: {str(e)}"]
            }

    def summarize_catalog(self, text: str, max_tokens: int = 4000) -> str:
        """
        Summarize long catalog text using Claude Sonnet 4.5
        (For future use with scraped data)
        """
        try:
            response = self.anthropic_client.messages.create(
                model=settings.CLAUDE_MODEL,
                max_tokens=max_tokens,
                messages=[
                    {
                        "role": "user",
                        "content": f"Summarize the following course catalog information, preserving all course codes, prerequisites, and requirements:\n\n{text}"
                    }
                ]
            )

            return response.content[0].text

        except Exception as e:
            print(f"Error summarizing with Claude: {e}")
            return text  # Return original if summarization fails
