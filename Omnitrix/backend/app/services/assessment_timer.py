import asyncio

from app.database.database import SessionLocal
from app.models.assessment import Assessment
from app.models.assessment_section import AssessmentSectionResult
from app.database.enums import AssessmentStatus

from app.api.assessment import (
    utc_now,
    submit_current_section,
)


async def assessment_timer_loop():
    """
    Background loop that checks active assessments
    and automatically submits expired sections.
    """

    while True:

        try:
            with SessionLocal() as db:

                now = utc_now()

                # Find all active sections whose timer has expired.
                expired_sections = (
                    db.query(AssessmentSectionResult)
                    .join(
                        Assessment,
                        Assessment.id
                        == AssessmentSectionResult.assessment_id,
                    )
                    .filter(
                        Assessment.status
                        == AssessmentStatus.IN_PROGRESS,

                        AssessmentSectionResult.started_at.isnot(None),

                        AssessmentSectionResult.submitted_at.is_(None),

                        AssessmentSectionResult.deadline.isnot(None),

                        AssessmentSectionResult.deadline <= now,
                    )
                    .all()
                )

                for section_result in expired_sections:

                    try:

                        assessment = (
                            db.query(Assessment)
                            .filter(
                                Assessment.id
                                == section_result.assessment_id
                            )
                            .first()
                        )

                        if assessment is None:
                            continue

                        if (
                            assessment.status
                            != AssessmentStatus.IN_PROGRESS
                        ):
                            continue

                        # The section_result we found is already
                        # the expired active section.
                        submit_current_section(
                            db=db,
                            assessment=assessment,
                            section_result=section_result,
                        )

                        db.commit()

                    except Exception as section_error:

                        db.rollback()

                        print(
                            "Error while automatically "
                            "submitting section "
                            f"{section_result.section}: "
                            f"{section_error}"
                        )

        except Exception as e:

            print(
                "Assessment timer database error:",
                e,
            )

        await asyncio.sleep(1)