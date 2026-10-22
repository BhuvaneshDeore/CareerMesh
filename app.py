"""
app.py - CareerMesh: Optional Lightweight Streamlit Web Interface

Provides an interactive GUI for CareerMesh using the same underlying
CareerMeshOrchestrator and 6-agent workflow.
"""

import sys
from pathlib import Path

# Add current directory to Python path
sys.path.insert(0, str(Path(__file__).resolve().parent))

try:
    import streamlit as st
except ImportError:
    print("Streamlit is not installed. To run the web interface, run 'pip install streamlit'.")
    sys.exit(1)

from orchestrator import CareerMeshOrchestrator
from config import BASE_DIR, SAMPLE_JOBS_DIR, OUTPUT_DIR
import json


st.set_page_config(
    page_title="CareerMesh - 6-Agent AI Career Assistant",
    page_icon="🚀",
    layout="wide",
)

st.title("🚀 CareerMesh — 6-Agent AI Career Assistant")
st.markdown(
    "**Multi-Agent Workflow:** Resume Analyst ➔ Job Analyst ➔ Skill Gap Analyst ➔ Resource Agent ➔ Roadmap Agent ➔ Career Advisor"
)

# Sidebar configurations
with st.sidebar:
    st.header("⚙️ Configuration")
    run_mode = st.radio(
        "Run Mode",
        ["Fast Demo (Sample AI Engineer Profile)", "Custom Resume & Job Description"],
    )

    st.subheader("Roadmap Parameters")
    timeline_weeks = st.slider("Target Timeline (Weeks)", min_value=2, max_value=16, value=8, step=2)
    available_hours = st.slider("Available Study Hours / Week", min_value=5, max_value=40, value=15, step=5)

    use_llm = st.checkbox("Enable Optional LLM Mode", value=False, help="Requires LLM_PROVIDER and LLM_API_KEY in .env")

col1, col2 = st.columns(2)

if run_mode == "Fast Demo (Sample AI Engineer Profile)":
    with col1:
        st.subheader("📄 Demo Resume")
        sample_resume_path = BASE_DIR / "data" / "sample_student_resume.txt"
        with open(sample_resume_path, "r", encoding="utf-8") as f:
            demo_resume_text = f.read()
        st.text_area("Resume Content", demo_resume_text, height=300, disabled=True)

    with col2:
        st.subheader("🎯 Demo Job Description")
        sample_job_path = SAMPLE_JOBS_DIR / "ai_engineer.txt"
        with open(sample_job_path, "r", encoding="utf-8") as f:
            demo_job_text = f.read()
        st.text_area("Job Description Content", demo_job_text, height=300, disabled=True)

    resume_input = str(sample_resume_path)
    job_input = str(sample_job_path)
    is_res_file = True
    is_job_file = True

else:
    with col1:
        st.subheader("📄 Your Resume")
        upload_resume = st.file_uploader("Upload Resume (.pdf, .docx, .txt)", type=["pdf", "docx", "txt"])
        paste_resume = st.text_area("Or Paste Resume Text Here", height=200)

        if upload_resume is not None:
            # Save temporary file
            temp_path = OUTPUT_DIR / upload_resume.name
            with open(temp_path, "wb") as f:
                f.write(upload_resume.getbuffer())
            resume_input = str(temp_path)
            is_res_file = True
        else:
            resume_input = paste_resume
            is_res_file = False

    with col2:
        st.subheader("🎯 Target Job Description")
        job_preset = st.selectbox(
            "Select Preset or Custom",
            ["Paste Custom Job Description", "AI Engineer (Preset)", "Data Scientist (Preset)"],
        )

        if job_preset == "AI Engineer (Preset)":
            job_input = str(SAMPLE_JOBS_DIR / "ai_engineer.txt")
            is_job_file = True
            with open(job_input, "r", encoding="utf-8") as f:
                st.text_area("Selected Preset", f.read(), height=200, disabled=True)
        elif job_preset == "Data Scientist (Preset)":
            job_input = str(SAMPLE_JOBS_DIR / "data_scientist.txt")
            is_job_file = True
            with open(job_input, "r", encoding="utf-8") as f:
                st.text_area("Selected Preset", f.read(), height=200, disabled=True)
        else:
            job_input = st.text_area("Paste Target Job Description Here", height=200)
            is_job_file = False

