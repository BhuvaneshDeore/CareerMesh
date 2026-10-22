"""
agents/skill_gap_agent.py - Agent 3: Skill Gap Analyst

Compares candidate skills with required and preferred job qualifications.
Evaluates evidence depth, calculates transparent, weighted match scores,
and identifies critical skill gaps.
"""

from typing import List, Dict, Optional
from models import (
    ResumeAnalysis,
    JobAnalysis,
    SkillGapAnalysis,
    SkillComparison,
    MatchStatus,
)
from config import (
    REQUIRED_SKILLS_WEIGHT,
    PREFERRED_SKILLS_WEIGHT,
    EVIDENCE_WEIGHT_DEMONSTRATED,
    EVIDENCE_WEIGHT_PARTIAL,
    EVIDENCE_WEIGHT_NOT_FOUND,
)


class SkillGapAnalystAgent:
    """Agent 3: Evaluates skill alignment, evidence depth, and transparent scoring."""

    def __init__(
        self,
        required_weight: float = REQUIRED_SKILLS_WEIGHT,
        preferred_weight: float = PREFERRED_SKILLS_WEIGHT,
    ):
        self.required_weight = required_weight
        self.preferred_weight = preferred_weight

    def analyze(self, resume: ResumeAnalysis, job: JobAnalysis) -> SkillGapAnalysis:
        """Compares resume analysis and job analysis."""
        comparisons: List[SkillComparison] = []

        # Build evidence lookup
        evidence_map: Dict[str, str] = {}
        for ev in resume.evidence_records:
            evidence_map[ev.skill_name] = f"{ev.evidence_type.title()} ({ev.context})"

        candidate_skills_set = set(resume.skills)

        # 1. Process Required Skills
        demonstrated_req = []
        partial_req = []
        missing_req = []

        for skill in job.required_skills:
            status, note, ev_text = self._evaluate_skill_match(skill, candidate_skills_set, evidence_map)
            comparisons.append(
                SkillComparison(
                    skill_name=skill,
                    is_required=True,
                    status=status,
                    resume_evidence=ev_text,
                    notes=note,
                )
            )
            if status == "Demonstrated":
                demonstrated_req.append(skill)
            elif status == "Partially Demonstrated":
                partial_req.append(skill)
            else:
                missing_req.append(skill)

        # 2. Process Preferred Skills
        demonstrated_pref = []
        missing_pref = []

        for skill in job.preferred_skills:
            status, note, ev_text = self._evaluate_skill_match(skill, candidate_skills_set, evidence_map)
            comparisons.append(
                SkillComparison(
                    skill_name=skill,
                    is_required=False,
                    status=status,
                    resume_evidence=ev_text,
                    notes=note,
                )
            )
            if status in ("Demonstrated", "Partially Demonstrated"):
                demonstrated_pref.append(skill)
            else:
                missing_pref.append(skill)

        # 3. Calculate Scores
        req_score = self._calculate_subscore(demonstrated_req, partial_req, len(job.required_skills))
        pref_score = self._calculate_subscore(demonstrated_pref, [], len(job.preferred_skills))

        # Overall weighted score
        # If no preferred skills exist, required score takes 100%
        if len(job.preferred_skills) == 0:
            overall_score = req_score
            formula_desc = "Overall Score = Required Skills Score (100% since no preferred skills listed)"
            denom_desc = f"{len(job.required_skills)} required skills"
        elif len(job.required_skills) == 0:
            overall_score = pref_score
            formula_desc = "Overall Score = Preferred Skills Score (100% since no required skills listed)"
            denom_desc = f"{len(job.preferred_skills)} preferred skills"
        else:
            overall_score = round(
                (req_score * self.required_weight) + (pref_score * self.preferred_weight), 1
            )
            formula_desc = (
                f"Overall Score = (Required Score {req_score}% × {self.required_weight}) + "
                f"(Preferred Score {pref_score}% × {self.preferred_weight})"
            )
            denom_desc = (
                f"{len(job.required_skills)} required skills (weight {self.required_weight}) + "
                f"{len(job.preferred_skills)} preferred skills (weight {self.preferred_weight})"
            )

        # Priority gaps: Missing required skills first, then partial required skills
        priority_gaps = missing_req + partial_req

        return SkillGapAnalysis(
            comparisons=comparisons,
            demonstrated_required=demonstrated_req,
            partially_demonstrated_required=partial_req,
            missing_required=missing_req,
            demonstrated_preferred=demonstrated_pref,
            missing_preferred=missing_pref,
            required_skills_score=req_score,
            preferred_skills_score=pref_score,
            overall_match_score=overall_score,
            scoring_formula=formula_desc,
            scoring_denominator=denom_desc,
            priority_gaps=priority_gaps,
            scoring_mode="rule_based",
        )

    def _evaluate_skill_match(
        self,
        skill: str,
        candidate_skills: set,
        evidence_map: Dict[str, str],
    ) -> tuple[MatchStatus, str, Optional[str]]:
        """Determines match status and provides notes."""
        if skill in candidate_skills:
            evidence_str = evidence_map.get(skill, "")
            if "Explicit" in evidence_str:
                return (
                    "Demonstrated",
                    "Explicit practical evidence found in projects or work history.",
                    evidence_str,
                )
            else:
                return (
                    "Partially Demonstrated",
                    "Skill mentioned in resume summary, but lacks project details.",
                    evidence_str,
                )

        # Check for related foundational knowledge
        related_map = {
            "PyTorch": ["Python", "Machine Learning", "Deep Learning"],
            "TensorFlow": ["Python", "Machine Learning"],
            "LangChain": ["Python", "Large Language Models (LLMs)"],
            "Retrieval-Augmented Generation (RAG)": ["Python", "Large Language Models (LLMs)"],
            "MLOps": ["Docker", "Git", "Python"],
            "Docker": ["Linux"],
            "Kubernetes": ["Docker"],
            "FastAPI": ["Python"],
        }
        foundations = related_map.get(skill, [])
        found_matches = [f for f in foundations if f in candidate_skills]

        if found_matches:
            return (
                "Partially Demonstrated",
                f"Candidate possesses relevant foundation ({', '.join(found_matches)}), making this an easy bridge.",
                None,
            )

        return (
            "Not Found in Resume",
            "Skill not mentioned in resume text. Note: This does not mean candidate cannot perform it.",
            None,
        )

    def _calculate_subscore(
        self,
        demonstrated: List[str],
        partial: List[str],
        total_count: int,
    ) -> float:
        """Safely calculates subscore handling zero division."""
        if total_count == 0:
            return 0.0

        points = (len(demonstrated) * EVIDENCE_WEIGHT_DEMONSTRATED) + (
            len(partial) * EVIDENCE_WEIGHT_PARTIAL
        )
        score = (points / total_count) * 100.0
        return round(min(score, 100.0), 1)
