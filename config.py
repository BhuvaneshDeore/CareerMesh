"""
config.py - Central Configuration for CareerMesh

Handles environment variables, scoring weights, paths, and normalization maps.
"""

import os
from pathlib import Path

# Load .env file if available
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# Paths
BASE_DIR = Path(__file__).resolve().parent
OUTPUT_DIR = BASE_DIR / "output"
DATA_DIR = BASE_DIR / "data"
SAMPLE_JOBS_DIR = DATA_DIR / "sample_job_descriptions"

# Ensure output directory exists
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# LLM Configuration
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "").strip().lower()  # "gemini", "openai", or ""
LLM_API_KEY = os.getenv("LLM_API_KEY", "").strip()
LLM_MODEL = os.getenv("LLM_MODEL", "gemini-1.5-flash").strip()
ENABLE_ONLINE_VERIFICATION = os.getenv("ENABLE_ONLINE_VERIFICATION", "false").lower() == "true"

# Scoring Weights
# Required skills account for 70% of overall match score; preferred skills account for 30%.
REQUIRED_SKILLS_WEIGHT = float(os.getenv("REQUIRED_SKILLS_WEIGHT", "0.70"))
PREFERRED_SKILLS_WEIGHT = float(os.getenv("PREFERRED_SKILLS_WEIGHT", "0.30"))

# Evidence Weights
# Fully demonstrated with project/experience: 1.0; Partially demonstrated / mention only: 0.5; Not found: 0.0
EVIDENCE_WEIGHT_DEMONSTRATED = 1.0
EVIDENCE_WEIGHT_PARTIAL = 0.5
EVIDENCE_WEIGHT_NOT_FOUND = 0.0

# Skill Normalization Map: aliases and acronyms to canonical names
SKILL_NORMALIZATION_MAP = {
    # Programming
    "python": "Python",
    "py": "Python",
    "c++": "C++",
    "cpp": "C++",
    "java": "Java",
    "javascript": "JavaScript",
    "typescript": "TypeScript",
    "js": "JavaScript",
    "ts": "TypeScript",
    "r": "R",
    "scala": "Scala",
    "bash": "Bash/Shell",
    "shell": "Bash/Shell",
    "linux": "Linux",

    # Data & Libraries
    "pandas": "Pandas",
    "numpy": "NumPy",
    "scipy": "SciPy",
    "matplotlib": "Matplotlib",
    "seaborn": "Seaborn",
    "sql": "SQL",
    "postgresql": "PostgreSQL",
    "postgres": "PostgreSQL",
    "mysql": "MySQL",
    "mongodb": "MongoDB",
    "redis": "Redis",
    "data analysis": "Data Analysis",
    "statistics": "Statistics",
    "data structures": "Data Structures & Algorithms",
    "dsa": "Data Structures & Algorithms",

    # Machine Learning & Deep Learning
    "machine learning": "Machine Learning",
    "ml": "Machine Learning",
    "deep learning": "Deep Learning",
    "dl": "Deep Learning",
    "scikit-learn": "Scikit-Learn",
    "sklearn": "Scikit-Learn",
    "pytorch": "PyTorch",
    "torch": "PyTorch",
    "tensorflow": "TensorFlow",
    "tf": "TensorFlow",
    "keras": "Keras",
    "xgboost": "XGBoost",
    "lightgbm": "LightGBM",
    "computer vision": "Computer Vision",
    "cv": "Computer Vision",
    "opencv": "OpenCV",
    "nlp": "Natural Language Processing (NLP)",
    "natural language processing": "Natural Language Processing (NLP)",

    # LLMs & Generative AI
    "llm": "Large Language Models (LLMs)",
    "llms": "Large Language Models (LLMs)",
    "large language models": "Large Language Models (LLMs)",
    "generative ai": "Generative AI",
    "genai": "Generative AI",
    "gen ai": "Generative AI",
    "langchain": "LangChain",
    "llamaindex": "LlamaIndex",
    "llama index": "LlamaIndex",
    "rag": "Retrieval-Augmented Generation (RAG)",
    "retrieval-augmented generation": "Retrieval-Augmented Generation (RAG)",
    "prompt engineering": "Prompt Engineering",
    "transformers": "Transformers",
    "hugging face": "Hugging Face",
    "huggingface": "Hugging Face",
    "vector database": "Vector Databases (e.g. Pinecone/Chroma)",
    "chromadb": "Vector Databases (e.g. Pinecone/Chroma)",
    "pinecone": "Vector Databases (e.g. Pinecone/Chroma)",

    # MLOps & Deployment
    "docker": "Docker",
    "kubernetes": "Kubernetes",
    "k8s": "Kubernetes",
    "git": "Git",
    "github": "Git",
    "fastapi": "FastAPI",
    "flask": "Flask",
    "mlops": "MLOps",
    "mlflow": "MLflow",
    "ci/cd": "CI/CD",
    "dvc": "DVC",

    # Cloud
    "aws": "AWS",
    "amazon web services": "AWS",
    "gcp": "GCP",
    "google cloud": "GCP",
    "google cloud platform": "GCP",
    "azure": "Azure",
    "microsoft azure": "Azure",
}

# Skill Categories mapping
SKILL_CATEGORIES = {
    "Programming": ["Python", "C++", "Java", "JavaScript", "TypeScript", "R", "Scala", "Bash/Shell", "Linux"],
    "Data & Analytics": ["Pandas", "NumPy", "SciPy", "Matplotlib", "Seaborn", "SQL", "PostgreSQL", "MySQL", "Data Analysis", "Statistics", "Data Structures & Algorithms"],
    "Machine Learning": ["Machine Learning", "Scikit-Learn", "XGBoost", "LightGBM"],
    "Deep Learning": ["Deep Learning", "PyTorch", "TensorFlow", "Keras", "Computer Vision", "OpenCV", "Natural Language Processing (NLP)"],
    "LLMs & Generative AI": ["Large Language Models (LLMs)", "Generative AI", "LangChain", "LlamaIndex", "Retrieval-Augmented Generation (RAG)", "Prompt Engineering", "Transformers", "Hugging Face", "Vector Databases (e.g. Pinecone/Chroma)"],
    "Deployment & MLOps": ["Docker", "Kubernetes", "Git", "FastAPI", "Flask", "MLOps", "MLflow", "CI/CD", "DVC"],
    "Cloud & Databases": ["AWS", "GCP", "Azure", "MongoDB", "Redis"],
}
