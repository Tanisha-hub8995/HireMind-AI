from datetime import datetime
from typing import Dict, List
from sqlalchemy.orm import Session

from app.models.assessment import Assessment, AssessmentSectionResult
from app.models.interview import Interview
from app.models.progress import UserProgress
from app.models.user import User
from app.schemas.badge import BadgeItem, BadgesResponse, UserLevelInfo


class BadgeService:
    """Calculates user XP, progressive levels (1 to 5), and 1-to-5 star badges

    across Assessments, AI Interviews, DSA, Aptitude, Professional Knowledge, and Communication.
    """

    def get_user_badges_and_level(self, db: Session, user: User) -> BadgesResponse:
        user_id = user.id

        # Fetch assessment records
        assessments = (
            db.query(Assessment)
            .filter(Assessment.user_id == user_id, Assessment.status == "COMPLETED")
            .all()
        )
        completed_assessments_count = len(assessments)
        best_assessment_pct = max([a.percentage for a in assessments if a.percentage is not None], default=0.0)

        # Fetch section records
        section_results = (
            db.query(AssessmentSectionResult)
            .join(Assessment, AssessmentSectionResult.assessment_id == Assessment.id)
            .filter(Assessment.user_id == user_id)
            .all()
        )

        dsa_pct = max([s.percentage for s in section_results if "DSA" in str(s.section).upper()], default=0.0)
        apt_pct = max([s.percentage for s in section_results if "APTITUDE" in str(s.section).upper()], default=0.0)
        prof_pct = max([s.percentage for s in section_results if "PROFESSIONAL" in str(s.section).upper()], default=0.0)

        # Fetch interview records
        interviews = (
            db.query(Interview)
            .filter(Interview.user_id == user_id, Interview.status == "COMPLETED")
            .all()
        )
        completed_interviews_count = len(interviews)
        best_interview_score = max([i.score for i in interviews if i.score is not None], default=0.0)

        # Fetch user progress metrics
        progress_records = db.query(UserProgress).filter(UserProgress.user_id == user_id).all()
        comm_scores = [p.value for p in progress_records if p.metric_name == "communication_score"]
        best_comm_score = max(comm_scores, default=0.0)

        # Calculate XP
        xp = (
            (completed_assessments_count * 200)
            + int(best_assessment_pct * 3)
            + (completed_interviews_count * 300)
            + int(best_interview_score * 4)
            + int(best_comm_score * 2)
            + (len(section_results) * 50)
        )

        # Level Calculation (Level 1 to 5)
        level_tiers = [
            (1, "Apprentice Engineer (1-Star)", 0, 500),
            (2, "Practitioner Specialist (2-Star)", 500, 1200),
            (3, "Senior Problem Solver (3-Star)", 1200, 2500),
            (4, "Lead Systems Architect (4-Star)", 2500, 4500),
            (5, "Grandmaster Principal (5-Star)", 4500, 10000),
        ]

        current_level = 1
        level_title = "Apprentice Engineer (1-Star)"
        xp_min = 0
        xp_next = 500

        for lvl, title, l_min, l_next in level_tiers:
            if xp >= l_min:
                current_level = lvl
                level_title = title
                xp_min = l_min
                xp_next = l_next

        xp_in_level = max(0, xp - xp_min)
        level_range = max(1, xp_next - xp_min)
        level_progress_pct = min(100.0, round((xp_in_level / level_range) * 100.0, 1))

        # Build 1-5 Star Badges
        def calc_stars(score: float, completed_count: int = 1) -> int:
            if completed_count == 0 or score <= 0:
                return 0
            if score >= 90.0:
                return 5
            if score >= 80.0:
                return 4
            if score >= 65.0:
                return 3
            if score >= 45.0:
                return 2
            return 1

        def get_tier(stars: int) -> str:
            tiers = {0: "LOCKED", 1: "BRONZE", 2: "SILVER", 3: "GOLD", 4: "PLATINUM", 5: "DIAMOND"}
            return tiers.get(stars, "BRONZE")

        dsa_stars = calc_stars(dsa_pct, len([s for s in section_results if "DSA" in str(s.section).upper()]))
        apt_stars = calc_stars(apt_pct, len([s for s in section_results if "APTITUDE" in str(s.section).upper()]))
        prof_stars = calc_stars(prof_pct, len([s for s in section_results if "PROFESSIONAL" in str(s.section).upper()]))
        interview_stars = calc_stars(best_interview_score, completed_interviews_count)
        comm_stars = calc_stars(best_comm_score, completed_interviews_count)
        overall_stars = min(5, max(current_level, (completed_assessments_count > 0) + (completed_interviews_count > 0)))

        badges: List[BadgeItem] = [
            BadgeItem(
                id="badge_dsa_mastery",
                name="DSA Algorithm Virtuoso",
                category="DSA",
                stars=dsa_stars,
                max_stars=5,
                tier=get_tier(dsa_stars),
                icon="⚡",
                description="Demonstrate excellence in Data Structures, Trees, Graphs, and Algorithmic Complexity.",
                unlocked=dsa_stars > 0,
                progress_percentage=min(100.0, round(dsa_pct, 1)),
                current_value=round(dsa_pct, 1),
                target_value=100.0,
                unlocked_at=datetime.utcnow() if dsa_stars > 0 else None,
            ),
            BadgeItem(
                id="badge_aptitude_master",
                name="Quantitative & Logic Prodigy",
                category="APTITUDE",
                stars=apt_stars,
                max_stars=5,
                tier=get_tier(apt_stars),
                icon="🧠",
                description="Master mathematical problem solving, numerical ability, and logical reasoning.",
                unlocked=apt_stars > 0,
                progress_percentage=min(100.0, round(apt_pct, 1)),
                current_value=round(apt_pct, 1),
                target_value=100.0,
                unlocked_at=datetime.utcnow() if apt_stars > 0 else None,
            ),
            BadgeItem(
                id="badge_prof_knowledge",
                name="System & Engineering Specialist",
                category="PROFESSIONAL",
                stars=prof_stars,
                max_stars=5,
                tier=get_tier(prof_stars),
                icon="🛠️",
                description="Show deep domain knowledge in Python, SQL, Caching, APIs, and System Design.",
                unlocked=prof_stars > 0,
                progress_percentage=min(100.0, round(prof_pct, 1)),
                current_value=round(prof_pct, 1),
                target_value=100.0,
                unlocked_at=datetime.utcnow() if prof_stars > 0 else None,
            ),
            BadgeItem(
                id="badge_interview_ace",
                name="AI Mock Interview Champion",
                category="INTERVIEW",
                stars=interview_stars,
                max_stars=5,
                tier=get_tier(interview_stars),
                icon="🎯",
                description="Excel in AI-driven technical interviews with adaptive questioning and follow-ups.",
                unlocked=interview_stars > 0,
                progress_percentage=min(100.0, round(best_interview_score, 1)),
                current_value=round(best_interview_score, 1),
                target_value=100.0,
                unlocked_at=datetime.utcnow() if interview_stars > 0 else None,
            ),
            BadgeItem(
                id="badge_communication_pro",
                name="Technical Articulation Pro",
                category="COMMUNICATION",
                stars=comm_stars,
                max_stars=5,
                tier=get_tier(comm_stars),
                icon="🎙️",
                description="Deliver structured, articulate, and clear engineering explanations under pressure.",
                unlocked=comm_stars > 0,
                progress_percentage=min(100.0, round(best_comm_score, 1)),
                current_value=round(best_comm_score, 1),
                target_value=100.0,
                unlocked_at=datetime.utcnow() if comm_stars > 0 else None,
            ),
            BadgeItem(
                id="badge_level_mastery",
                name="Omnitrix Milestone Titan",
                category="OVERALL",
                stars=current_level,
                max_stars=5,
                tier=get_tier(current_level),
                icon="⭐",
                description=f"Advance through milestones to achieve up to 5-Star Grandmaster status. Current Level: {current_level}.",
                unlocked=True,
                progress_percentage=level_progress_pct,
                current_value=float(xp),
                target_value=float(xp_next),
                unlocked_at=user.created_at or datetime.utcnow(),
            ),
        ]

        unlocked_badges = [b for b in badges if b.unlocked]
        total_stars_earned = sum(b.stars for b in badges)

        level_info = UserLevelInfo(
            current_level=current_level,
            level_title=level_title,
            stars_earned=total_stars_earned,
            total_stars_possible=len(badges) * 5,
            xp=xp,
            xp_to_next_level=max(0, xp_next - xp),
            level_progress_percentage=level_progress_pct,
            badges_unlocked_count=len(unlocked_badges),
            total_badges_count=len(badges),
        )

        return BadgesResponse(
            user_id=user.id,
            level_info=level_info,
            badges=badges,
            recent_unlocked_badges=unlocked_badges[:3],
        )
