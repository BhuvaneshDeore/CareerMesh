"""
models.py - Core data models and schemas for CareerMesh.

Defines Pydantic schemas for all 6 agents to ensure type safety,
validation, and reliable serialization.
"""

from typing import List, Dict, Optional, Literal
from pydantic import BaseModel, Field


# -------------------------------------------------------------
# Agent 1: Resume Analyst Models
# -------------------------------------------------------------
class SkillEvidence(BaseModel):
    skill_name: str
    category: str = "other"  # programming, data, machine_learning, deep_learning, llms, deployment, databases, cloud, other
    evidence_type: Literal["explicit", "inferred"] = "explicit"
    context: str = ""  # excerpt or project context
    years_or_depth: Optional[str] = None


class ResumeAnalysis(BaseModel):
    candidate_name: Optional[str] = None
    contact_email: Optional[str] = None
    education: List[str] = Field(default_factory=list)
    experience: List[str] = Field(default_factory=list)
    projects: List[str] = Field(default_factory=list)
    certifications: List[str] = Field(default_factory=list)
    skills: List[str] = Field(default_factory=list)
    skill_categories: Dict[str, List[str]] = Field(default_factory=dict)
    evidence_records: List[SkillEvidence] = Field(default_factory=list)
    summary: str = ""
    missing_or_unreadable: List[str] = Field(default_factory=list)
    extraction_mode: str = "rule_based"  # "rule_based" or "llm"


# -------------------------------------------------------------
# Agent 2: Job Description Analyst Models
# -------------------------------------------------------------
class JobAnalysis(BaseModel):
    job_title: str = "Target Role"
    seniority_level: str = "Not Specified"  # Entry-Level, Junior, Mid-Level, Senior
    job_family: str = "AI Engineer"  # AI Engineer, Data Scientist, ML Engineer, Python Developer, Data Analyst, Other
    responsibilities: List[str] = Field(default_factory=list)
    required_skills: List[str] = Field(default_factory=list)
    preferred_skills: List[str] = Field(default_factory=list)
    tools_and_frameworks: List[str] = Field(default_factory=list)
    experience_expectations: str = ""
    ambiguous_requirements: List[str] = Field(default_factory=list)
    extraction_mode: str = "rule_based"


# -------------------------------------------------------------
# Agent 3: Skill Gap Analyst Models
# -------------------------------------------------------------
MatchStatus = Literal[
    "Demonstrated",
    "Partially Demonstrated",
    "Not Found in Resume",
    "Requires Manual Verification",
]


class SkillComparison(BaseModel):
    skill_name: str
    is_required: bool = True  # True if required, False if preferred
    status: MatchStatus
    resume_evidence: Optional[str] = None
    notes: str = ""


class SkillGapAnalysis(BaseModel):
    comparisons: List[SkillComparison] = Field(default_factory=list)
    demonstrated_required: List[str] = Field(default_factory=list)
    partially_demonstrated_required: List[str] = Field(default_factory=list)
    missing_required: List[str] = Field(default_factory=list)
    demonstrated_preferred: List[str] = Field(default_factory=list)
    missing_preferred: List[str] = Field(default_factory=list)
    required_skills_score: float = 0.0
    preferred_skills_score: float = 0.0
    overall_match_score: float = 0.0
    scoring_formula: str = ""
    scoring_denominator: str = ""
    priority_gaps: List[str] = Field(default_factory=list)
    scoring_mode: str = "rule_based"


# -------------------------------------------------------------
# Agent 4: Learning Resource Agent Models
# -------------------------------------------------------------
class LearningResource(BaseModel):
    title: str
    provider: str
    skill: str
    difficulty: Literal["Beginner", "Intermediate", "Advanced"] = "Beginner"
    resource_type: Literal[
        "Official Documentation",
        "Interactive Course",
        "Practical Tutorial",
        "Book",
        "Hands-on Project Guide",
    ] = "Official Documentation"
    url: str
    is_verified: bool = False
    why_useful: str = ""


class ResourceRecommendations(BaseModel):
    resources_by_skill: Dict[str, List[LearningResource]] = Field(default_factory=dict)
    catalog_mode: Literal["offline_catalog", "online_search"] = "offline_catalog"
    notes: List[str] = Field(default_factory=list)


# -------------------------------------------------------------
# Agent 5: Career Roadmap Agent Models
# -------------------------------------------------------------
class WeeklyMilestone(BaseModel):
    week_number: int
    title: str
    focus_skills: List[str] = Field(default_factory=list)
    learning_objectives: List[str] = Field(default_factory=list)
    practical_exercises: List[str] = Field(default_factory=list)
    project_deliverable: str = ""
    recommended_resource_titles: List[str] = Field(default_factory=list)
    estimated_hours: int = 10
    completion_criteria: List[str] = Field(default_factory=list)


class CareerRoadmap(BaseModel):
    target_role: str = "AI Engineer"
    experience_level: str = "Transitioning"
    timeline_weeks: int = 8
    available_hours_per_week: int = 15
    weekly_milestones: List[WeeklyMilestone] = Field(default_factory=list)
    portfolio_project_idea: str = ""
    roadmap_notes: str = ""


# -------------------------------------------------------------
# Agent 6: Career Advisor and Final Report Models
# -------------------------------------------------------------
class AdvisorReport(BaseModel):
    generated_at: str
    candidate_strengths: List[str] = Field(default_factory=list)
    critical_skill_gaps: List[str] = Field(default_factory=list)
    prioritized_action_plan: List[str] = Field(default_factory=list)
    resume_improvement_suggestions: List[str] = Field(default_factory=list)
    portfolio_recommendations: List[str] = Field(default_factory=list)
    interview_prep_checklist: List[str] = Field(default_factory=list)
    limitations_disclaimer: str = ""
    markdown_report_path: Optional[str] = None
    json_report_path: Optional[str] = None


# -------------------------------------------------------------
# Full Multi-Agent Session Result
# -------------------------------------------------------------
class CareerMeshSessionResult(BaseModel):
    session_id: str
    created_at: str
    execution_mode: str = "rule_based"  # "rule_based" or "llm"
    resume_analysis: ResumeAnalysis
    job_analysis: JobAnalysis
    skill_gap_analysis: SkillGapAnalysis
    resource_recommendations: ResourceRecommendations
    roadmap: CareerRoadmap
    advisor_report: AdvisorReport
    markdown_report_file: str = ""
    json_report_file: str = ""
