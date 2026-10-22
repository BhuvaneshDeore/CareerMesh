"""
agents/resource_agent.py - Agent 4: Learning Resource Agent

Recommends reputable, vetted learning resources for priority missing
and partially demonstrated technical skills.
Works completely offline without requiring any API keys.
"""

from typing import Dict, List, Optional
from models import SkillGapAnalysis, ResourceRecommendations, LearningResource
from services.resource_catalog import get_resources_for_skill
from config import ENABLE_ONLINE_VERIFICATION


class LearningResourceAgent:
    """Agent 4: Curates learning resources for skill gaps."""

    def __init__(self, enable_online: bool = ENABLE_ONLINE_VERIFICATION):
        self.enable_online = enable_online

    def recommend(self, gap_analysis: SkillGapAnalysis) -> ResourceRecommendations:
        """
        Receives gap analysis and compiles relevant resources for priority skills.
        """
        resources_by_skill: Dict[str, List[LearningResource]] = {}
        notes: List[str] = []

        # Target skills: Priority gaps (required missing/partial) + missing preferred
        target_skills = list(dict.fromkeys(gap_analysis.priority_gaps + gap_analysis.missing_preferred))

        if not target_skills:
            notes.append("Candidate matches all identified role requirements. No critical skill gaps need resources.")
            return ResourceRecommendations(
                resources_by_skill={},
                catalog_mode="offline_catalog",
                notes=notes,
            )

        for skill in target_skills:
            skill_resources = get_resources_for_skill(skill)
            if skill_resources:
                resources_by_skill[skill] = skill_resources

        mode_str = "online_search" if self.enable_online else "offline_catalog"
        notes.append(f"Compiled learning resources for {len(resources_by_skill)} priority skills using {mode_str}.")

        return ResourceRecommendations(
            resources_by_skill=resources_by_skill,
            catalog_mode=mode_str,
            notes=notes,
        )