# Action button
if st.button("🚀 Run 6-Agent Assessment", type="primary", use_container_width=True):
    if not resume_input or (not is_res_file and not resume_input.strip()):
        st.error("Please provide a resume before running.")
    elif not job_input or (not is_job_file and not job_input.strip()):
        st.error("Please provide a job description before running.")
    else:
        progress_bar = st.progress(0)
        status_text = st.empty()

        def ui_progress(step: int, msg: str):
            progress_bar.progress(int((step / 6) * 100))
            status_text.text(f"Agent {step}/6: {msg}")

        try:
            orchestrator = CareerMeshOrchestrator(use_llm_if_available=use_llm)
            with st.spinner("Executing multi-agent pipeline..."):
                result = orchestrator.run_workflow(
                    resume_input=resume_input,
                    job_input=job_input,
                    is_resume_file=is_res_file,
                    is_job_file=is_job_file,
                    timeline_weeks=timeline_weeks,
                    available_hours_per_week=available_hours,
                    progress_callback=ui_progress,
                )

            st.success("✅ Multi-Agent Assessment Completed Successfully!")
            progress_bar.progress(100)

            # Display Key Metrics
            gap = result.skill_gap_analysis
            m1, m2, m3, m4 = st.columns(4)
            m1.metric("Overall Match Score", f"{gap.overall_match_score}%")
            m2.metric("Required Skills Match", f"{gap.required_skills_score}%")
            m3.metric("Preferred Skills Match", f"{gap.preferred_skills_score}%")
            m4.metric("Priority Skill Gaps", len(gap.priority_gaps))

            # Tabs for results
            t_overview, t_gaps, t_resources, t_roadmap, t_advisor = st.tabs(
                ["📊 Overview & Matrix", "⚠️ Skill Gaps", "📚 Resources", "🗓️ Roadmap", "💡 Advisor"]
            )

            with t_overview:
                st.subheader("Skill Comparison Matrix")
                matrix_data = [
                    {
                        "Skill": c.skill_name,
                        "Type": "Required" if c.is_required else "Preferred",
                        "Status": c.status,
                        "Evidence": c.resume_evidence or c.notes,
                    }
                    for c in gap.comparisons
                ]
                st.dataframe(matrix_data, use_container_width=True)

            with t_gaps:
                col_g1, col_g2 = st.columns(2)
                with col_g1:
                    st.write("**Demonstrated Skills (Keep)**")
                    for s in gap.demonstrated_required:
                        st.write(f"- ✅ **{s}**")
                with col_g2:
                    st.write("**Priority Skill Gaps (Learn)**")
                    for g in gap.priority_gaps:
                        st.write(f"- ⚠️ **{g}**")

            with t_resources:
                st.subheader("Curated Learning Resources")
                for skill, res_list in result.resource_recommendations.resources_by_skill.items():
                    with st.expander(f"📘 Resources for {skill} ({len(res_list)})"):
                        for r in res_list:
                            st.markdown(f"**[{r.title}]({r.url})** — *{r.provider}* ({r.difficulty})")
                            st.caption(f"{r.resource_type} | Verified: {'Yes' if r.is_verified else 'Unverified'}")
                            st.write(r.why_useful)

            with t_roadmap:
                st.subheader(f"Personalized {timeline_weeks}-Week Roadmap (~{available_hours} hrs/week)")
                st.info(f"💡 Recommended Capstone: {result.roadmap.portfolio_project_idea}")
                for m in result.roadmap.weekly_milestones:
                    with st.expander(f"Week {m.week_number}: {m.title} ({m.estimated_hours} hrs)"):
                        st.write("**Objectives:**")
                        for o in m.learning_objectives:
                            st.write(f"- {o}")
                        st.write(f"**Deliverable:** {m.project_deliverable}")

            with t_advisor:
                st.subheader("Career Advisor Recommendations")
                st.write("**Action Plan:**")
                for a in result.advisor_report.prioritized_action_plan:
                    st.write(f"- {a}")

                st.write("**Resume Improvements:**")
                for r in result.advisor_report.resume_improvement_suggestions:
                    st.write(f"- {r}")

                st.write("**Interview Preparation:**")
                for ip in result.advisor_report.interview_prep_checklist:
                    st.write(f"- {ip}")

            # Download buttons for reports
            st.divider()
            st.subheader("📥 Export Reports")
            with open(result.markdown_report_file, "r", encoding="utf-8") as f:
                st.download_button(
                    "Download Markdown Report",
                    data=f.read(),
                    file_name=Path(result.markdown_report_file).name,
                    mime="text/markdown",
                )

        except Exception as e:
            st.error(f"Assessment error: {str(e)}")
