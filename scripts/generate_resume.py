from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import LETTER
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import (
    BaseDocTemplate,
    Frame,
    HRFlowable,
    KeepTogether,
    PageTemplate,
    Paragraph,
    Spacer,
)


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "output" / "pdf" / "Robert-Leggieri-Resume.pdf"
PUBLIC_COPY = ROOT / "public" / "docs" / "Robert-Leggieri-Resume.pdf"
GITHUB_PAGES_COPY = ROOT / "docs" / "Robert-Leggieri-Resume.pdf"

INK = colors.HexColor("#17201F")
MUTED = colors.HexColor("#555E5A")
ORANGE = colors.HexColor("#AE4F00")
LINE = colors.HexColor("#C9C6BD")


def link(url: str, text: str) -> str:
    return f'<link href="{url}" color="#17201F"><u>{text}</u></link>'


def build_styles():
    styles = getSampleStyleSheet()
    styles.add(
        ParagraphStyle(
            name="Name",
            parent=styles["Normal"],
            fontName="Helvetica-Bold",
            fontSize=22,
            leading=24,
            textColor=INK,
            alignment=TA_CENTER,
            spaceAfter=3,
        )
    )
    styles.add(
        ParagraphStyle(
            name="Positioning",
            parent=styles["Normal"],
            fontName="Helvetica-Bold",
            fontSize=8.5,
            leading=10.5,
            tracking=0.8,
            textColor=ORANGE,
            alignment=TA_CENTER,
            spaceAfter=5,
        )
    )
    styles.add(
        ParagraphStyle(
            name="Contact",
            parent=styles["Normal"],
            fontName="Helvetica",
            fontSize=8.2,
            leading=10.5,
            textColor=MUTED,
            alignment=TA_CENTER,
            spaceAfter=5,
        )
    )
    styles.add(
        ParagraphStyle(
            name="Section",
            parent=styles["Heading2"],
            fontName="Helvetica-Bold",
            fontSize=10,
            leading=11.5,
            textColor=INK,
            borderColor=ORANGE,
            borderWidth=0,
            borderPadding=0,
            spaceBefore=4,
            spaceAfter=3,
            keepWithNext=True,
        )
    )
    styles.add(
        ParagraphStyle(
            name="Summary",
            parent=styles["BodyText"],
            fontName="Helvetica",
            fontSize=9.5,
            leading=12,
            textColor=INK,
            spaceAfter=3,
        )
    )
    styles.add(
        ParagraphStyle(
            name="Skills",
            parent=styles["BodyText"],
            fontName="Helvetica",
            fontSize=9,
            leading=11.5,
            textColor=INK,
            leftIndent=0,
            spaceAfter=1.5,
        )
    )
    styles.add(
        ParagraphStyle(
            name="ProjectTitle",
            parent=styles["Heading3"],
            fontName="Helvetica-Bold",
            fontSize=10,
            leading=12,
            textColor=INK,
            spaceBefore=3,
            spaceAfter=1,
            keepWithNext=True,
        )
    )
    styles.add(
        ParagraphStyle(
            name="ProjectMeta",
            parent=styles["Normal"],
            fontName="Helvetica-Oblique",
            fontSize=8,
            leading=10,
            textColor=MUTED,
            spaceAfter=2,
            keepWithNext=True,
        )
    )
    styles.add(
        ParagraphStyle(
            name="ResumeBullet",
            parent=styles["BodyText"],
            fontName="Helvetica",
            fontSize=9,
            leading=11.3,
            textColor=INK,
            leftIndent=11,
            firstLineIndent=-7,
            bulletIndent=0,
            spaceBefore=2,
            spaceAfter=1,
        )
    )
    styles.add(
        ParagraphStyle(
            name="ExperienceTitle",
            parent=styles["Heading3"],
            fontName="Helvetica-Bold",
            fontSize=9.1,
            leading=10.7,
            textColor=INK,
            spaceBefore=4,
            spaceAfter=1,
            keepWithNext=True,
        )
    )
    styles.add(
        ParagraphStyle(
            name="ExperienceMeta",
            parent=styles["Normal"],
            fontName="Helvetica-Oblique",
            fontSize=7.5,
            leading=8.7,
            textColor=MUTED,
            spaceAfter=3,
            keepWithNext=True,
        )
    )
    styles.add(
        ParagraphStyle(
            name="Education",
            parent=styles["BodyText"],
            fontName="Helvetica",
            fontSize=9,
            leading=11.5,
            textColor=INK,
            spaceAfter=3,
        )
    )
    return styles


