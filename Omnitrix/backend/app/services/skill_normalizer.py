import re

from sqlalchemy.orm import Session

from app.models.resume_skill import ResumeSkill
from app.models.skill import Skill


class SkillNormalizer:
    """Evidence-gates model skills and links them to canonical database skills."""

    aliases = {
        "postgres": "PostgreSQL",
        "postgresql": "PostgreSQL",
        "react.js": "React",
        "reactjs": "React",
        "ml": "Machine Learning",
        "cv": "Computer Vision",
        "python 3": "Python",
    }

    def normalize_name(self, name: str) -> str:
        cleaned = re.sub(r"\s+", " ", name.strip())
        return self.aliases.get(cleaned.lower(), cleaned)

    def validate(self, analysis: dict, resume_text: str) -> dict:
        lowered = resume_text.lower()
        valid_skills = []
        for skill in analysis.get("skills", []):
            name = self.normalize_name(skill.get("name", ""))
            evidence = (skill.get("evidence") or "").strip()
            if not name or (name.lower() not in lowered and evidence.lower() not in lowered):
                continue
            valid_skills.append({
                **skill,
                "name": name,
                "evidence": evidence or name,
            })
        return {**analysis, "skills": valid_skills}

    def persist(self, db: Session, resume_id: int, analysis: dict) -> list[dict]:
        persisted = []
        for item in analysis.get("skills", []):
            name = self.normalize_name(item["name"])
            skill = db.query(Skill).filter(Skill.canonical_name == name).first()
            if skill is None:
                skill = Skill(
                    canonical_name=name,
                    category=item.get("category"),
                    aliases=[name],
                )
                db.add(skill)
                db.flush()
            link = ResumeSkill(
                resume_id=resume_id,
                skill_id=skill.id,
                evidence=item.get("evidence"),
                confidence=item.get("confidence", 0.0),
            )
            db.add(link)
            persisted.append({"id": skill.id, "name": name, "category": skill.category})
        return persisted
