"""
agents/roadmap_agent.py - Agent 5: Career Roadmap Agent

Generates structured, realistic, week-by-week learning roadmaps
tailored to the user's available time and skill gaps.
"""

from typing import List, Dict
from models import (
    SkillGapAnalysis,
    ResourceRecommendations,
    CareerRoadmap,
    WeeklyMilestone,
)


class CareerRoadmapAgent:
    """Agent 5: Builds week-by-week personalized learning milestones."""

    def build_roadmap(
        self,
        gap_analysis: SkillGapAnalysis,
        resource_recs: ResourceRecommendations,
        target_role: str = "AI Engineer",
        experience_level: str = "Transitioning / Student",
        timeline_weeks: int = 8,
        available_hours_per_week: int = 15,
    ) -> CareerRoadmap:
        """
        Creates a structured weekly roadmap respecting time caps and dependencies.
        """
        # Ensure timeline_weeks is at least 2 and within reasonable limits
        timeline_weeks = max(2, min(timeline_weeks, 16))
        available_hours_per_week = max(5, min(available_hours_per_week, 40))

        priority_gaps = gap_analysis.priority_gaps
        if not priority_gaps:
            priority_gaps = gap_analysis.missing_preferred or ["Advanced Portfolio & System Design"]

        # Sort skills by dependency order: Foundations -> Frameworks -> Deployment/MLOps
        ordered_skills = self._order_skills_by_dependency(priority_gaps)

        milestones: List[WeeklyMilestone] = []

        # Distribute skills across the available weeks
        num_skills = len(ordered_skills)
        for week in range(1, timeline_weeks + 1):
            # Select skills for this week
            if num_skills > 0:
                skill_index = ((week - 1) * num_skills) // timeline_weeks
                current_skill = ordered_skills[min(skill_index, num_skills - 1)]
            else:
                current_skill = "System Optimization & Portfolio"

            # Retrieve recommended resource titles for this skill
            skill_resources = resource_recs.resources_by_skill.get(current_skill, [])
            resource_titles = [r.title for r in skill_resources[:2]]

            # Realistic hour allocation (never exceed available hours)
            planned_hours = min(available_hours_per_week, 12 if available_hours_per_week >= 12 else available_hours_per_week)

            title, objectives, exercises, deliverable, criteria = self._generate_week_content(
                week, timeline_weeks, current_skill
            )

            milestone = WeeklyMilestone(
                week_number=week,
                title=title,
                focus_skills=[current_skill],
                learning_objectives=objectives,
                practical_exercises=exercises,
                project_deliverable=deliverable,
                recommended_resource_titles=resource_titles,
                estimated_hours=planned_hours,
                completion_criteria=criteria,
            )
            milestones.append(milestone)

        portfolio_idea = (
            f"End-to-End {target_role} Showcase: Build a containerized AI service featuring "
            f"{', '.join(ordered_skills[:3])} with automated evaluation and interactive demo."
        )

        return CareerRoadmap(
            target_role=target_role,
            experience_level=experience_level,
            timeline_weeks=timeline_weeks,
            available_hours_per_week=available_hours_per_week,
            weekly_milestones=milestones,
            portfolio_project_idea=portfolio_idea,
            roadmap_notes=(
                "All hour figures are realistic estimates. Study hours are strictly capped "
                f"at your declared {available_hours_per_week} hrs/week limit."
            ),
        )

    def _order_skills_by_dependency(self, skills: List[str]) -> List[str]:
        """Orders skills logically: Foundations -> Core Deep Learning -> LLMs/GenAI -> MLOps."""
        tier_1 = {"Python", "SQL", "Pandas", "NumPy", "Statistics", "Data Structures & Algorithms"}
        tier_2 = {"Machine Learning", "Scikit-Learn", "Deep Learning", "PyTorch", "TensorFlow"}
        tier_3 = {"Natural Language Processing (NLP)", "Large Language Models (LLMs)", "LangChain", "Retrieval-Augmented Generation (RAG)"}
        tier_4 = {"Docker", "FastAPI", "MLOps", "Kubernetes", "AWS", "GCP"}

        t1, t2, t3, t4, other = [], [], [], [], []
        for s in skills:
            if s in tier_1:
                t1.append(s)
            elif s in tier_2:
                t2.append(s)
            elif s in tier_3:
                t3.append(s)
            elif s in tier_4:
                t4.append(s)
            else:
                other.append(s)

        return t1 + t2 + t3 + t4 + other

    def _generate_week_content(self, week: int, total_weeks: int, skill: str):
        """Generates concrete, practical exercises and measurable completion criteria."""
        if week == total_weeks:
            title = f"Capstone Integration & Portfolio Polish ({skill})"
            objectives = [
                f"Integrate {skill} into a cohesive final project repository.",
                "Write comprehensive README with architecture diagram and run instructions.",
                "Record a 2-minute demo walkthrough for technical recruiters.",
            ]
            exercises = [
                "Refactor codebase, add automated unit tests, and document environment setup.",
                "Deploy demo to a cloud host (Hugging Face Spaces or AWS/GCP).",
            ]
            deliverable = "Public GitHub repository with complete documentation, passing tests, and live demo."
            criteria = [
                "Repository is publicly accessible with clean commit history.",
                "Anyone can run the application with a single command.",
            ]
        elif week == 1:
            title = f"Foundational Ramp-Up & Environment Setup ({skill})"
            objectives = [
                f"Master core paradigms and syntax of {skill}.",
                "Set up local development environment, virtual environment, and linting.",
            ]
            exercises = [
                f"Complete beginner tutorials and small standalone scripts for {skill}.",
                "Implement 3 hands-on mini-exercises verifying expected outputs.",
            ]
            deliverable = f"Working local environment and documented sample scripts for {skill}."
            criteria = [
                f"Can explain the core concepts of {skill} without consulting documentation.",
                "All mini-exercise scripts run without errors.",
            ]
        else:
            title = f"Applied Implementation & Architectural Depth ({skill})"
            objectives = [
                f"Build a feature-complete module utilizing {skill}.",
                "Implement error handling, edge case coverage, and performance optimization.",
            ]
            exercises = [
                f"Develop a standalone micro-project demonstrating {skill} best practices.",
                "Benchmark execution time or evaluate metrics against a baseline.",
            ]
            deliverable = f"Self-contained project module showcasing {skill} in action."
            criteria = [
                "Module includes clear docstrings and error handling.",
                "Successfully processes real or realistic test inputs.",
            ]

        return title, objectives, exercises, deliverable, criteria