def section_rule(title: str, styles):
    return [
        Paragraph(title.upper(), styles["Section"]),
        HRFlowable(width="100%", thickness=0.7, color=ORANGE, spaceBefore=0, spaceAfter=3),
    ]


def bullets(items, styles):
    return [Paragraph("- " + item, styles["ResumeBullet"]) for item in items]


def project(title: str, meta: str, items, styles):
    content = [
        Paragraph(title, styles["ProjectTitle"]),
        Paragraph(meta, styles["ProjectMeta"]),
        *bullets(items, styles),
    ]
    return KeepTogether(content)


def page_footer(canvas, doc):
    canvas.saveState()
    canvas.setStrokeColor(LINE)
    canvas.setLineWidth(0.4)
    canvas.line(doc.leftMargin, 0.42 * inch, LETTER[0] - doc.rightMargin, 0.42 * inch)
    canvas.setFont("Helvetica", 7)
    canvas.setFillColor(MUTED)
    canvas.drawString(doc.leftMargin, 0.27 * inch, "Robert Leggieri")
    canvas.drawRightString(LETTER[0] - doc.rightMargin, 0.27 * inch, f"Page {doc.page}")
    canvas.restoreState()


def generate():
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    PUBLIC_COPY.parent.mkdir(parents=True, exist_ok=True)
    GITHUB_PAGES_COPY.parent.mkdir(parents=True, exist_ok=True)
    styles = build_styles()

    doc = BaseDocTemplate(
        str(OUTPUT),
        pagesize=LETTER,
        leftMargin=0.58 * inch,
        rightMargin=0.58 * inch,
        topMargin=0.38 * inch,
        bottomMargin=0.48 * inch,
        title="Robert Leggieri - Resume",
        author="Robert Leggieri",
        subject="Graduate AI training, AI project experience, and professional business systems experience",
    )
    frame = Frame(doc.leftMargin, doc.bottomMargin, doc.width, doc.height, id="main")
    doc.addPageTemplates(PageTemplate(id="resume", frames=[frame], onPage=page_footer))

    story = [
        Paragraph("Robert Leggieri", styles["Name"]),
        Paragraph("APPLIED AI PROJECT WORK | BUSINESS SYSTEMS EXPERIENCE", styles["Positioning"]),
        Paragraph(
            "Columbia, MD  |  (240) 446-8143  |  "
            + link("mailto:rjleggieri@gmail.com", "rjleggieri@gmail.com")
            + "  |  " + link("https://www.linkedin.com/in/rjleggieri/", "LinkedIn")
            + "  |  " + link("https://github.com/rjleggieri", "GitHub")
            + "  |  " + link("https://rjleggieri.github.io/", "Portfolio"), styles["Contact"]),
        *section_rule("Summary", styles),
        Paragraph("M.S. in Artificial Intelligence with project experience in NLP, model training and evaluation, and AI service integration. More than twenty years managing business technology, automating workflows, and supporting users. Seeking opportunities to contribute to applied AI, NLP, and research software alongside researchers and engineers.", styles["Summary"]),
        *section_rule("Technical Skills", styles),
        Paragraph("<b>Models / experimentation:</b> Python, PyTorch, Hugging Face Transformers, scikit-learn, LoRA / QLoRA", styles["Skills"]),
        Paragraph("<b>Data / evaluation:</b> NumPy, pandas, SQL / SQLite, grouped evaluation, calibration, pytest, Git", styles["Skills"]),
        Paragraph("<b>Software / integration:</b> REST APIs, ETL, React, Node.js, Socket.IO, PowerShell", styles["Skills"]),
        *section_rule("Selected AI and Software Projects", styles),
        project("NLP Robustness through Training-Data Analysis", "Graduate NLP project, UT Austin  |  " + link("https://rjleggieri.github.io/docs/Making-DeBERTa-Smarter.pdf", "Paper"), [
            "Instrumented DeBERTa training on 392,702 MNLI examples across five epochs; implemented a Hugging Face callback, weighted dataset, Trainer override, and category-weighted cross-entropy.",
            "Measured HANS accuracy of 78.59% versus 77.49% at baseline (+1.10 points), with MNLI accuracy of 88.47% versus 88.91%; analyzed adversarial subcases and generalization trade-offs."
        ], styles),
        project("PraxiCom: Faculty-Directed Voice Simulation", "Academic prototype, UT Austin NURSING-AI Challenge, Spring 2025  |  " + link("https://github.com/rjleggieri/ut-nursing-ai", "GitHub"), [
            "Built React student/faculty interfaces and a Node.js / Socket.IO relay for Hume EVI voice sessions, with nursing-faculty guidance.",
            "Added configurable YAML patient personas, a faculty-defined evaluation rubric, session monitoring, and local export of transcripts, chat, scores, and notes."
        ], styles),
        project("Text-Prosody Study and Evaluation Software", "Graduate study and independent software project  |  " + link("https://rjleggieri.github.io/docs/Text-Prosody-Misalignment.pdf", "Report") + "  |  " + link("https://github.com/rjleggieri/text-prosody-evidence", "GitHub"), [
            "Built alignment, pretrained affect-model inference, and session-feature extraction across 32,401 utterances from 189 interviews; documented measurement and evaluation limitations.",
            "Extended the study into grouped evaluation, calibration, and provenance software. A public EmoBank text benchmark improved valence RMSE from 0.4276 to 0.3908."
        ], styles),
        project("BQE CORE Connector: Business Data for Planning", "Professional project, GLW  |  " + link("https://github.com/rjleggieri/bqe-core-ai-data-connector", "GitHub"), [
            "Built a read-only connector for authorized project, time, expense, and billing records; normalized data into SQLite for reporting and planning.",
            "Implemented OAuth PKCE, permission-aware incremental sync, retries, deduplication, and validation; generated management briefs and traceable AI-context exports."
        ], styles),
        *section_rule("Professional Experience", styles),
        Paragraph("Network Manager - Gutschick, Little &amp; Weber, P.A.", styles["ExperienceTitle"]),
        Paragraph("Burtonsville, MD  |  July 2004 - Present", styles["ExperienceMeta"]),
        *bullets([
            "Automate workflows with Python and PowerShell; integrate business systems and translate user requirements into practical technical solutions.",
            "Manage technology operations, security, vendors, and infrastructure planning for an engineering firm supporting more than 40 users.",
            "Organize and deliver software and AI training; create instructional videos and written guides, and provide demonstrations and one-on-one guidance."
        ], styles),
        *section_rule("Education", styles),
        Paragraph("<b>The University of Texas at Austin</b> - M.S., Artificial Intelligence, GPA 4.0  |  August 2026", styles["Education"]),
        Paragraph("<b>University of Maryland Global Campus</b> - B.S., Data Science, Summa Cum Laude  |  May 2024", styles["Education"]),
    ]

    doc.build(story)
    PUBLIC_COPY.write_bytes(OUTPUT.read_bytes())
    GITHUB_PAGES_COPY.write_bytes(OUTPUT.read_bytes())


if __name__ == "__main__":
    generate()
