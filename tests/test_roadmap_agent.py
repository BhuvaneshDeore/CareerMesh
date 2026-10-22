"""
tests/test_roadmap_agent.py - Unit tests for Agent 5: Career Roadmap Agent
"""

import pytest
from agents.roadmap_agent import CareerRoadmapAgent
from models import SkillGapAnalysis, ResourceRecommendations


def test_roadmap_timelines():
    agent = CareerRoadmapAgent()
    gap = SkillGapAnalysis(priority_gaps=["Python", "PyTorch", "Docker", "MLOps"])
    recs = ResourceRecommendations()

    # Test 4 weeks
    roadmap_4 = agent.build_roadmap(gap, recs, timeline_weeks=4, available_hours_per_week=10)
    assert len(roadmap_4.weekly_milestones) == 4

    # Test 8 weeks
    roadmap_8 = agent.build_roadmap(gap, recs, timeline_weeks=8, available_hours_per_week=15)
    assert len(roadmap_8.weekly_milestones) == 8


def test_roadmap_study_hour_caps():
    agent = CareerRoadmapAgent()
    gap = SkillGapAnalysis(priority_gaps=["PyTorch", "FastAPI"])
    recs = ResourceRecommendations()

    available_hours = 8
    roadmap = agent.build_roadmap(gap, recs, timeline_weeks=4, available_hours_per_week=available_hours)

    for milestone in roadmap.weekly_milestones:
        assert milestone.estimated_hours <= available_hours


def test_roadmap_dependency_ordering():
    agent = CareerRoadmapAgent()
    skills = ["MLOps", "Python", "PyTorch"]
    ordered = agent._order_skills_by_dependency(skills)

    # Python (foundations) should be before PyTorch (DL) and MLOps (Deployment)
    assert ordered.index("Python") < ordered.index("PyTorch")
    assert ordered.index("PyTorch") < ordered.index("MLOps")
