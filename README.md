# CareerMesh — 6-Agent AI Career Assistant

CareerMesh is a Python-based career assistant that analyzes a resume against a job description, identifies skill gaps, recommends learning resources, creates a personalized learning roadmap, and generates a career report.

## Features

- **Resume Analyst:** Extracts skills, education, projects, and experience.
- **Job Description Analyst:** Identifies required and preferred skills.
- **Skill Gap Analyst:** Compares resume skills with job requirements and calculates a match score.
- **Learning Resource Agent:** Recommends relevant learning resources.
- **Career Roadmap Agent:** Creates a weekly learning plan based on available study hours.
- **Career Advisor Agent:** Generates career recommendations and a final report.

### Additional Features

- Supports PDF, DOCX, and TXT resumes.
- Provides a command-line interface (CLI).
- Includes an optional Streamlit web interface.
- Supports rule-based processing without an API key.
- Offers optional LLM integration when configured.
- Generates Markdown and JSON reports.

## Project Workflow

```text
Resume + Job Description
          |
          v
  1. Resume Analyst
          |
          v
  2. Job Analyst
          |
          v
  3. Skill Gap Analyst
          |
          v
  4. Learning Resource Agent
          |
          v
  5. Career Roadmap Agent
          |
          v
  6. Career Advisor Agent
          |
          v
   Markdown + JSON Reports
```

## Technology Stack

- **Language:** Python
- **Data Validation:** Pydantic
- **Document Processing:** pypdf, python-docx
- **Configuration:** python-dotenv
- **Optional Web Interface:** Streamlit
- **Testing:** pytest

## Project Structure

```text
career-mesh/
├── main.py
├── app.py
├── orchestrator.py
├── config.py
├── models.py
├── agents/
│   ├── resume_agent.py
│   ├── job_agent.py
│   ├── skill_gap_agent.py
│   ├── resource_agent.py
│   ├── roadmap_agent.py
│   └── advisor_agent.py
├── services/
│   ├── file_parser.py
│   ├── resource_catalog.py
│   ├── report_generator.py
│   └── llm_provider.py
├── data/
├── tests/
├── output/
├── requirements.txt
├── .env.example
└── README.md
```

## Installation



Open PowerShell in the project directory and run:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
```

## How to Run

### 1. Start the CLI application

```powershell
python main.py
```

Choose one of the available options:

- **1:** Run the sample demo.
- **2:** Analyze your own resume and a target job description.
- **3:** Exit.

For a custom assessment, provide your resume text or the full path to your PDF, DOCX, or TXT resume. Then select or provide a job description and configure your learning timeline.

**Note:** Enter a normal Windows file path, for example:

`C:\Users\bhuvi\Downloads\resume.pdf`

### 2. Run the optional web interface

```powershell
streamlit run app.py
```

### 3. Run automated tests

```powershell
python -m pytest -v
```

## Output

After a successful assessment, CareerMesh generates:

- **Markdown report (`.md`):** Readable career analysis, skill gaps, resources, roadmap, and recommendations.
- **JSON report (`.json`):** Structured assessment data for further processing.

Reports are saved in the `output/` directory.

## AI Engine

CareerMesh supports two processing modes:

- **Rule-Based Mode:** Uses predefined skill patterns and comparison logic. Works without an API key.
- **LLM Mode:** Optional language-model processing that requires a supported provider and valid configuration.

To configure LLM mode, review `.env.example` and `services/llm_provider.py`. Follow the provider-specific setup instructions and keep API keys private.

## Limitations

- Rule-based skill extraction depends on predefined patterns and keywords.
- A skill missing from a resume is not necessarily a skill the candidate lacks.
- Match scores indicate alignment with the analyzed job requirements; they do not predict hiring outcomes.
- Scanned PDFs may require OCR support.
- Learning roadmaps are estimates and should be adapted to individual progress.
- LLM functionality depends on correct provider configuration and availability.

## Future Enhancements

- Improved semantic resume and job matching.
- Additional LLM providers.
- Verified online learning-resource search.
- More job-role templates.
- Enhanced resume improvement suggestions.

## Author

**Bhuvanesh Himmat Deore**

CareerMesh is an educational project demonstrating modular Python agents, career-skill analysis, workflow orchestration, and automated report generation.