from typing import Any, Dict
from app.services.resume_parser import ResumeParser
from app.services.skill_extractor import SkillExtractor
from app.services.vector_store import InMemoryVectorStore


class ResumeAnalyzer:
    """Composite resume analysis service for parsing, skill extraction, rich section decomposition,

    education, experience, internships, projects, certifications, achievements, and vectorization.
    """

    def __init__(self):
        self.parser = ResumeParser()
        self.skill_extractor = SkillExtractor()
        self.vector_store = InMemoryVectorStore()

    def analyze(self, text: str, user_id: int | None = None) -> Dict[str, Any]:
        parsed = self.parser.parse(text)
        extracted_skills = self.skill_extractor.extract(text)
        
        # Merge parsed skills with extractor skills
        all_raw_skills = list(dict.fromkeys(extracted_skills + parsed.get("skills", [])))
        normalized_skills = self.skill_extractor.normalize(all_raw_skills)

        # Build skill objects with confidence and category
        skills_objects = []
        for s in normalized_skills:
            category = self._categorize_skill(s)
            skills_objects.append({
                "name": s,
                "category": category,
                "evidence": f"Demonstrated proficiency in {s} within engineering projects and experience.",
                "confidence": 0.95,
            })

        if user_id is not None:
            self.vector_store.add_document(
                user_id,
                text,
                metadata={"skills": normalized_skills},
                section_name="full_resume",
            )

            for section_name, section_text in self.vector_store._split_sections(text):
                if section_name == "full_resume":
                    continue
                self.vector_store.add_document(
                    user_id,
                    section_text,
                    metadata={"skills": normalized_skills, "section_name": section_name},
                    section_name=section_name,
                )

        summary = {
            "name": parsed.get("name") or "Candidate",
            "email": parsed.get("email"),
            "phone": parsed.get("phone"),
            "skills": skills_objects,
            "education": parsed.get("education", []),
            "experience": parsed.get("experience", []),
            "internships": parsed.get("internships", []),
            "projects": parsed.get("projects", []),
            "certifications": parsed.get("certifications", []),
            "achievements": parsed.get("achievements", []),
            "suggested_roles": parsed.get("suggested_roles", []),
            "domains": parsed.get("domains", []),
            "summary": f"Candidate profile highlights strong expertise in {', '.join(normalized_skills[:4]) if normalized_skills else 'Software Engineering'} with proven project delivery across {', '.join(parsed.get('domains', ['Software Development'])[:2])}.",
            "sections": [
                "summary",
                "skills",
                "experience",
                "internships",
                "education",
                "projects",
                "certifications",
                "achievements",
            ],
            "status": "complete",
            "provider": "deterministic-nlp",
        }
        return summary

    def _categorize_skill(self, skill: str) -> str:
        lowered = skill.lower()
        if lowered in ["python", "java", "c++", "c#", "javascript", "typescript", "go", "rust", "ruby", "php"]:
            return "Programming Language"
        if lowered in ["fastapi", "django", "flask", "react", "next.js", "node.js", "express", "spring boot", "tailwind"]:
            return "Framework / Library"
        if lowered in ["sql", "postgresql", "mysql", "mongodb", "redis", "cassandra", "dynamodb"]:
            return "Database & Storage"
        if lowered in ["aws", "azure", "gcp", "docker", "kubernetes", "ci/cd", "git", "linux", "jenkins"]:
            return "Cloud & DevOps"
        if lowered in ["machine learning", "deep learning", "nlp", "computer vision", "tensorflow", "pytorch", "pandas", "numpy", "scikit-learn"]:
            return "AI & Data Science"
        if lowered in ["communication", "leadership", "problem solving", "teamwork", "agile", "scrum"]:
            return "Professional & Soft Skills"
        return "Technical Skill"
