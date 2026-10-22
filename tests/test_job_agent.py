"""
tests/test_job_agent.py - Unit tests for Agent 2: Job Description Analyst
"""

import pytest
from agents.job_agent import JobAnalystAgent
from models import JobAnalysis


def test_job_analyst_skill_normalization():
    agent = JobAnalystAgent()
    job_text = """
    Job Title: Senior AI Engineer
    Requirements:
    Must have hands-on experience with sklearn, tf, and py.
    Nice to have:
    Knowledge of k8s and postgres.
    """
    result = agent.analyze(job_text)

    assert isinstance(result, JobAnalysis)
    assert result.seniority_level == "Senior"
    # Verify normalization
    assert "Scikit-Learn" in result.required_skills
    assert "TensorFlow" in result.required_skills
    assert "Python" in result.required_skills
    assert "Kubernetes" in result.preferred_skills
    assert "PostgreSQL" in result.preferred_skills


def test_job_analyst_mandatory_vs_preferred():
    agent = JobAnalystAgent()
    job_text = """
    We require Python and SQL.
    Preferred:
    Docker and AWS.
    """
    result = agent.analyze(job_text)

    assert "Python" in result.required_skills
    assert "SQL" in result.required_skills
    assert "Docker" in result.preferred_skills
    assert "AWS" in result.preferred_skills
    # Check no cross-contamination
    assert "Docker" not in result.required_skills


def test_job_analyst_empty_input():
    agent = JobAnalystAgent()
    result = agent.analyze("")
    assert isinstance(result, JobAnalysis)
    assert len(result.required_skills) == 0
    assert len(result.preferred_skills) == 0
