import json
from typing import Dict, List, Any


class PromptBuilder:
    """Centralized manager for all LLM prompts used in analysis and theme extraction."""

    RESEARCH_QUESTIONS = {
        "Q1": "Why do users repeatedly buy from the same categories?",
        "Q2": "What prevents users from exploring new categories?",
        "Q3": "How do users discover products today?",
        "Q4": "What role do habits play in shopping behavior?",
        "Q5": "What information do users need before trying a new category?",
        "Q6": "What frustrations emerge repeatedly?",
        "Q7": "Which user segments are more likely to experiment?",
        "Q8": "What unmet needs emerge consistently across discussions?",
    }

    SYSTEM_BASE = (
        "You are an expert Principal Product Manager and Customer Intelligence Engine for Blinkit, "
        "India's leading quick-commerce platform delivering groceries, snacks, household items, electronics, "
        "personal care, and pet supplies in 10 minutes.\n"
        "Your goal is to analyze user feedback to uncover why users stick to repetitive grocery orders "
        "and how to drive cross-category adoption to increase Monthly Active Customers (MAC) buying from new categories."
    )

    @classmethod
    def theme_extraction_prompt(cls, source: str, records: List[Dict[str, Any]]) -> tuple[str, str]:
        """Generates prompt and system instruction for batch theme extraction."""
        reviews_input = [
            {
                "record_id": r.get("id"),
                "text": r.get("text_clean", r.get("text", ""))[:300],
                "rating": r.get("rating"),
                "categories": r.get("categories", []),
                "topics": r.get("topics", []),
            }
            for r in records
        ]

        system_instruction = (
            f"{cls.SYSTEM_BASE}\n"
            "Extract 5 to 10 recurring customer themes from this batch of feedback records for source: '{source}'.\n"
            "Return JSON matching this schema exactly:\n"
            "{\n"
            "  \"themes\": [\n"
            "    {\n"
            "      \"id\": \"theme_<source>_<number>\",\n"
            "      \"name\": \"Short descriptive theme title\",\n"
            "      \"description\": \"Detailed explanation of user behaviour or complaint\",\n"
            "      \"frequency\": \"high|medium|low\",\n"
            "      \"category_relevance\": \"high|medium|low\",\n"
            "      \"source\": \"" + source + "\",\n"
            "      \"representative_quotes\": [\n"
            "        {\"record_id\": \"<exact_record_id>\", \"text\": \"<exact_review_text>\", \"source\": \"" + source + "\"}\n"
            "      ],\n"
            "      \"research_question_mapping\": [\"Q1\", \"Q2\", ...]\n"
            "    }\n"
            "  ]\n"
            "}\n"
            "Map each theme to relevant research questions from: " + json.dumps(cls.RESEARCH_QUESTIONS)
        )

        user_prompt = json.dumps({"source": source, "reviews_batch": reviews_input}, indent=2)
        return user_prompt, system_instruction

    @classmethod
    def theme_consolidation_prompt(cls, per_source_themes: Dict[str, List[Dict[str, Any]]]) -> tuple[str, str]:
        """Generates prompt for consolidating themes across all sources into mega-themes."""
        system_instruction = (
            f"{cls.SYSTEM_BASE}\n"
            "Consolidate overlapping themes from multiple feedback sources into 6 to 10 unified Mega-Themes.\n"
            "Return JSON matching this schema:\n"
            "{\n"
            "  \"consolidated_themes\": [\n"
            "    {\n"
            "      \"id\": \"mega_theme_<number>\",\n"
            "      \"name\": \"Unified Theme Name\",\n"
            "      \"description\": \"Comprehensive synthesis across sources\",\n"
            "      \"contributing_sources\": [\"play_store\", \"reddit\", ...],\n"
            "      \"underlying_theme_ids\": [\"theme_ps_001\", ...],\n"
            "      \"representative_quotes\": [{\"record_id\": \"...\", \"text\": \"...\", \"source\": \"...\"}],\n"
            "      \"research_question_mapping\": [\"Q1\", \"Q2\", ...]\n"
            "    }\n"
            "  ]\n"
            "}"
        )

        user_prompt = json.dumps({"per_source_themes": per_source_themes}, indent=2)
        return user_prompt, system_instruction

    @classmethod
    def insight_synthesis_prompt(cls, consolidated_themes: List[Dict[str, Any]]) -> tuple[str, str]:
        """Generates prompt for synthesizing actionable product insights from consolidated themes."""
        system_instruction = (
            f"{cls.SYSTEM_BASE}\n"
            "Synthesize 8 to 15 strategic Product Insights from the consolidated mega-themes.\n"
            "Each insight MUST address the North Star Metric: '% MAC purchasing from >=1 new category/month'.\n"
            "Return JSON matching this schema:\n"
            "{\n"
            "  \"insights\": [\n"
            "    {\n"
            "      \"id\": \"insight_<number>\",\n"
            "      \"title\": \"Clear Executive Summary Title\",\n"
            "      \"statement\": \"In-depth problem statement and user behaviour insight\",\n"
            "      \"evidence_strength\": \"strong|moderate|weak\",\n"
            "      \"sources_corroborating\": [\"play_store\", \"app_store\", ...],\n"
            "      \"source_count\": 2,\n"
            "      \"supporting_themes\": [\"mega_theme_01\", ...],\n"
            "      \"representative_quotes\": [{\"record_id\": \"...\", \"text\": \"...\", \"source\": \"...\"}],\n"
            "      \"research_questions_addressed\": [\"Q1\", \"Q4\", ...],\n"
            "      \"user_segment\": \"Habitual Grocery Buyers\",\n"
            "      \"recommended_action\": \"Specific PM product change or feature experiment\",\n"
            "      \"impact_potential\": \"high|medium|low\",\n"
            "      \"priority_rank\": 1\n"
            "    }\n"
            "  ]\n"
            "}\n"
            "Ensure ALL 8 research questions (Q1–Q8) are addressed across the insight set."
        )

    @classmethod
    def emotion_agent_prompt(cls, records: List[Dict[str, Any]]) -> tuple[str, str]:
        """Generates prompt for Agent 2: Emotional Spectrum Extraction."""
        reviews_input = [{"id": r.get("id"), "text": r.get("text_clean", r.get("text", ""))[:200]} for r in records[:15]]
        system_instruction = (
            f"{cls.SYSTEM_BASE}\n"
            "You are Agent 2 (Emotion Agent). Analyze the underlying emotional spectrum blocking category expansion.\n"
            "Return JSON matching this schema:\n"
            "{\n"
            "  \"emotion_profiles\": [\n"
            "    {\n"
            "      \"emotion_name\": \"Risk Perception | Uncertainty | Cognitive Fatigue | Trust Deficit | Delight\",\n"
            "      \"intensity\": 0.0-1.0,\n"
            "      \"trigger_context\": \"Why customers feel this emotion regarding non-grocery categories\",\n"
            "      \"impact_on_exploration\": \"High Friction | Moderate Barrier | Positive Driver\",\n"
            "      \"representative_quotes\": [{\"text\": \"...\", \"source\": \"...\"}]\n"
            "    }\n"
            "  ]\n"
            "}"
        )
        return json.dumps({"reviews": reviews_input}, indent=2), system_instruction

    @classmethod
    def habit_agent_prompt(cls, records: List[Dict[str, Any]]) -> tuple[str, str]:
        """Generates prompt for Agent 3: Habit Loop Detection."""
        reviews_input = [{"id": r.get("id"), "text": r.get("text_clean", r.get("text", ""))[:200]} for r in records[:15]]
        system_instruction = (
            f"{cls.SYSTEM_BASE}\n"
            "You are Agent 3 (Habit Agent). Extract behavioral Habit Loops (Trigger -> Action -> Reward).\n"
            "Return JSON matching this schema:\n"
            "{\n"
            "  \"habit_loops\": [\n"
            "    {\n"
            "      \"trigger\": \"Contextual need (e.g. Sunday Morning Grocery Need)\",\n"
            "      \"action\": \"App behavior (e.g. Repeat Previous Basket in 1-click)\",\n"
            "      \"reward\": \"App outcome (e.g. 10-Minute Instant Checkout)\",\n"
            "      \"exploration_barrier\": \"Why this loop prevents trying new categories\",\n"
            "      \"interruption_opportunity\": \"Product intervention to nudge exploration\"\n"
            "    }\n"
            "  ]\n"
            "}"
        )
        return json.dumps({"reviews": reviews_input}, indent=2), system_instruction

    @classmethod
    def jtbd_agent_prompt(cls, records: List[Dict[str, Any]]) -> tuple[str, str]:
        """Generates prompt for Agent 4: Jobs-To-Be-Done Analysis."""
        reviews_input = [{"id": r.get("id"), "text": r.get("text_clean", r.get("text", ""))[:200]} for r in records[:15]]
        system_instruction = (
            f"{cls.SYSTEM_BASE}\n"
            "You are Agent 4 (JTBD Agent). Identify fundamental human Jobs-To-Be-Done customer needs.\n"
            "Return JSON matching this schema:\n"
            "{\n"
            "  \"jtbd_items\": [\n"
            "    {\n"
            "      \"job_statement\": \"When I am in [context], I want to [action], so that [outcome]\",\n"
            "      \"functional_need\": \"Practical task to achieve\",\n"
            "      \"emotional_need\": \"Internal feeling desired\",\n"
            "      \"target_category_opportunity\": \"Category expansion opportunity (e.g., Personal Care, Pet Care)\",\n"
            "      \"current_solution\": \"How users attempt to solve this today\"\n"
            "    }\n"
            "  ]\n"
            "}"
        )
        return json.dumps({"reviews": reviews_input}, indent=2), system_instruction

    @classmethod
    def segment_agent_prompt(cls, records: List[Dict[str, Any]]) -> tuple[str, str]:
        """Generates prompt for Agent 5: Consumer Archetype Finder."""
        reviews_input = [{"id": r.get("id"), "text": r.get("text_clean", r.get("text", ""))[:200]} for r in records[:15]]
        system_instruction = (
            f"{cls.SYSTEM_BASE}\n"
            "You are Agent 5 (Segment Agent). Discover emergent consumer archetypes.\n"
            "Return JSON matching this schema:\n"
            "{\n"
            "  \"consumer_archetypes\": [\n"
            "    {\n"
            "      \"archetype_name\": \"Routine Buyers | Explorers | Value Seekers | Busy Parents | Health Focused | Convenience Seekers\",\n"
            "      \"description\": \"Key behavioral traits and shopping profile\",\n"
            "      \"percentage_estimate\": 10-40,\n"
            "      \"primary_categories\": [\"groceries\", \"snacks\"],\n"
            "      \"barriers_to_new_categories\": \"Main friction preventing category trial\",\n"
            "      \"growth_nudge\": \"Product feature or experiment to trigger trial\"\n"
            "    }\n"
            "  ]\n"
            "}"
        )
        return json.dumps({"reviews": reviews_input}, indent=2), system_instruction

    @classmethod
    def contradiction_agent_prompt(cls, records: List[Dict[str, Any]]) -> tuple[str, str]:
        """Generates prompt for Agent 6: Stated vs. Actual Contradictions."""
        reviews_input = [{"id": r.get("id"), "text": r.get("text_clean", r.get("text", ""))[:300]} for r in records[:50]]
        system_instruction = (
            f"{cls.SYSTEM_BASE}\n"
            "You are Agent 6 (Contradiction Agent). Surface gaps between stated desires vs actual purchasing behaviors.\n"
            "Return JSON matching this schema:\n"
            "{\n"
            "  \"contradictions\": [\n"
            "    {\n"
            "      \"stated_desire\": \"What users claim in reviews or discussions\",\n"
            "      \"actual_behavior\": \"How users actually behave on the platform\",\n"
            "      \"underlying_friction\": \"The psychological or UX root cause\",\n"
            "      \"product_opportunity\": \"How Blinkit can bridge this gap to drive category expansion\"\n"
            "    }\n"
            "  ]\n"
            "}"
        )
        return json.dumps({"reviews": reviews_input}, indent=2), system_instruction

