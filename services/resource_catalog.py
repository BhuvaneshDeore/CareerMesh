"""
services/resource_catalog.py - Curated Learning Resource Catalog

Provides verified, reputable learning resources for technical skills in offline mode.
Optionally verifies URLs online when configured.
"""

from typing import List, Dict, Optional
from models import LearningResource
from config import ENABLE_ONLINE_VERIFICATION


# Curated catalog of real, high-quality, reputable resources
OFFLINE_CATALOG: Dict[str, List[dict]] = {
    "Python": [
        {
            "title": "The Official Python Tutorial",
            "provider": "Python Software Foundation",
            "skill": "Python",
            "difficulty": "Beginner",
            "resource_type": "Official Documentation",
            "url": "https://docs.python.org/3/tutorial/",
            "is_verified": True,
            "why_useful": "The canonical guide covering data structures, modules, OOP, and standard libraries directly from Python's core maintainers.",
        },
        {
            "title": "Real Python Tutorials & Learning Paths",
            "provider": "Real Python",
            "skill": "Python",
            "difficulty": "Intermediate",
            "resource_type": "Practical Tutorial",
            "url": "https://realpython.com/",
            "is_verified": True,
            "why_useful": "High quality, peer-reviewed practical tutorials covering modern Python programming idioms and application architecture.",
        },
    ],
    "PyTorch": [
        {
            "title": "Deep Learning with PyTorch: A 60 Minute Blitz",
            "provider": "PyTorch Foundation",
            "skill": "PyTorch",
            "difficulty": "Beginner",
            "resource_type": "Official Documentation",
            "url": "https://pytorch.org/tutorials/beginner/deep_learning_60min_blitz.html",
            "is_verified": True,
            "why_useful": "Hands-on introduction to Tensors, Autograd, neural networks, and training your first classifier on PyTorch.",
        },
        {
            "title": "Practical Deep Learning for Coders",
            "provider": "Fast.ai",
            "skill": "PyTorch",
            "difficulty": "Intermediate",
            "resource_type": "Interactive Course",
            "url": "https://course.fast.ai/",
            "is_verified": True,
            "why_useful": "Top-down, code-first course building real deep learning models using PyTorch with state-of-the-art results.",
        },
    ],
    "TensorFlow": [
        {
            "title": "TensorFlow Quickstart for Beginners",
            "provider": "TensorFlow Team (Google)",
            "skill": "TensorFlow",
            "difficulty": "Beginner",
            "resource_type": "Official Documentation",
            "url": "https://www.tensorflow.org/tutorials/quickstart/beginner",
            "is_verified": True,
            "why_useful": "Official step-by-step tutorial on building a basic neural network with Keras in TensorFlow.",
        },
    ],
    "Machine Learning": [
        {
            "title": "Machine Learning Specialization",
            "provider": "DeepLearning.AI / Coursera (Andrew Ng)",
            "skill": "Machine Learning",
            "difficulty": "Beginner",
            "resource_type": "Interactive Course",
            "url": "https://www.coursera.org/specializations/machine-learning-introduction",
            "is_verified": True,
            "why_useful": "Industry-standard foundational course on supervised learning, neural networks, decision trees, and best practices.",
        },
    ],
    "Scikit-Learn": [
        {
            "title": "Scikit-Learn User Guide & Getting Started",
            "provider": "Scikit-Learn Developers",
            "skill": "Scikit-Learn",
            "difficulty": "Beginner",
            "resource_type": "Official Documentation",
            "url": "https://scikit-learn.org/stable/getting_started.html",
            "is_verified": True,
            "why_useful": "Clear examples and API patterns for classification, regression, clustering, and data preprocessing pipelines.",
        },
    ],
    "Deep Learning": [
        {
            "title": "Deep Learning Specialization",
            "provider": "DeepLearning.AI (Andrew Ng)",
            "skill": "Deep Learning",
            "difficulty": "Intermediate",
            "resource_type": "Interactive Course",
            "url": "https://www.deeplearning.ai/courses/deep-learning-specialization/",
            "is_verified": True,
            "why_useful": "Covers backpropagation, optimization algorithms (Adam/RMSProp), CNNs, RNNs, and transformer intuition.",
        },
    ],
    "Natural Language Processing (NLP)": [
        {
            "title": "The Hugging Face NLP Course",
            "provider": "Hugging Face",
            "skill": "Natural Language Processing (NLP)",
            "difficulty": "Intermediate",
            "resource_type": "Interactive Course",
            "url": "https://huggingface.co/learn/nlp-course/",
            "is_verified": True,
            "why_useful": "Comprehensive, free, hands-on curriculum on tokenizers, fine-tuning pretrained models, datasets, and pipeline APIs.",
        },
    ],
    "Large Language Models (LLMs)": [
        {
            "title": "Large Language Model Courses & Guides",
            "provider": "Hugging Face / DeepLearning.AI",
            "skill": "Large Language Models (LLMs)",
            "difficulty": "Intermediate",
            "resource_type": "Interactive Course",
            "url": "https://www.deeplearning.ai/short-courses/",
            "is_verified": True,
            "why_useful": "Concise, free micro-courses covering LLM architectures, fine-tuning, embeddings, and prompt patterns.",
        },
    ],
    "LangChain": [
        {
            "title": "LangChain Official Quickstart & Conceptual Guides",
            "provider": "LangChain",
            "skill": "LangChain",
            "difficulty": "Intermediate",
            "resource_type": "Official Documentation",
            "url": "https://python.langchain.com/docs/get_started/introduction",
            "is_verified": True,
            "why_useful": "Step-by-step guide to building retrieval-augmented generation (RAG) chains, agents, and tool integrations.",
        },
    ],
    "Retrieval-Augmented Generation (RAG)": [
        {
            "title": "Building Systems with the ChatGPT API / RAG",
            "provider": "DeepLearning.AI & OpenAI",
            "skill": "Retrieval-Augmented Generation (RAG)",
            "difficulty": "Intermediate",
            "resource_type": "Hands-on Project Guide",
            "url": "https://www.deeplearning.ai/short-courses/building-systems-with-chatgpt/",
            "is_verified": True,
            "why_useful": "Practical architecture for combining vector embeddings, chunking strategies, and generation for production Q&A systems.",
        },
    ],
    "Docker": [
        {
            "title": "Docker Getting Started Guide",
            "provider": "Docker Inc.",
            "skill": "Docker",
            "difficulty": "Beginner",
            "resource_type": "Official Documentation",
            "url": "https://docs.docker.com/get-started/",
            "is_verified": True,
            "why_useful": "Explains images, containers, Dockerfiles, volumes, port forwarding, and multi-container Docker Compose files.",
        },
    ],
    "FastAPI": [
        {
            "title": "FastAPI Tutorial - User Guide",
            "provider": "Tiangolo / FastAPI",
            "skill": "FastAPI",
            "difficulty": "Beginner",
            "resource_type": "Official Documentation",
            "url": "https://fastapi.tiangolo.com/tutorial/",
            "is_verified": True,
            "why_useful": "Build high-performance REST APIs with automatic OpenAPI/Swagger documentation, Pydantic validation, and async support.",
        },
    ],
    "MLOps": [
        {
            "title": "Made With ML: Production Machine Learning",
            "provider": "Goku Mohandas",
            "skill": "MLOps",
            "difficulty": "Intermediate",
            "resource_type": "Hands-on Project Guide",
            "url": "https://madewithml.com/",
            "is_verified": True,
            "why_useful": "End-to-end practical walkthrough of experiment tracking, testing, CI/CD, serving, and monitoring ML models in production.",
        },
    ],
    "SQL": [
        {
            "title": "PostgreSQL Tutorial & SQL Exercises",
            "provider": "PostgreSQL Tutorial / SQLBolt",
            "skill": "SQL",
            "difficulty": "Beginner",
            "resource_type": "Interactive Course",
            "url": "https://sqlbolt.com/",
            "is_verified": True,
            "why_useful": "Interactive browser-based SQL queries covering SELECT, JOIN, GROUP BY, aggregations, and subqueries.",
        },
    ],
    "Git": [
        {
            "title": "Pro Git Book (Free Online)",
            "provider": "Scott Chacon and Ben Straub / Git-SCM",
            "skill": "Git",
            "difficulty": "Beginner",
            "resource_type": "Book",
            "url": "https://git-scm.com/book/en/v2",
            "is_verified": True,
            "why_useful": "The official open-source book covering branching, merging, rebasing, remote repositories, and collaborative workflows.",
        },
    ],
    "AWS": [
        {
            "title": "AWS Cloud Essentials & Machine Learning Foundations",
            "provider": "Amazon Web Services",
            "skill": "AWS",
            "difficulty": "Beginner",
            "resource_type": "Official Documentation",
            "url": "https://aws.amazon.com/training/digital/",
            "is_verified": True,
            "why_useful": "Learn core AWS cloud building blocks (EC2, S3, IAM) and managed ML services (Amazon SageMaker).",
        },
    ],
}


