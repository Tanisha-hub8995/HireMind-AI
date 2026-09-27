from io import BytesIO

from app.schemas.resume import GeneratedResume


def build_resume_pdf(resume: GeneratedResume) -> bytes:
    from reportlab.lib.pagesizes import LETTER
    from reportlab.lib.styles import getSampleStyleSheet
    from reportlab.lib.units import inch
    from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer

    buffer = BytesIO()
    document = SimpleDocTemplate(
        buffer,
        pagesize=LETTER,
        rightMargin=0.65 * inch,
        leftMargin=0.65 * inch,
        topMargin=0.6 * inch,
        bottomMargin=0.6 * inch,
        title=f"Resume - {resume.name}",
        author="AI Interviewer",
    )
    styles = getSampleStyleSheet()
    title_style = styles["Title"]
    heading_style = styles["Heading2"]
    body_style = styles["BodyText"]
    story = [
        Paragraph(resume.name, title_style),
        Paragraph(resume.headline or "Professional", heading_style),
        Spacer(1, 8),
    ]

    def add_section(title: str, content: list[str]):
        if not content:
            return
        story.append(Paragraph(title, heading_style))
        for item in content:
            story.append(Paragraph(item, body_style))
            story.append(Spacer(1, 4))
        story.append(Spacer(1, 6))

    if resume.summary:
        add_section("Professional Summary", [resume.summary])
    add_section("Skills", [", ".join(resume.skills)] if resume.skills else [])
    add_section("Experience", [_format_item(item) for item in resume.experience])
    add_section("Projects", [_format_item(item) for item in resume.projects])
    add_section("Education", [_format_item(item) for item in resume.education])
    add_section("Certifications", resume.certifications)
    add_section("Achievements", resume.achievements)
    add_section("Domains", [", ".join(resume.domains)] if resume.domains else [])

    document.build(story)
    return buffer.getvalue()


def _format_item(item: dict) -> str:
    values = []
    for key, value in item.items():
        if value is None or value == "":
            continue
        if isinstance(value, list):
            value = ", ".join(str(entry) for entry in value)
        values.append(f"<b>{key.replace('_', ' ').title()}:</b> {value}")
    return "<br/>".join(values)
