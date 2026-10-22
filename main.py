"""
main.py - CareerMesh: 6-Agent AI Career Assistant CLI

Interactive terminal interface supporting:
- Pre-loaded Demo Profiles (AI Engineer, Data Scientist)
- Custom resume entry (Paste text, .txt, .pdf, .docx)
- Custom job description (Paste text, .txt)
- Configurable study hours and target timeline
- Live progress feedback across all 6 agents
- Concise terminal summary and output file paths
"""

import sys
import os
from pathlib import Path

# Add current directory to Python path
sys.path.insert(0, str(Path(__file__).resolve().parent))

from orchestrator import CareerMeshOrchestrator, OrchestrationError
from config import BASE_DIR, SAMPLE_JOBS_DIR, LLM_PROVIDER
from services.file_parser import FileParsingError


def print_banner():
    print("\n" + "=" * 70)
    print("      CAREERMESH -- 6-AGENT AI CAREER ASSISTANT")
    print("      Modular, Explainable, Multi-Agent Career Strategy")
    print("=" * 70)
    print("  Workflow: Resume Analyst -> Job Analyst -> Skill Gap Analyst")
    print("            -> Resource Agent -> Roadmap Agent -> Career Advisor")
    print("=" * 70)


def get_multiline_text(prompt_title: str) -> str:
    """Safely prompts user for multiline text terminated by 'DONE'."""
    print(f"\n{prompt_title}")
    print("(Tip: Paste your text, then type 'DONE' on a new line and press Enter)\n")

    lines = []
    while True:
        try:
            line = input()
            if line.strip().upper() == "DONE":
                break
            lines.append(line)
        except EOFError:
            break
        except KeyboardInterrupt:
            print("\nInput cancelled.")
            sys.exit(0)

    return "\n".join(lines).strip()


def prompt_resume_input() -> tuple[str, bool]:
    """Prompts user to select resume input method (paste or file)."""
    print("\nSelect Resume Input Method:")
    print("  [1] Paste resume text")
    print("  [2] Load resume file (.pdf, .docx, or .txt)")

    choice = input("Enter choice [1/2, default: 1]: ").strip()
    if choice == "2":
        file_path_str = input("Enter full path to resume file: ").strip().strip('"').strip("'")
        return file_path_str, True
    else:
        text = get_multiline_text("Paste Resume Text:")
        return text, False


def prompt_job_input() -> tuple[str, bool]:
    """Prompts user to select job description input method."""
    print("\nSelect Job Description Input Method:")
    print("  [1] Paste job description text")
    print("  [2] Load job description file (.txt)")
    print("  [3] Use built-in Sample AI Engineer Job Description")
    print("  [4] Use built-in Sample Data Scientist Job Description")

    choice = input("Enter choice [1-4, default: 3]: ").strip()
    if choice == "2":
        path_str = input("Enter path to job description file: ").strip().strip('"').strip("'")
        return path_str, True
    elif choice == "1":
        text = get_multiline_text("Paste Job Description Text:")
        return text, False
    elif choice == "4":
        sample_path = SAMPLE_JOBS_DIR / "data_scientist.txt"
        return str(sample_path), True
    else:
        sample_path = SAMPLE_JOBS_DIR / "ai_engineer.txt"
        return str(sample_path), True


