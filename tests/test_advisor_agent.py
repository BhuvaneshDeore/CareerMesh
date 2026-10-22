"""
tests/test_advisor_agent.py - Unit tests for Agent 6: Career Advisor Agent
"""

import pytest
from agents.advisor_agent import CareerAdvisorAgent
from models import (
    ResumeAnalysis,
    JobAnalysis,
    SkillGapAnalysis,
    ResourceRecommendations,
    CareerRoadmap,
)


def test_advisor_agent_grounded_output():
    agent = CareerAdvisorAgent()
    resume = ResumeAnalysis(
        skills=["Python"],
        projects=["Built customer churn predictor."],
    )
    job = JobAnalysis(
        job_title="AI Engineer",
        required_skills=["Python", "PyTorch"],
    )
    gap = SkillGapAnalysis(
        demonstrated_required=["Python"],
        missing_required=["PyTorch"],
        priority_gaps=["PyTorch"],
    )
    resources = ResourceRecommendations()
    roadmap = CareerRoadmap(portfolio_project_idea="Build PyTorch AI Service")

    report = agent.advise(resume, job, gap, resources, roadmap)

    # Strengths should mention Python
    assert any("Python" in s for s in report.candidate_strengths)
    # Gaps should mention PyTorch
    assert any("PyTorch" in g for g in report.critical_skill_gaps)
    # Interview prep should link to PyTorch
    assert any("PyTorch" in ip for ip in report.interview_prep_checklist)
    # Must contain disclaimer
    assert "guarantee" in report.limitations_disclaimer.lower()
    assert "not" in report.limitations_disclaimer.lower()
