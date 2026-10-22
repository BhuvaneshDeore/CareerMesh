"""
tests/test_skill_gap_agent.py - Unit tests for Agent 3: Skill Gap Analyst
"""

import pytest
from agents.skill_gap_agent import SkillGapAnalystAgent
from models import ResumeAnalysis, JobAnalysis, SkillEvidence


def test_skill_gap_perfect_match():
    agent = SkillGapAnalystAgent(required_weight=0.7, preferred_weight=0.3)
    resume = ResumeAnalysis(
        skills=["Python", "SQL"],
        evidence_records=[
            SkillEvidence(skill_name="Python", evidence_type="explicit", context="Projects"),
            SkillEvidence(skill_name="SQL", evidence_type="explicit", context="Experience"),
        ],
    )
    job = JobAnalysis(
        required_skills=["Python", "SQL"],
        preferred_skills=[],
    )
    result = agent.analyze(resume, job)

    assert result.required_skills_score == 100.0
    assert result.overall_match_score == 100.0
    assert len(result.missing_required) == 0


def test_skill_gap_zero_division_guard():
    agent = SkillGapAnalystAgent()
    resume = ResumeAnalysis(skills=[])
    job = JobAnalysis(required_skills=[], preferred_skills=[])

    result = agent.analyze(resume, job)
    assert result.overall_match_score == 0.0
    assert result.required_skills_score == 0.0
    assert result.preferred_skills_score == 0.0


def test_skill_gap_partial_and_missing():
    agent = SkillGapAnalystAgent(required_weight=0.7, preferred_weight=0.3)
    resume = ResumeAnalysis(
        skills=["Python"],
        evidence_records=[
            SkillEvidence(skill_name="Python", evidence_type="inferred", context="Skills list"),
        ],
    )
    # Required: Python (partial: 0.5), Docker (missing: 0.0) -> (0.5 / 2) * 100 = 25%
    # Preferred: AWS (missing: 0.0) -> 0%
    job = JobAnalysis(
        required_skills=["Python", "Docker"],
        preferred_skills=["AWS"],
    )
    result = agent.analyze(resume, job)

    assert result.required_skills_score == 25.0
    assert result.preferred_skills_score == 0.0
    # Overall: 25.0 * 0.7 + 0.0 * 0.3 = 17.5%
    assert result.overall_match_score == 17.5
    assert "Docker" in result.priority_gaps


def test_skill_gap_duplicate_skills_handling():
    agent = SkillGapAnalystAgent()
    resume = ResumeAnalysis(
        skills=["Python", "Python", "SQL"],
        evidence_records=[
            SkillEvidence(skill_name="Python", evidence_type="explicit"),
        ],
    )
    job = JobAnalysis(
        required_skills=["Python", "Python"],
        preferred_skills=["SQL", "SQL"],
    )
    result = agent.analyze(resume, job)

    # Should not inflate scoring beyond 100%
    assert result.required_skills_score <= 100.0
    assert result.preferred_skills_score <= 100.0