def main():
    print_banner()

    print("\nSelect Run Mode:")
    print("  [1] Fast Interactive Demo (Pre-loaded Student Resume & AI Engineer Job)")
    print("  [2] Custom Assessment (Provide your own Resume & Target Job)")
    print("  [3] Exit")

    mode_choice = input("\nEnter choice [1-3, default: 1]: ").strip()
    if mode_choice == "3":
        print("Goodbye!")
        sys.exit(0)

    # 1. Gather Inputs
    if mode_choice == "2":
        resume_input, is_resume_file = prompt_resume_input()
        job_input, is_job_file = prompt_job_input()
    else:
        print("\n>>> Loading Fast Interactive Demo data...")
        resume_input = str(BASE_DIR / "data" / "sample_student_resume.txt")
        job_input = str(SAMPLE_JOBS_DIR / "ai_engineer.txt")
        is_resume_file = True
        is_job_file = True

    # 2. Timeline & Hours
    print("\nRoadmap Configuration:")
    try:
        timeline_raw = input("Target timeline in weeks [4, 8, 12, default: 8]: ").strip()
        timeline_weeks = int(timeline_raw) if timeline_raw else 8
    except ValueError:
        timeline_weeks = 8

    try:
        hours_raw = input("Available study hours per week [5-40, default: 15]: ").strip()
        available_hours = int(hours_raw) if hours_raw else 15
    except ValueError:
        available_hours = 15

    # 3. Execution Mode Selection (Rule-based vs LLM)
    use_llm = False
    print("\nAgent Reasoning Engine:")
    print("  [1] Deterministic Rule-Based Engine (Default, fast, zero API keys required)")
    if LLM_PROVIDER:
        print(f"  [2] Configured LLM Provider ({LLM_PROVIDER.upper()})")
    else:
        print("  [2] LLM Mode (No provider configured in .env - will run demo mode with instructions)")

    engine_choice = input("Enter engine choice [1/2, default: 1]: ").strip()
    if engine_choice == "2":
        if LLM_PROVIDER:
            print(f"\n[Notice]: Using configured {LLM_PROVIDER.upper()} provider. Resume text will be analyzed via external API.")
            use_llm = True
        else:
            print("\n[Notice]: LLM mode requested, but no LLM_PROVIDER is configured in .env.")
            print("To enable LLM mode: copy .env.example to .env and set LLM_PROVIDER & LLM_API_KEY.")
            print("Proceeding with deterministic rule-based engine.")
            use_llm = False

    # 4. Run Orchestrator
    print("\n" + "-" * 70)
    print(">>> Starting CareerMesh Multi-Agent Workflow...")
    print("-" * 70)

    def progress_callback(step: int, msg: str):
        print(f"  [{step}/6] {msg}")

    try:
        orchestrator = CareerMeshOrchestrator(use_llm_if_available=use_llm)
        result = orchestrator.run_workflow(
            resume_input=resume_input,
            job_input=job_input,
            is_resume_file=is_resume_file,
            is_job_file=is_job_file,
            timeline_weeks=timeline_weeks,
            available_hours_per_week=available_hours,
            progress_callback=progress_callback,
        )
    except FileParsingError as fpe:
        print(f"\n[File Error]: {str(fpe)}")
        sys.exit(1)
    except OrchestrationError as oe:
        print(f"\n[Workflow Error]: {str(oe)}")
        sys.exit(1)
    except Exception as e:
        print(f"\n[Unexpected Error]: {str(e)}")
        sys.exit(1)

    # 5. Display Terminal Summary
    gap = result.skill_gap_analysis
    job = result.job_analysis
    advisor = result.advisor_report

    print("\n" + "=" * 70)
    print("                   CAREERMESH SUMMARY REPORT")
    print("=" * 70)
    print(f"Target Role           : {job.job_title} ({job.seniority_level})")
    print(f"Overall Role Match    : {gap.overall_match_score}%")
    print(f"Required Skills Match : {gap.required_skills_score}% ({len(gap.demonstrated_required)}/{len(job.required_skills)} demonstrated)")
    print(f"Preferred Skills Match: {gap.preferred_skills_score}% ({len(gap.demonstrated_preferred)}/{len(job.preferred_skills)} demonstrated)")
    print(f"Execution Engine      : {result.execution_mode.upper()} Mode")
    print("-" * 70)

    print("\n[DEMONSTRATED REQUIRED SKILLS]:")
    if gap.demonstrated_required:
        for s in gap.demonstrated_required:
            print(f"  [OK] {s}")
    else:
        print("  None fully demonstrated with project evidence.")

    print("\n[PRIORITY SKILL GAPS TO LEARN]:")
    if gap.priority_gaps:
        for g in gap.priority_gaps:
            print(f"  [GAP] {g}")
    else:
        print("  [OK] No critical skill gaps found for this role.")

    print("\n[RECOMMENDED ACTION PLAN]:")
    for act in advisor.prioritized_action_plan:
        print(f"  * {act}")

    print("\n[CAPSTONE PORTFOLIO DELIVERABLE]:")
    print(f"  {result.roadmap.portfolio_project_idea}")

    print("\n" + "=" * 70)
    print("FULL REPORTS GENERATED SUCCESSFULLY:")
    print(f"  * Markdown Report : {result.markdown_report_file}")
    print(f"  * JSON Data Report: {result.json_report_file}")
    print("=" * 70 + "\n")


if __name__ == "__main__":
    main()
