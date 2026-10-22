"""
agents/resume_agent.py - Agent 1: Resume Analyst

Extracts structured profile data, skills, evidence, education, and projects
from candidate resumes (pasted text, TXT, PDF, DOCX).
Never hallucinates skills that are absent from the resume.
"""

import re
from typing import List, Dict, Optional, Tuple
from pathlib import Path

from models import ResumeAnalysis, SkillEvidence
from config import SKILL_NORMALIZATION_MAP, SKILL_CATEGORIES
from services.file_parser import parse_file, parse_text_input, FileParsingError
from services.llm_provider import BaseLLMProvider, LLMExecutionError


class ResumeAnalystAgent:
    """Agent 1: Analyzes resumes into validated structured models."""

    def __init__(self, llm_provider: Optional[BaseLLMProvider] = None):
        self.llm_provider = llm_provider

    def analyze(self, input_source: str, is_file_path: bool = False) -> ResumeAnalysis:
        """
        Main entry point for Agent 1.
        input_source: raw text or path to file (.txt, .pdf, .docx).
        """
        extracted_text = ""
        file_warning = None

        if not input_source or not str(input_source).strip():
            return ResumeAnalysis(
                summary="Resume input is empty.",
                missing_or_unreadable=["No readable text found in resume."],
                extraction_mode="rule_based",
            )

        if is_file_path:
            extracted_text, metadata = parse_file(input_source)
            file_warning = metadata.get("warning")
        else:
            try:
                extracted_text = parse_text_input(input_source)
            except FileParsingError:
                return ResumeAnalysis(
                    summary="Resume input is empty.",
                    missing_or_unreadable=["No readable text found in resume."],
                    extraction_mode="rule_based",
                )

        # Use LLM if configured and available
        if self.llm_provider and self.llm_provider.is_available():
            try:
                return self._analyze_with_llm(extracted_text, file_warning)
            except LLMExecutionError as e:
                # Notify and fall back to rule-based
                print(f"[Resume Analyst Warning]: LLM analysis failed ({str(e)}). Falling back to rule-based extraction.")

        # Default: deterministic rule-based analysis
        return self._analyze_rule_based(extracted_text, file_warning)

    def _analyze_rule_based(self, text: str, file_warning: Optional[str] = None) -> ResumeAnalysis:
        """Rule-based parsing using regex, heuristics, and section analysis."""
        lines = [line.strip() for line in text.splitlines() if line.strip()]

        # 1. Contact info & Name extraction heuristics
        name = self._extract_candidate_name(lines)
        email = self._extract_email(text)

        # 2. Section segmentation
        sections = self._segment_sections(text)

        # 3. Skills extraction and evidence mapping
        skills, skill_cats, evidence_records = self._extract_skills_and_evidence(text, sections)

        # 4. Education, Experience, Projects, Certifications
        education = self._extract_bullets(sections.get("education", ""))
        experience = self._extract_bullets(sections.get("experience", ""))
        projects = self._extract_bullets(sections.get("projects", ""))
        certifications = self._extract_bullets(sections.get("certifications", ""))

        # 5. Missing / Unreadable check
        missing_sections = []
        if not education:
            missing_sections.append("Education section not clearly identified")
        if not experience:
            missing_sections.append("Work/Internship experience not clearly identified")
        if not projects:
            missing_sections.append("Projects section not clearly identified")
        if file_warning:
            missing_sections.append(file_warning)

        # 6. Summary construction
        skills_count = len(skills)
        summary = (
            f"Candidate profile with {skills_count} verified technical skills detected across "
            f"{len(skill_cats)} domains. "
            f"{'Identified projects and practical achievements.' if projects else 'Limited project evidence provided.'}"
        )

        return ResumeAnalysis(
            candidate_name=name,
            contact_email=email,
            education=education,
            experience=experience,
            projects=projects,
            certifications=certifications,
            skills=skills,
            skill_categories=skill_cats,
            evidence_records=evidence_records,
            summary=summary,
            missing_or_unreadable=missing_sections,
            extraction_mode="rule_based",
        )

    def _extract_candidate_name(self, lines: List[str]) -> Optional[str]:
        """Candidate name is usually the first non-contact line without common heading words."""
        heading_keywords = {"resume", "curriculum", "vitae", "cv", "profile", "contact", "experience", "education"}
        for line in lines[:5]:
            clean = line.strip()
            # If line has no email, no phone, <= 4 words, alphabetic
            if not re.search(r"[@\d]", clean) and len(clean.split()) <= 4:
                if not any(kw in clean.lower() for kw in heading_keywords):
                    return clean
        return None

    def _extract_email(self, text: str) -> Optional[str]:
        match = re.search(r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+", text)
        return match.group(0) if match else None

    def _segment_sections(self, text: str) -> Dict[str, str]:
        """Segments text into known resume headers."""
        section_headers = {
            "education": r"(?:education|academic|qualifications|university)",
            "experience": r"(?:work experience|professional experience|experience|employment|internships)",
            "projects": r"(?:projects|key projects|academic projects|portfolio)",
            "skills": r"(?:skills|technical skills|technologies|tools|competencies)",
            "certifications": r"(?:certifications|certificates|licenses|courses)",
        }

        # Find boundaries
        lines = text.splitlines()
        found_sections: Dict[str, List[str]] = {"other": []}
        current_section = "other"

        for line in lines:
            line_clean = line.strip().lower()
            matched_header = None
            if len(line_clean) < 35 and (line.isupper() or line.strip().endswith(":") or len(line.split()) <= 3):
                for sec, pattern in section_headers.items():
                    if re.search(rf"\b{pattern}\b", line_clean):
                        matched_header = sec
                        break

            if matched_header:
                current_section = matched_header
                if current_section not in found_sections:
                    found_sections[current_section] = []
            else:
                if current_section not in found_sections:
                    found_sections[current_section] = []
                found_sections[current_section].append(line)

        return {sec: "\n".join(lines).strip() for sec, lines in found_sections.items() if lines}

    def _extract_bullets(self, section_text: str) -> List[str]:
        if not section_text:
            return []
        items = []
        for line in section_text.splitlines():
            clean = line.strip()
            if not clean:
                continue
            # Remove bullet symbols
            clean = re.sub(r"^[\*\-\•\–\d\.\)]\s*", "", clean).strip()
            if len(clean) > 8:
                items.append(clean)
        return items[:6]  # top items to keep summary focused

    def _extract_skills_and_evidence(
        self, full_text: str, sections: Dict[str, str]
    ) -> Tuple[List[str], Dict[str, List[str]], List[SkillEvidence]]:
        """Identifies skills and flags explicit evidence from projects/experience."""
        detected_skills = set()
        evidence_list = []
        lowered_full = full_text.lower()

        # Check skills section vs projects section
        projects_text = sections.get("projects", "").lower()
        experience_text = sections.get("experience", "").lower()

        for keyword, canonical_name in SKILL_NORMALIZATION_MAP.items():
            pattern = rf"(?<!\w){re.escape(keyword)}(?!\w)"
            match_full = re.search(pattern, lowered_full)

            if match_full:
                detected_skills.add(canonical_name)

                # Check if demonstrated with explicit evidence in projects or experience
                in_project = bool(re.search(pattern, projects_text))
                in_exp = bool(re.search(pattern, experience_text))

                if in_project or in_exp:
                    context_source = "Projects" if in_project else "Work Experience"
                    evidence_list.append(
                        SkillEvidence(
                            skill_name=canonical_name,
                            category=self._categorize_skill(canonical_name),
                            evidence_type="explicit",
                            context=f"Demonstrated in candidate {context_source} section.",
                        )
                    )
                else:
                    evidence_list.append(
                        SkillEvidence(
                            skill_name=canonical_name,
                            category=self._categorize_skill(canonical_name),
                            evidence_type="inferred",
                            context="Mentioned in skills summary list without explicit project description.",
                        )
                    )

        sorted_skills = sorted(list(detected_skills))

        # Categorize
        skill_categories: Dict[str, List[str]] = {}
        for category, cat_skills in SKILL_CATEGORIES.items():
            matched_in_cat = [s for s in sorted_skills if s in cat_skills]
            if matched_in_cat:
                skill_categories[category] = matched_in_cat

        # Any leftover skills go to "Other"
        categorized_set = {s for cat in skill_categories.values() for s in cat}
        uncategorized = [s for s in sorted_skills if s not in categorized_set]
        if uncategorized:
            skill_categories["Other Technical Skills"] = uncategorized

        return sorted_skills, skill_categories, evidence_list

    def _categorize_skill(self, skill_name: str) -> str:
        for cat, skills in SKILL_CATEGORIES.items():
            if skill_name in skills:
                return cat
        return "Other"

    def _analyze_with_llm(self, text: str, file_warning: Optional[str] = None) -> ResumeAnalysis:
        prompt = (
            "Analyze this candidate resume. Extract candidate name, email, education, work experience, "
            "projects, certifications, and technical skills. Only include skills explicitly mentioned in the resume. "
            "Do NOT invent any skills.\n\n"
            f"Resume Text:\n{text}"
        )
        schema_desc = (
            '{"candidate_name": "string", "contact_email": "string", "education": ["string"], '
            '"experience": ["string"], "projects": ["string"], "certifications": ["string"], '
            '"skills": ["string"], "summary": "string"}'
        )

        llm_data = self.llm_provider.generate_json(prompt, schema_desc)

        # Normalize returned skills
        raw_skills = llm_data.get("skills", [])
        normalized_skills = set()
        for s in raw_skills:
            low = s.strip().lower()
            norm = SKILL_NORMALIZATION_MAP.get(low, s.strip())
            normalized_skills.add(norm)

        sorted_skills = sorted(list(normalized_skills))

        # Categorize
        skill_categories = {}
        for category, cat_skills in SKILL_CATEGORIES.items():
            matched = [s for s in sorted_skills if s in cat_skills]
            if matched:
                skill_categories[category] = matched

        evidence_records = [
            SkillEvidence(
                skill_name=s,
                category=self._categorize_skill(s),
                evidence_type="explicit",
                context="Identified via LLM resume parsing.",
            )
            for s in sorted_skills
        ]

        missing = []
        if file_warning:
            missing.append(file_warning)

        return ResumeAnalysis(
            candidate_name=llm_data.get("candidate_name"),
            contact_email=llm_data.get("contact_email"),
            education=llm_data.get("education", []),
            experience=llm_data.get("experience", []),
            projects=llm_data.get("projects", []),
            certifications=llm_data.get("certifications", []),
            skills=sorted_skills,
            skill_categories=skill_categories,
            evidence_records=evidence_records,
            summary=llm_data.get("summary", "LLM-extracted resume profile."),
            missing_or_unreadable=missing,
            extraction_mode="llm",
        )
