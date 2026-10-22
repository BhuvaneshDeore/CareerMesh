"""
orchestrator.py - CareerMesh Multi-Agent Workflow Coordinator

Coordinates execution across all six agents sequentially:
1. Resume Analyst
2. Job Description Analyst
3. Skill Gap Analyst
4. Learning Resource Agent
5. Career Roadmap Agent
6. Career Advisor Agent
Then saves generated Markdown and JSON reports.
"""

import uuid
import logging
from datetime import datetime
from typing import Optional, Callable

from models import CareerMeshSessionResult
from agents.resume_agent import ResumeAnalystAgent
from agents.job_agent import JobAnalystAgent
from agents.skill_gap_agent import SkillGapAnalystAgent
from agents.resource_agent import LearningResourceAgent
from agents.roadmap_agent import CareerRoadmapAgent
from agents.advisor_agent import CareerAdvisorAgent
from services.report_generator import save_reports
from services.llm_provider import get_configured_llm_provider

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] [%(name)s]: %(message)s",
)
logger = logging.getLogger("CareerMesh.Orchestrator")


class OrchestrationError(Exception):
    """Raised when an orchestration stage fails critically."""
    pass


class CareerMeshOrchestrator:
    """
    Manages the sequential lifecycle of CareerMesh's 6 agents.
    Provides real-time terminal progress callbacks and safe error handling.
    """

    def __init__(self, use_llm_if_available: bool = False):
        self.use_llm = use_llm_if_available
        self.llm_provider = get_configured_llm_provider() if use_llm_if_available else None

        # Instantiate agents
        self.resume_agent = ResumeAnalystAgent(llm_provider=self.llm_provider)
        self.job_agent = JobAnalystAgent(llm_provider=self.llm_provider)
        self.skill_gap_agent = SkillGapAnalystAgent()
        self.resource_agent = LearningResourceAgent()
        self.roadmap_agent = CareerRoadmapAgent()
        self.advisor_agent = CareerAdvisorAgent()

    def run_workflow(
        self,
        resume_input: str,
        job_input: str,
        is_resume_file: bool = False,
        is_job_file: bool = False,
        timeline_weeks: int = 8,
        available_hours_per_week: int = 15,
        progress_callback: Optional[Callable[[int, str], None]] = None,
    ) -> CareerMeshSessionResult:
        """
        Executes the full 6-agent workflow.

        progress_callback: optional function(step_number, message) for UI updates.
        """
        session_id = str(uuid.uuid4())[:8]
        created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        execution_mode = "llm" if (self.llm_provider and self.llm_provider.is_available()) else "rule_based"

        def notify(step: int, msg: str):
            logger.info(f"[Step {step}/6] {msg}")
            if progress_callback:
                progress_callback(step, msg)

        # -----------------------------------------------------------------
        # Stage 1: Resume Analyst
        # -----------------------------------------------------------------
        notify(1, "Running Agent 1: Resume Analyst...")
        try:
            resume_analysis = self.resume_agent.analyze(resume_input, is_file_path=is_resume_file)
            if not resume_analysis.skills and not resume_analysis.education and not resume_analysis.experience:
                logger.warning("Agent 1 extracted minimal or no content from resume.")
        except Exception as e:
            logger.error(f"Stage 1 failed: {str(e)}", exc_info=True)
            raise OrchestrationError(f"Agent 1 (Resume Analyst) failed: {str(e)}")

        # -----------------------------------------------------------------
        # Stage 2: Job Description Analyst
        # -----------------------------------------------------------------
        notify(2, "Running Agent 2: Job Description Analyst...")
        try:
            job_analysis = self.job_agent.analyze(job_input, is_file_path=is_job_file)
            if not job_analysis.required_skills and not job_analysis.preferred_skills:
                logger.warning("Agent 2 did not identify explicit technical skills from job description.")
        except Exception as e:
            logger.error(f"Stage 2 failed: {str(e)}", exc_info=True)
            raise OrchestrationError(f"Agent 2 (Job Description Analyst) failed: {str(e)}")

        # -----------------------------------------------------------------
        # Stage 3: Skill Gap Analyst
        # -----------------------------------------------------------------
        notify(3, "Running Agent 3: Skill Gap Analyst...")
        try:
            gap_analysis = self.skill_gap_agent.analyze(resume_analysis, job_analysis)
        except Exception as e:
            logger.error(f"Stage 3 failed: {str(e)}", exc_info=True)
            raise OrchestrationError(f"Agent 3 (Skill Gap Analyst) failed: {str(e)}")

        # -----------------------------------------------------------------
        # Stage 4: Learning Resource Agent
        # -----------------------------------------------------------------
        notify(4, "Running Agent 4: Learning Resource Agent...")
        try:
            resource_recs = self.resource_agent.recommend(gap_analysis)
        except Exception as e:
            logger.error(f"Stage 4 failed: {str(e)}", exc_info=True)
            raise OrchestrationError(f"Agent 4 (Learning Resource Agent) failed: {str(e)}")

        # -----------------------------------------------------------------
        # Stage 5: Career Roadmap Agent
        # -----------------------------------------------------------------
        notify(5, "Running Agent 5: Career Roadmap Agent...")
        try:
            roadmap = self.roadmap_agent.build_roadmap(
                gap_analysis=gap_analysis,
                resource_recs=resource_recs,
                target_role=job_analysis.job_title,
                timeline_weeks=timeline_weeks,
                available_hours_per_week=available_hours_per_week,
            )
        except Exception as e:
            logger.error(f"Stage 5 failed: {str(e)}", exc_info=True)
            raise OrchestrationError(f"Agent 5 (Career Roadmap Agent) failed: {str(e)}")

        # -----------------------------------------------------------------
        # Stage 6: Career Advisor and Final Report Agent
        # -----------------------------------------------------------------
        notify(6, "Running Agent 6: Career Advisor & Report Agent...")
        try:
            advisor_report = self.advisor_agent.advise(
                resume=resume_analysis,
                job=job_analysis,
                gap=gap_analysis,
                resources=resource_recs,
                roadmap=roadmap,
            )
        except Exception as e:
            logger.error(f"Stage 6 failed: {str(e)}", exc_info=True)
            raise OrchestrationError(f"Agent 6 (Career Advisor Agent) failed: {str(e)}")

        # -----------------------------------------------------------------
        # Save Generated Reports
        # -----------------------------------------------------------------
        logger.info("Saving session reports (Markdown & JSON)...")
        session_result = CareerMeshSessionResult(
            session_id=session_id,
            created_at=created_at,
            execution_mode=execution_mode,
            resume_analysis=resume_analysis,
            job_analysis=job_analysis,
            skill_gap_analysis=gap_analysis,
            resource_recommendations=resource_recs,
            roadmap=roadmap,
            advisor_report=advisor_report,
        )

        try:
            md_path, json_path = save_reports(session_result)
            session_result.markdown_report_file = str(md_path)
            session_result.json_report_file = str(json_path)
            advisor_report.markdown_report_path = str(md_path)
            advisor_report.json_report_path = str(json_path)
            logger.info(f"Reports saved: \n  Markdown: {md_path}\n  JSON: {json_path}")
        except Exception as e:
            logger.error(f"Report saving failed: {str(e)}", exc_info=True)
            raise OrchestrationError(f"Report generation failed: {str(e)}")

        return session_result
