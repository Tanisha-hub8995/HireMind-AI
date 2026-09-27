from collections import Counter
import re


class SkillExtractor:
    """Normalize and extract skills from parsed resume text."""

    def __init__(self):
        self.normalized_map = {
            "python": "Python",
            "fastapi": "FastAPI",
            "sql": "SQL",
            "postgresql": "PostgreSQL",
            "javascript": "JavaScript",
            "react": "React",
            "node": "Node.js",
            "typescript": "TypeScript",
            "ai": "AI",
            "machine learning": "Machine Learning",
            "data analysis": "Data Analysis",
            "excel": "Excel",
            "power bi": "Power BI",
            "aws": "AWS",
            "docker": "Docker",
            "kubernetes": "Kubernetes",
            "java": "Java",
            "csharp": "C#",
            "c++": "C++",
            "django": "Django",
            "flask": "Flask",
            "pandas": "Pandas",
            "numpy": "NumPy",
            "scikit": "Scikit-learn",
            "spark": "Spark",
            "tableau": "Tableau",
            "communication": "Communication",
            "leadership": "Leadership",
            "problem solving": "Problem Solving",
            "api": "API",
            "mongodb": "MongoDB",
            "redis": "Redis",
            "testing": "Testing",
            "analytics": "Analytics",
            "statistics": "Statistics",
            "research": "Research",
            "security": "Security",
            "cybersecurity": "Cybersecurity",
        }

    def extract(self, text: str):
        tokens = re.findall(r"[a-zA-Z0-9+#.-]+", text.lower())
        found = Counter()

        for token in tokens:
            for skill_key, normalized in self.normalized_map.items():
                if token == skill_key or skill_key in token:
                    found[normalized] += 1

        return [skill for skill, _ in found.most_common()]

    def normalize(self, skills):
        normalized = []
        seen = set()
        for skill in skills:
            key = skill.lower().strip()
            mapped = self.normalized_map.get(key, (skill.strip()))
            if mapped not in seen:
                normalized.append(mapped)
                seen.add(mapped)
        return normalized
