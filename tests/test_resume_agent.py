"""
tests/test_resume_agent.py - Unit tests for Agent 1: Resume Analyst
"""

import pytest
from agents.resume_agent import ResumeAnalystAgent
from models import ResumeAnalysis


def test_resume_analyst_basic_extraction():
    agent = ResumeAnalystAgent()
    sample_text = """
    Jane Doe
    jane.doe@example.com
    
    Education:
    Bachelor of Science in Data Science, Stanford University
    
    Technical Skills:
    Python, SQL, PyTorch, Scikit-Learn, Docker
    
    Projects:
    Autonomous Vision Model: Built deep learning pipeline in PyTorch for image classification.
    """
    result = agent.analyze(sample_text)

    assert isinstance(result, ResumeAnalysis)
    assert result.candidate_name == "Jane Doe"
    assert result.contact_email == "jane.doe@example.com"
    assert "Python" in result.skills
    assert "PyTorch" in result.skills
    assert "SQL" in result.skills
    assert "Docker" in result.skills

    # Check evidence identification
    pytorch_ev = next((e for e in result.evidence_records if e.skill_name == "PyTorch"), None)
    assert pytorch_ev is not None
    assert pytorch_ev.evidence_type == "explicit"


def test_resume_analyst_empty_input():
    agent = ResumeAnalystAgent()
    result = agent.analyze("")
    assert isinstance(result, ResumeAnalysis)
    assert len(result.skills) == 0
    assert "empty" in result.summary.lower()


def test_resume_analyst_no_hallucination():
    agent = ResumeAnalystAgent()
    # Resume only mentions Python and SQL
    text = "Candidate has expertise in Python scripting and SQL queries."
    result = agent.analyze(text)

    assert "Python" in result.skills
    assert "SQL" in result.skills
    # Must NOT invent LangChain or Docker
    assert "LangChain" not in result.skills
    assert "Docker" not in result.skills
