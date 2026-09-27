from app.services.job_matcher import JobMatcher


class CareerRecommendationEngine:
    """Generate career suggestions from candidate skills and role requirements."""

    def __init__(self):
        self.matcher = JobMatcher()
        self.role_catalog = {
            "backend_developer": {
                "skills": ["Python", "FastAPI", "SQL", "PostgreSQL", "API", "Docker"],
                "description": "Build and maintain server-side systems and APIs."
            },
            "data_analyst": {
                "skills": ["SQL", "Python", "Excel", "Power BI", "Statistics", "Analytics"],
                "description": "Analyze business data and generate insights."
            },
            "ai_engineer": {
                "skills": ["Python", "AI", "Machine Learning", "Data Analysis", "SQL", "API"],
                "description": "Build AI-driven products and intelligent systems."
            },
            "full_stack_developer": {
                "skills": ["Python", "JavaScript", "React", "FastAPI", "SQL", "API"],
                "description": "Work across frontend and backend product development."
            },
        }

    def recommend(self, candidate_skills):
        recommendations = []
        for role_name, payload in self.role_catalog.items():
            result = self.matcher.match(candidate_skills, payload["skills"])
            recommendations.append({
                "role": role_name,
                "description": payload["description"],
                "match_score": result["match_score"],
                "matched_skills": result["matched_skills"],
                "missing_skills": result["missing_skills"],
            })

        recommendations.sort(key=lambda item: item["match_score"], reverse=True)
        return recommendations

    def recommend_for_job(self, candidate_skills, job_requirements):
        result = self.matcher.match(candidate_skills, job_requirements)
        return {
            "match_score": result["match_score"],
            "matched_skills": result["matched_skills"],
            "missing_skills": result["missing_skills"],
            "extra_skills": result["extra_skills"],
        }
