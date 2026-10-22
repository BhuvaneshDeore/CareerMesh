"""
tests/test_resource_agent.py - Unit tests for Agent 4: Learning Resource Agent
"""

import pytest
from agents.resource_agent import LearningResourceAgent
from models import SkillGapAnalysis


def test_resource_agent_known_skills():
    agent = LearningResourceAgent(enable_online=False)
    gap = SkillGapAnalysis(
        priority_gaps=["PyTorch", "Docker"],
        missing_preferred=["FastAPI"],
    )
    result = agent.recommend(gap)

    assert "PyTorch" in result.resources_by_skill
    assert "Docker" in result.resources_by_skill
    assert "FastAPI" in result.resources_by_skill

    pytorch_resources = result.resources_by_skill["PyTorch"]
    assert len(pytorch_resources) > 0
    assert pytorch_resources[0].is_verified is True
    assert "pytorch.org" in pytorch_resources[0].url


def test_resource_agent_unknown_skill_fallback():
    agent = LearningResourceAgent(enable_online=False)
    gap = SkillGapAnalysis(
        priority_gaps=["QuantumSuperpositionComputingFrameworkXYZ"],
    )
    result = agent.recommend(gap)

    assert "QuantumSuperpositionComputingFrameworkXYZ" in result.resources_by_skill
    resources = result.resources_by_skill["QuantumSuperpositionComputingFrameworkXYZ"]
    assert len(resources) == 1
    # Must NOT claim this fabricated resource is verified
    assert resources[0].is_verified is False
    assert "search?q=" in resources[0].url


def test_resource_agent_no_gaps():
    agent = LearningResourceAgent(enable_online=False)
    gap = SkillGapAnalysis(priority_gaps=[], missing_preferred=[])
    result = agent.recommend(gap)

    assert len(result.resources_by_skill) == 0
    assert len(result.notes) > 0
