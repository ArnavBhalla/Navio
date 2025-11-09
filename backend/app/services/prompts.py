"""
AI prompt templates for academic advisor
"""

SYSTEM_PROMPT = """You are Navio, an academic advisor AI. Be precise and cautious. Use only the provided catalog and requirement snippets as your source of truth. If a rule is unclear, say so and cite the source_url.

Output a JSON object with:
- "recommendations": array of objects with {code, title, reason, fulfills, prereq_ok, citations: [source_url]}
- "notes": array of strings (general notes about the recommendations)
- "assumptions": array of strings (if you had to assume anything)
- "warnings": array of strings (for conflicts or missing prerequisite data)

Guidelines:
- Only recommend courses that appear in the provided catalog context
- Verify prerequisites carefully against completed courses
- Prioritize courses that fulfill multiple requirements
- For track requirements, ensure courses have appropriate tags
- Cite source URLs for every recommendation
- If a student is missing prerequisites, set prereq_ok to false and add a warning
- Target the requested credit load but prioritize staying on track for graduation
"""


def create_user_prompt(
    university: str,
    program_id: str,
    degree: str,
    major: str,
    completed: list[str],
    credits_target: int,
    track: str = None,
    preferences: dict = None,
    context_snippets: list[str] = None
) -> str:
    """Create user prompt with all context"""

    completed_str = ", ".join(completed) if completed else "None"
    prefs_str = str(preferences) if preferences else "None specified"
    context_str = "\n\n".join(context_snippets) if context_snippets else ""

    prompt = f"""University: {university}
Program: {program_id} ({degree} {major})
Track: {track if track else "None"}
Completed courses: {completed_str}
Desired credit load: {credits_target} credits
Preferences: {prefs_str}

CATALOG AND REQUIREMENT CONTEXT:
{context_str}

---

Based on the above context, recommend courses for next semester that:
1. Keep the student on track to graduate
2. Fulfill program requirements and track requirements (if applicable)
3. Have satisfied prerequisites
4. Meet the target credit load (approximately {credits_target} credits)

Return recommendations as a JSON object matching the schema described in the system prompt.
"""

    return prompt
