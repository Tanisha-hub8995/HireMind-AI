from collections import Counter


class JobMatcher:
    """Weighted matching between candidate skills and job requirements."""

    def match(self, candidate_skills, job_requirements):
        candidate = {skill.lower().strip() for skill in candidate_skills}
        requirements = {skill.lower().strip() for skill in job_requirements}

        overlap = candidate.intersection(requirements)
        candidate_only = candidate - requirements
        requirement_only = requirements - candidate

        weighted_score = (len(overlap) * 100) / max(len(requirements), 1)
        penalty = (len(requirement_only) * 15) / max(len(requirements), 1)
        score = max(0, min(100, round(weighted_score - penalty, 2)))

        return {
            "match_score": score,
            "matched_skills": sorted(overlap),
            "missing_skills": sorted(requirement_only),
            "extra_skills": sorted(candidate_only),
        }

    def match_resume_sections(self, section_matches, job_requirements):
        sections = []
        for match in section_matches:
            section_result = self.match(match.get("skills", []), job_requirements)
            sections.append({
                "section_name": match.get("section_name"),
                "similarity": match.get("similarity", 0.0),
                "skills": match.get("skills", []),
                "match_score": section_result["match_score"],
                "matched_skills": section_result["matched_skills"],
                "missing_skills": section_result["missing_skills"],
            })
        return sections
