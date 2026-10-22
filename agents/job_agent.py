"""
agents/job_agent.py - Agent 2: Job Description Analyst

Extracts job title, seniority, job family, mandatory vs preferred skills,
and identifies ambiguous requirements across multiple job families.
"""

import re
from typing import List, Dict, Tuple, Optional
from models import JobAnalysis
from config import SKILL_NORMALIZATION_MAP
from services.file_parser import parse_text_input, parse_file
from services.llm_provider import BaseLLMProvider, LLMExecutionError


class JobAnalystAgent:
    """Agent 2: Analyzes job descriptions into validated structured models."""

    def __init__(self, llm_provider: Optional[BaseLLMProvider] = None):
        self.llm_provider = llm_provider

    def analyze(self, input_source: str, is_file_path: bool = False) -> JobAnalysis:
        """
        Main entry point for Agent 2.
        input_source: raw text or file path.
        """
        if not input_source or not str(input_source).strip():
            return JobAnalysis(
                job_title="Unspecified Role",
                seniority_level="Not Specified",
                job_family="Other",
                ambiguous_requirements=["Empty job description provided."],
                extraction_mode="rule_based",
            )

        if is_file_path:
            raw_text, _ = parse_file(input_source)
        else:
            try:
                raw_text = parse_text_input(input_source)
            except FileParsingError:
                return JobAnalysis(
                    job_title="Unspecified Role",
                    seniority_level="Not Specified",
                    job_family="Other",
                    ambiguous_requirements=["Empty job description provided."],
                    extraction_mode="rule_based",
                )

        if self.llm_provider and self.llm_provider.is_available():
            try:
                return self._analyze_with_llm(raw_text)
            except LLMExecutionError as e:
                print(f"[Job Analyst Warning]: LLM analysis failed ({str(e)}). Falling back to rule-based extraction.")

        return self._analyze_rule_based(raw_text)

    def _analyze_rule_based(self, text: str) -> JobAnalysis:
        """Deterministic rule-based job description parser."""
        lines = [line.strip() for line in text.splitlines() if line.strip()]

        # 1. Job Title & Family
        title, family = self._extract_title_and_family(lines, text)

        # 2. Seniority Level
        seniority = self._extract_seniority(text)

        # 3. Experience Expectations
        exp_expectation = self._extract_experience_expectation(text)

        # 4. Mandatory vs Preferred Skills Extraction
        required_skills, preferred_skills, ambiguous = self._segment_and_extract_skills(text)

        # 5. Extract Responsibilities
        responsibilities = self._extract_responsibilities(text)

        return JobAnalysis(
            job_title=title,
            seniority_level=seniority,
            job_family=family,
            responsibilities=responsibilities,
            required_skills=required_skills,
            preferred_skills=preferred_skills,
            tools_and_frameworks=required_skills + preferred_skills,
            experience_expectations=exp_expectation,
            ambiguous_requirements=ambiguous,
            extraction_mode="rule_based",
        )

    def _extract_title_and_family(self, lines: List[str], text: str) -> Tuple[str, str]:
        title = "AI Engineer"
        family = "AI Engineer"

        title_patterns = [
            (r"\b(?:senior|lead|principal|junior|staff)?\s*ai engineer\b", "AI Engineer", "AI Engineer"),
            (r"\b(?:machine learning|ml)\s*engineer\b", "Machine Learning Engineer", "ML Engineer"),
            (r"\bdata scientist\b", "Data Scientist", "Data Scientist"),
            (r"\bdata analyst\b", "Data Analyst", "Data Analyst"),
            (r"\bpython developer\b", "Python Developer", "Python Developer"),
            (r"\bllm engineer\b", "LLM Engineer", "AI Engineer"),
            (r"\bgenerative ai engineer\b", "Generative AI Engineer", "AI Engineer"),
            (r"\bdata engineer\b", "Data Engineer", "Data Scientist"),
        ]

        # Check first 5 lines for direct title line
        found_in_header = False
        for line in lines[:5]:
            low = line.lower()
            for pat, detected_title, detected_family in title_patterns:
                if re.search(pat, low):
                    clean_title = re.sub(r"^(?:job\s+title|title)\s*:\s*", "", line.strip(), flags=re.IGNORECASE)
                    title = clean_title or detected_title
                    family = detected_family
                    found_in_header = True
                    break
            if found_in_header:
                break

        if not found_in_header:
            # Fallback to search whole text
            low_text = text.lower()
            for pat, detected_title, detected_family in title_patterns:
                if re.search(pat, low_text):
                    title = detected_title
                    family = detected_family
                    break

        return title, family

    def _extract_seniority(self, text: str) -> str:
        low = text.lower()
        if re.search(r"\b(?:lead|principal|staff|architect)\b", low):
            return "Lead / Principal"
        if re.search(r"\b(?:senior|sr\.?)\b", low):
            return "Senior"
        if re.search(r"\b(?:junior|jr\.?|entry[- ]level|associate|intern|freshers?)\b", low):
            return "Junior / Entry-Level"
        if re.search(r"\b(?:mid[- ]level|intermediate)\b", low):
            return "Mid-Level"
        return "Mid-Level (Standard)"

    def _extract_experience_expectation(self, text: str) -> str:
        match = re.search(r"(\d+[\+]?\s*(?:to|-)\s*\d+|\d+\+?)\s*(?:years|yrs)(?:\s*of\s*experience)?", text, re.IGNORECASE)
        if match:
            return f"{match.group(0).strip()} expected in relevant field"
        return "Experience level not strictly quantified in years."

    def _segment_and_extract_skills(self, text: str) -> Tuple[List[str], List[str], List[str]]:
        """Separates required/mandatory qualifications from preferred/nice-to-have."""
        required_skills = set()
        preferred_skills = set()
        ambiguous = []

        low_text = text.lower()

        # Check for vague buzzwords
        vague_patterns = [
            r"ninja", r"rockstar", r"guru", r"expert in all modern ai",
            r"must know everything", r"10\+ years of experience with (?:chatgpt|gpt-4|langchain)",
        ]
        for vp in vague_patterns:
            if re.search(vp, low_text):
                ambiguous.append(f"Vague requirement detected: '{vp}'")

        # Split into preferred vs required sections
        preferred_split = re.split(r"(?:preferred|nice to have|plus|bonus|optional|good to have):?", low_text)
        required_part = preferred_split[0]
        preferred_part = preferred_split[1] if len(preferred_split) > 1 else ""

        for keyword, canonical_name in SKILL_NORMALIZATION_MAP.items():
            pattern = rf"(?<!\w){re.escape(keyword)}(?!\w)"

            in_pref = bool(re.search(pattern, preferred_part))
            in_req = bool(re.search(pattern, required_part))

            if in_req:
                required_skills.add(canonical_name)
            elif in_pref:
                preferred_skills.add(canonical_name)

        # Remove overlap (if required, it's not merely preferred)
        preferred_skills = preferred_skills.difference(required_skills)

        # Flag if no skills were recognized
        if not required_skills and not preferred_skills:
            ambiguous.append("No standard technical skills were explicitly identified. Review role text manually.")

        return sorted(list(required_skills)), sorted(list(preferred_skills)), ambiguous

    def _extract_responsibilities(self, text: str) -> List[str]:
        responsibilities = []
        for line in text.splitlines():
            clean = line.strip()
            if not clean:
                continue
            if re.match(r"^[\*\-\•]\s+", clean) and len(clean) > 20:
                responsibilities.append(re.sub(r"^[\*\-\•]\s*", "", clean))
        return responsibilities[:5]

    def _analyze_with_llm(self, text: str) -> JobAnalysis:
        prompt = (
            "Analyze this job description. Extract job_title, seniority_level, job_family, responsibilities, "
            "required_skills (mandatory), preferred_skills (nice-to-have), experience_expectations, "
            "and any ambiguous_requirements.\n\n"
            f"Job Description:\n{text}"
        )
        schema_desc = (
            '{"job_title": "string", "seniority_level": "string", "job_family": "string", '
            '"responsibilities": ["string"], "required_skills": ["string"], "preferred_skills": ["string"], '
            '"experience_expectations": "string", "ambiguous_requirements": ["string"]}'
        )

        data = self.llm_provider.generate_json(prompt, schema_desc)

        # Normalize skills
        def norm_list(skills):
            res = set()
            for s in skills:
                low = s.strip().lower()
                norm = SKILL_NORMALIZATION_MAP.get(low, s.strip())
                res.add(norm)
            return sorted(list(res))

        req_skills = norm_list(data.get("required_skills", []))
        pref_skills = norm_list(data.get("preferred_skills", []))

        return JobAnalysis(
            job_title=data.get("job_title", "AI Engineer"),
            seniority_level=data.get("seniority_level", "Mid-Level"),
            job_family=data.get("job_family", "AI Engineer"),
            responsibilities=data.get("responsibilities", []),
            required_skills=req_skills,
            preferred_skills=pref_skills,
            tools_and_frameworks=req_skills + pref_skills,
            experience_expectations=data.get("experience_expectations", ""),
            ambiguous_requirements=data.get("ambiguous_requirements", []),
            extraction_mode="llm",
        )
