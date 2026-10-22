"""
tests/test_orchestrator.py - End-to-end integration tests for CareerMesh Orchestrator
"""

import pytest
import json
from pathlib import Path
from orchestrator import CareerMeshOrchestrator, OrchestrationError
from services.llm_provider import GeminiRESTProvider, LLMConfigurationError


def test_orchestrator_full_e2e_run():
    orchestrator = CareerMeshOrchestrator(use_llm_if_available=False)

    sample_resume = """
    Jane Developer
    jane@example.com
    Skills: Python, SQL, Pandas, Git, Scikit-Learn
    Projects: Built regression model predicting prices with Scikit-Learn.
    """

    sample_job = """
    Job Title: AI Engineer
    Requirements:
    Python, SQL, PyTorch, Docker, MLOps
    Preferred:
    FastAPI, AWS
    """

    steps_recorded = []

    def callback(step, msg):
        steps_recorded.append(step)

    result = orchestrator.run_workflow(
        resume_input=sample_resume,
        job_input=sample_job,
        timeline_weeks=4,
        available_hours_per_week=10,
        progress_callback=callback,
    )

    # 1. Verify all 6 stages executed
    assert steps_recorded == [1, 2, 3, 4, 5, 6]

    # 2. Verify outputs from each agent
    assert result.resume_analysis.skills == ["Git", "Pandas", "Python", "SQL", "Scikit-Learn"]
    assert "PyTorch" in result.job_analysis.required_skills
    assert "Docker" in result.skill_gap_analysis.missing_required
    assert "PyTorch" in result.skill_gap_analysis.priority_gaps
    assert "PyTorch" in result.resource_recommendations.resources_by_skill
    assert len(result.roadmap.weekly_milestones) == 4
    assert len(result.advisor_report.prioritized_action_plan) > 0

    # 3. Verify reports saved to disk
    md_file = Path(result.markdown_report_file)
    json_file = Path(result.json_report_file)

    assert md_file.exists()
    assert json_file.exists()
    assert md_file.stat().st_size > 500
    assert json_file.stat().st_size > 500

    # 4. Verify JSON valid serialization
    with open(json_file, "r", encoding="utf-8") as f:
        loaded = json.load(f)
    assert loaded["session_id"] == result.session_id


def test_missing_api_key_behavior():
    # Attempting to call LLM provider with empty API key raises clean LLMConfigurationError
    provider = GeminiRESTProvider(api_key="")
    assert provider.is_available() is False
    with pytest.raises(LLMConfigurationError):
        provider.generate_json("test prompt", "schema")
