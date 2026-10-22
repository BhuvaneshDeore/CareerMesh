"""
services/report_generator.py - Report Generator for CareerMesh

Generates formatted Markdown reports and structured JSON reports.
Ensures unique timestamped filenames, sanitization, and deterministic output.
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Tuple

from config import OUTPUT_DIR
from models import CareerMeshSessionResult


def save_reports(session_result: CareerMeshSessionResult) -> Tuple[Path, Path]:
    """
    Saves both the Markdown report and the JSON report to the configured output folder.

    Returns:
    (markdown_file_path, json_file_path)
    """
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    timestamp_str = datetime.now().strftime("%Y%m%d_%H%M%S")
    sanitized_id = "".join(c for c in session_result.session_id if c.isalnum() or c in ("-", "_"))

    md_filename = f"careermesh_report_{sanitized_id}_{timestamp_str}.md"
    json_filename = f"careermesh_report_{sanitized_id}_{timestamp_str}.json"

    md_path = OUTPUT_DIR / md_filename
    json_path = OUTPUT_DIR / json_filename

    # Generate Markdown text
    markdown_content = generate_markdown_report(session_result)
    with open(md_path, "w", encoding="utf-8") as f:
        f.write(markdown_content)

    # Generate JSON text
    json_data = session_result.model_dump(mode="json")
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(json_data, f, indent=2, ensure_ascii=False)

    return md_path, json_path


def generate_markdown_report(result: CareerMeshSessionResult) -> str:
    """Creates a comprehensive, beautifully styled Markdown report."""
    res = result.resume_analysis
    job = result.job_analysis
    gap = result.skill_gap_analysis
    res_rec = result.resource_recommendations
    roadmap = result.roadmap
    advisor = result.advisor_report

    lines = []
    lines.append("# CareerMesh — Multi-Agent AI Career Assessment Report")
    lines.append(f"**Session ID:** `{result.session_id}` | **Generated:** {result.created_at} | **Mode:** `{result.execution_mode.upper()}`")
    lines.append("\n---\n")

    # 1. Executive Summary
    lines.append("## 1. Executive Summary")
    lines.append(f"- **Target Role:** {job.job_title} ({job.seniority_level} Seniority, {job.job_family})")
    lines.append(f"- **Overall Role Match Score:** **{gap.overall_match_score}%** (Transparent weighted evaluation)")
    lines.append(f"- **Required Skills Match:** **{gap.required_skills_score}%**")
    lines.append(f"- **Preferred Skills Match:** **{gap.preferred_skills_score}%**")
    lines.append(f"- **Top Priority Gaps:** {', '.join(gap.priority_gaps) if gap.priority_gaps else 'None detected'}")
    lines.append("\n---\n")

    # 2. Candidate Profile Analysis
    lines.append("## 2. Candidate Profile Analysis (Resume Analyst)")
    if res.candidate_name:
        lines.append(f"- **Name:** {res.candidate_name}")
    if res.contact_email:
        lines.append(f"- **Contact:** {res.contact_email}")
    lines.append(f"- **Summary:** {res.summary or 'Profile extracted from resume.'}")
    if res.education:
        lines.append(f"- **Education:** {', '.join(res.education)}")
    if res.experience:
        lines.append(f"- **Experience:** {', '.join(res.experience)}")
    if res.projects:
        lines.append(f"- **Projects:** {', '.join(res.projects)}")
    if res.certifications:
        lines.append(f"- **Certifications:** {', '.join(res.certifications)}")

    lines.append("\n### Detected Skills by Category:")
    for cat, skills in res.skill_categories.items():
        if skills:
            lines.append(f"- **{cat}:** {', '.join(skills)}")

    if res.missing_or_unreadable:
        lines.append("\n> [!NOTE]\n> **Missing/Unreadable Sections:** " + ", ".join(res.missing_or_unreadable))

    lines.append("\n---\n")

    # 3. Target Job Description Analysis
    lines.append("## 3. Target Role Requirements (Job Analyst)")
    lines.append(f"- **Job Title:** {job.job_title}")
    lines.append(f"- **Seniority Level:** {job.seniority_level}")
    lines.append(f"- **Job Family:** {job.job_family}")
    if job.experience_expectations:
        lines.append(f"- **Experience Expectations:** {job.experience_expectations}")
    lines.append(f"- **Required Skills:** {', '.join(job.required_skills) if job.required_skills else 'None recognized'}")
    lines.append(f"- **Preferred Skills:** {', '.join(job.preferred_skills) if job.preferred_skills else 'None recognized'}")
    if job.ambiguous_requirements:
        lines.append(f"- **Ambiguous Requirements Identified:** {', '.join(job.ambiguous_requirements)}")

    lines.append("\n---\n")

    # 4. Detailed Skill Comparison Table
    lines.append("## 4. Skill Gap Matrix & Scoring (Skill Gap Analyst)")
    lines.append("\n| Skill Name | Requirement Type | Match Status | Resume Evidence & Notes |")
    lines.append("| :--- | :--- | :--- | :--- |")
    for comp in gap.comparisons:
        req_label = "Mandatory" if comp.is_required else "Preferred"
        evidence = comp.resume_evidence if comp.resume_evidence else comp.notes
        lines.append(f"| **{comp.skill_name}** | {req_label} | `{comp.status}` | {evidence} |")

    lines.append("\n### Scoring Formula & Breakdown:")
    lines.append(f"- **Formula:** `{gap.scoring_formula}`")
    lines.append(f"- **Denominator:** {gap.scoring_denominator}")
    lines.append(f"- **Required Skills Score:** {gap.required_skills_score}%")
    lines.append(f"- **Preferred Skills Score:** {gap.preferred_skills_score}%")
    lines.append(f"- **Final Weighted Score:** **{gap.overall_match_score}%**")
    lines.append("\n> [!IMPORTANT]\n> The Match Score is an objective skills alignment assessment. It is **NOT** a probability of being hired or receiving an interview.")

    lines.append("\n---\n")

    # 5. Curated Learning Resources
    lines.append("## 5. Curated Learning Resources (Resource Agent)")
    if res_rec.resources_by_skill:
        lines.append("\n| Skill | Title & Provider | Type | Verified | Link | Why Useful |")
        lines.append("| :--- | :--- | :--- | :--- | :--- | :--- |")
        for skill, items in res_rec.resources_by_skill.items():
            for r in items:
                v_badge = "Yes" if r.is_verified else "Unverified"
                lines.append(f"| **{skill}** | {r.title} ({r.provider}) | {r.resource_type} | {v_badge} | [Link]({r.url}) | {r.why_useful} |")
    else:
        lines.append("No specific missing skills to recommend resources for.")

    lines.append("\n---\n")

    # 6. Personalized Weekly Roadmap
    lines.append("## 6. Personalized Career Roadmap (Roadmap Agent)")
    lines.append(f"- **Timeline:** {roadmap.timeline_weeks} Weeks")
    lines.append(f"- **Available Commitment:** {roadmap.available_hours_per_week} Hours / Week (Total: ~{roadmap.timeline_weeks * roadmap.available_hours_per_week} hours)")
    lines.append(f"- **Recommended Portfolio Capstone:** {roadmap.portfolio_project_idea}")

    for m in roadmap.weekly_milestones:
        lines.append(f"\n### Week {m.week_number}: {m.title} (~{m.estimated_hours} Hours)")
        lines.append(f"- **Focus Skills:** {', '.join(m.focus_skills)}")
        lines.append("- **Objectives:**")
        for obj in m.learning_objectives:
            lines.append(f"  - {obj}")
        lines.append("- **Practical Exercises:**")
        for ex in m.practical_exercises:
            lines.append(f"  - {ex}")
        if m.project_deliverable:
            lines.append(f"- **Milestone Deliverable:** {m.project_deliverable}")
        lines.append("- **Completion Criteria:**")
        for crit in m.completion_criteria:
            lines.append(f"  - {crit}")

    lines.append("\n---\n")

    # 7. Strategic Career Advice
    lines.append("## 7. Strategic Career Advice (Career Advisor Agent)")
    lines.append("\n### Candidate Strengths:")
    for s in advisor.candidate_strengths:
        lines.append(f"- {s}")

    lines.append("\n### Action Plan:")
    for action in advisor.prioritized_action_plan:
        lines.append(f"- {action}")

    lines.append("\n### Resume Improvements (Based Strictly on Provided Evidence):")
    for r_sug in advisor.resume_improvement_suggestions:
        lines.append(f"- {r_sug}")

    lines.append("\n### Recommended Portfolio Projects:")
    for port in advisor.portfolio_recommendations:
        lines.append(f"- {port}")

    lines.append("\n### Interview Preparation Checklist:")
    for item in advisor.interview_prep_checklist:
        lines.append(f"- [ ] {item}")

    lines.append("\n---\n")

    # 8. Limitations & Privacy Disclaimer
    lines.append("## 8. Limitations & Disclaimer")
    lines.append(advisor.limitations_disclaimer)

    return "\n".join(lines)