def verify_url_online(url: str, timeout_seconds: float = 3.0) -> bool:
    """
    Safely checks if a URL is reachable online via HEAD/GET request.
    Only called when ENABLE_ONLINE_VERIFICATION is True.
    """
    try:
        import urllib.request
        req = urllib.request.Request(
            url,
            headers={"User-Agent": "CareerMesh-Resource-Verifier/1.0"}
        )
        with urllib.request.urlopen(req, timeout=timeout_seconds) as response:
            return response.status in (200, 301, 302, 307, 308)
    except Exception:
        return False


def get_resources_for_skill(skill_name: str) -> List[LearningResource]:
    """
    Finds curated learning resources for the given skill.
    If the skill is in our verified catalog, returns those items.
    If not, returns an honest general guide marked as unverified (no fabricated links).
    """
    # Direct match or case-insensitive match in catalog
    matched_items = None
    for key, items in OFFLINE_CATALOG.items():
        if key.lower() == skill_name.lower():
            matched_items = items
            break

    resources = []
    if matched_items:
        for item in matched_items:
            # Check online status if online verification enabled
            is_verified = item.get("is_verified", True)
            if ENABLE_ONLINE_VERIFICATION:
                is_verified = verify_url_online(item["url"])

            resources.append(
                LearningResource(
                    title=item["title"],
                    provider=item["provider"],
                    skill=skill_name,
                    difficulty=item["difficulty"],
                    resource_type=item["resource_type"],
                    url=item["url"],
                    is_verified=is_verified,
                    why_useful=item["why_useful"],
                )
            )
    else:
        # Honest fallback: Do not fabricate a fake course or fake platform link!
        # Provide the official search guidance and mark as unverified.
        search_query = skill_name.replace(" ", "+")
        resources.append(
            LearningResource(
                title=f"Official Documentation & Community Tutorials for {skill_name}",
                provider="Search Query / Official Docs",
                skill=skill_name,
                difficulty="Beginner",
                resource_type="Official Documentation",
                url=f"https://www.google.com/search?q={search_query}+official+documentation+tutorial",
                is_verified=False,  # Explicitly marked unverified
                why_useful=f"Search for the official project repository, documentation, and getting-started tutorials for {skill_name}.",
            )
        )

    return resources
