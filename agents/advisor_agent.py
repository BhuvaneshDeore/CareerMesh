"""
agents/advisor_agent.py - Agent 6: Career Advisor and Report Agent

Synthesizes findings from Agents 1 through 5.
Generates candidate strengths, grounded resume improvement suggestions,
portfolio project designs, and interview preparation checklists.
"""

from datetime import datetime
from typing import List
from models import (
    ResumeAnalysis,
    JobAnalysis,
    SkillGapAnalysis,
    ResourceRecommendations,
    CareerRoadmap,
    AdvisorReport,
)


class CareerAdvisorAgent:
    """Agent 6: Strategic advisor synthesizing all multi-agent findings."""

    def advise(
        self,
        resume: ResumeAnalysis,
        job: JobAnalysis,
        gap: SkillGapAnalysis,
        resources: ResourceRecommendations,
        roadmap: CareerRoadmap,
    ) -> AdvisorReport:
        """Compiles strategic career guidance grounded exclusively in user inputs."""
        now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # 1. Candidate Strengths
        strengths = []
        if gap.demonstrated_required:
            strengths.append(
                f"Core Qualification Alignment: You possess proven practical experience in "
                f"{', '.join(gap.demonstrated_required)}, which are mandatory for this role."
            )
        if gap.demonstrated_preferred:
            strengths.append(
                f"Competitive Bonus Skills: You already possess preferred technologies: "
                f"{', '.join(gap.demonstrated_preferred)}."
            )
        if resume.projects:
            strengths.append(f"Demonstrated Project Capability: {len(resume.projects)} documented project achievements.")
        if not strengths:
            strengths.append("Foundational ambition to transition into modern AI Engineering.")

        # 2. Critical Skill Gaps
        critical_gaps = []
        if gap.missing_required:
            critical_gaps.append(
                f"High-Priority Missing Requirements: {', '.join(gap.missing_required)}. "
                "These are essential criteria for recruiter screening."
            )
        if gap.partially_demonstrated_required:
            critical_gaps.append(
                f"Under-documented Skills: {', '.join(gap.partially_demonstrated_required)} are mentioned "
                "in your resume but lack concrete project evidence or quantifiable results."
            )
        if gap.missing_preferred:
            critical_gaps.append(f"Nice-to-Have Expansion: {', '.join(gap.missing_preferred)}.")

        # 3. Prioritized Action Plan
        action_plan = [
            f"Phase 1 (Weeks 1-{max(1, roadmap.timeline_weeks // 2)}): Bridge foundational gaps in {', '.join(gap.priority_gaps[:2]) or 'target stack'}.",
            f"Phase 2 (Weeks {max(2, roadmap.timeline_weeks // 2 + 1)}-{roadmap.timeline_weeks}): Build the Capstone Portfolio Project ({roadmap.portfolio_project_idea}).",
            "Phase 3: Update resume bullet points with quantified outcomes and begin targeted interview preparation.",
        ]

        # 4. Resume Improvements (Grounded ONLY in supplied evidence)
        resume_improvements = []
        if gap.partially_demonstrated_required:
            for skill in gap.partially_demonstrated_required[:3]:
                resume_improvements.append(
                    f"Add measurable impact for {skill}: Instead of just listing '{skill}' under Skills, "
                    f"add a bullet point under a project or job describing what you built and the result achieved."
                )

        if resume.projects and not any(re_kw in "".join(resume.projects).lower() for re_kw in ("%", "improved", "reduced", "accuracy")):
            resume_improvements.append(
                "Quantify Existing Projects: Include specific metrics (e.g., accuracy, latency, dataset size, users) "
                "for your current projects to make your achievements verifiable."
            )

        if not resume.education:
            resume_improvements.append("Ensure your degree or relevant coursework is clearly listed under an 'Education' section.")

        if not resume_improvements:
            resume_improvements.append("Resume formatting is solid. Ensure links to your GitHub or live demo URLs are active.")

        # 5. Portfolio Recommendations
        portfolio_recs = [
            f"Primary Recommendation: {roadmap.portfolio_project_idea}",
            "Technical Requirements for Capstone: Include automated testing (pytest), Dockerfile for reproducibility, "
            "and a clean README explaining business problem, architecture, and instructions to run.",
        ]

        # 6. Interview Preparation Checklist (linked to gaps & matched skills)
        interview_prep = []
        for skill in gap.demonstrated_required[:3]:
            interview_prep.append(
                f"Prepare to explain technical trade-offs you made when using {skill} in your past projects."
            )
        for skill in gap.priority_gaps[:3]:
            interview_prep.append(
                f"Review fundamental interview questions and system design patterns for {skill}."
            )
        interview_prep.append("Practice describing your project failures and how you debugged complex issues.")

        # 7. Plain-Language Limitations Disclaimer
        disclaimer = (
            "CareerMesh is an automated career assessment and guidance tool. All match scores, roadmap time estimates, "
            "and recommendations are generated algorithmically for learning guidance only. This report does NOT guarantee "
            "employment, interview callbacks, salary levels, or hiring decisions from any employer. Real hiring decisions "
            "depend on numerous factors including live technical interviews, communication skills, cultural fit, and market conditions."
        )

        return AdvisorReport(
            generated_at=now_str,
            candidate_strengths=strengths,
            critical_skill_gaps=critical_gaps,
            prioritized_action_plan=action_plan,
            resume_improvement_suggestions=resume_improvements,
            portfolio_recommendations=portfolio_recs,
            interview_prep_checklist=interview_prep,
            limitations_disclaimer=disclaimer,
        )
