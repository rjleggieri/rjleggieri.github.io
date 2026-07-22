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
    PageBreak,
    PageTemplate,
    Paragraph,
    Spacer,
)


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "output" / "pdf" / "Robert-Leggieri-Resume.pdf"
PUBLIC_COPY = ROOT / "public" / "docs" / "Robert-Leggieri-Resume.pdf"

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
            fontSize=24,
            leading=27,
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
            spaceAfter=9,
        )
    )
    styles.add(
        ParagraphStyle(
            name="Section",
            parent=styles["Heading2"],
            fontName="Helvetica-Bold",
            fontSize=10.5,
            leading=13,
            textColor=INK,
            borderColor=ORANGE,
            borderWidth=0,
            borderPadding=0,
            spaceBefore=7,
            spaceAfter=5,
            keepWithNext=True,
        )
    )
    styles.add(
        ParagraphStyle(
            name="Summary",
            parent=styles["BodyText"],
            fontName="Helvetica",
            fontSize=9.2,
            leading=12.3,
            textColor=INK,
            spaceAfter=3,
        )
    )
    styles.add(
        ParagraphStyle(
            name="Skills",
            parent=styles["BodyText"],
            fontName="Helvetica",
            fontSize=8.4,
            leading=11,
            textColor=INK,
            leftIndent=0,
            spaceAfter=2.5,
        )
    )
    styles.add(
        ParagraphStyle(
            name="ProjectTitle",
            parent=styles["Heading3"],
            fontName="Helvetica-Bold",
            fontSize=9.4,
            leading=11.5,
            textColor=INK,
            spaceBefore=5,
            spaceAfter=2,
            keepWithNext=True,
        )
    )
    styles.add(
        ParagraphStyle(
            name="ProjectMeta",
            parent=styles["Normal"],
            fontName="Helvetica-Oblique",
            fontSize=7.8,
            leading=9.5,
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
            fontSize=8.35,
            leading=10.8,
            textColor=INK,
            leftIndent=11,
            firstLineIndent=-7,
            bulletIndent=0,
            spaceAfter=1.8,
        )
    )
    styles.add(
        ParagraphStyle(
            name="ExperienceTitle",
            parent=styles["Heading3"],
            fontName="Helvetica-Bold",
            fontSize=9.6,
            leading=12,
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
            fontSize=8,
            leading=10,
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
            fontSize=8.7,
            leading=11.3,
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
    styles = build_styles()

    doc = BaseDocTemplate(
        str(OUTPUT),
        pagesize=LETTER,
        leftMargin=0.58 * inch,
        rightMargin=0.58 * inch,
        topMargin=0.48 * inch,
        bottomMargin=0.55 * inch,
        title="Robert Leggieri - Resume",
        author="Robert Leggieri",
        subject="Applied AI, machine learning, and technology leadership",
    )
    frame = Frame(doc.leftMargin, doc.bottomMargin, doc.width, doc.height, id="main")
    doc.addPageTemplates(PageTemplate(id="resume", frames=[frame], onPage=page_footer))

    story = [
        Paragraph("Robert Leggieri", styles["Name"]),
        Paragraph("APPLIED AI  |  MACHINE LEARNING  |  TECHNOLOGY LEADERSHIP", styles["Positioning"]),
        Paragraph(
            "Columbia, MD  |  (240) 446-8143  |  "
            + link("mailto:rjleggieri@gmail.com", "rjleggieri@gmail.com")
            + "  |  "
            + link("https://www.linkedin.com/in/rjleggieri/", "LinkedIn")
            + "  |  "
            + link("https://github.com/rjleggieri", "GitHub")
            + "  |  "
            + link("https://rjleggieri.github.io/", "Portfolio"),
            styles["Contact"],
        ),
        *section_rule("Professional Summary", styles),
        Paragraph(
            "Technology leader and applied AI practitioner with over two decades of systems ownership and graduate training in artificial intelligence. Builds secure, auditable systems across natural language processing, speech, computer vision, and data engineering. Combines hands-on model implementation with operational judgment, security awareness, and cross-functional delivery.",
            styles["Summary"],
        ),
        *section_rule("Technical Skills", styles),
        Paragraph("<b>AI / ML:</b> PyTorch, TensorFlow / Keras, scikit-learn, Hugging Face Transformers, CNNs, multimodal learning, model evaluation, LoRA / QLoRA", styles["Skills"]),
        Paragraph("<b>Data / Engineering:</b> Python, NumPy, Pandas, OpenCV, SQL / SQLite, REST APIs, OAuth 2.0 / PKCE, ETL pipelines, pytest, Git", styles["Skills"]),
        Paragraph("<b>Systems / Automation:</b> PowerShell, Windows Server, network and security operations, workflow automation, vendor and infrastructure strategy", styles["Skills"]),
        *section_rule("Selected AI Projects", styles),
        project(
            "Text-Prosody Alignment: The \"I'm Fine\" Effect",
            "Case Studies in Machine Learning, The University of Texas at Austin",
            [
                "Designed the Alignment Discrepancy Score (ADS) to quantify differences between text-derived sentiment and audio-derived prosody in a shared valence-arousal space using DAIC-WOZ interview data.",
                "Observed approximately 0.62 AUC for elevated PHQ-8 classification, above audio-only baselines; documented the exploratory, nonclinical scope and need for external validation.",
                "Built " + link("https://github.com/rjleggieri/text-prosody-evidence", "text-prosody-evidence") + ", a public dataset-neutral reference implementation for leakage-aware grouping, nested evaluation, calibration sensitivity, reliability, bootstrap intervals, provenance, and auditable evidence manifests.",
            ],
            styles,
        ),
        project(
            "BQE CORE AI Data Connector",
            "Professional project, Gutschick, Little & Weber, P.A.  |  " + link("https://github.com/rjleggieri/bqe-core-reporting-poc", "GitHub"),
            [
                "Built a governed read-only ingestion layer that transforms BQE CORE operational and financial data into normalized, auditable structures for downstream AI-assisted analysis.",
                "Implemented OAuth Authorization Code with PKCE, validated endpoints, secure credential storage, pagination, retries, deduplication, incremental synchronization, and raw-response audit preservation.",
                "Created a tested SQLite analytical model and reconciliation workflow so model-driven reporting can remain traceable to source-system evidence.",
            ],
            styles,
        ),
        project(
            "PraxiCom: Affect-Aware Simulated Patient",
            "UT Austin NURSING-AI Challenge  |  " + link("https://github.com/rjleggieri/ut-nursing-ai", "GitHub") + "  |  " + link("https://youtu.be/jZb3aR0x7cI", "Demo"),
            [
                "Developed a voice-based simulated patient system with nursing-faculty guidance for practicing emotionally complex, patient-centered clinical communication.",
                "Built React student and faculty interfaces, a Node.js / Socket.IO session relay, YAML-authored patient personas, Hume EVI voice integration, transcript visibility, faculty chat, and structured evaluation.",
                "Designed the academic prototype around synthetic patients and observable faculty oversight; no protected health information was used.",
            ],
            styles,
        ),
        PageBreak(),
        *section_rule("Selected AI Projects - Continued", styles),
        project(
            "Advances in Deep Learning - Four-Project Series",
            "The University of Texas at Austin",
            [
                "Implemented memory-efficient fine-tuning with mixed precision, LoRA, 4-bit quantization, and QLoRA to reduce memory requirements while maintaining downstream performance.",
                "Built patch-level autoencoding, Binary Spherical Quantization, and autoregressive latent modeling for generative image compression and compact representations.",
                "Adapted smaller language models for mathematical reasoning through structured prompting, custom generation strategies, and parameter-efficient fine-tuning.",
                "Generated nearly one million grounded vision-language question-answer pairs from SuperTuxKart game state for object identity, counting, track recognition, and ego-centric spatial reasoning.",
            ],
            styles,
        ),
        project(
            "Debiasing an NLI Model",
            "AI 388 Natural Language Processing Final Project, The University of Texas at Austin",
            [
                "Applied dataset cartography to identify examples associated with spurious shortcuts in MNLI, then implemented loss re-weighting informed by training dynamics.",
                "Evaluated the model on adversarial and out-of-domain examples and observed better generalization from the re-weighted training strategy.",
            ],
            styles,
        ),
        project(
            "Additional Applied ML Coursework",
            "The University of Texas at Austin",
            [
                "Fact-checked LLM outputs against Wikipedia using lexical similarity and DeBERTa-v3 textual entailment, then added overlap-based pruning and fine-grained error analysis.",
                "Implemented character-level Transformer language models with self-attention and positional encoding, achieving the required perplexity of 7 or lower within the course training budget.",
                "Built MLP, cross-attention Transformer, and CNN waypoint planners for autonomous driving in SuperTuxKart, alongside image classification, road segmentation, and depth-estimation pipelines.",
                "Developed perceptron, logistic regression, and Deep Averaging Network classifiers while exploring feature design, pretrained embeddings, batching, spelling robustness, and generalization.",
            ],
            styles,
        ),
        *section_rule("Professional Experience", styles),
        Paragraph("Network Manager - Gutschick, Little & Weber, P.A.", styles["ExperienceTitle"]),
        Paragraph("Burtonsville, MD  |  July 2004 - Present", styles["ExperienceMeta"]),
        *bullets(
            [
                "Own technology operations, network infrastructure, security, automation, vendor strategy, and long-range planning for an engineering firm supporting more than 40 users.",
                "Use Python and PowerShell to streamline workflows and integrate systems while preserving reliability, maintainability, and appropriate access controls.",
                "Partner with engineering and administrative teams to translate evolving business requirements into scalable, cost-conscious technology solutions.",
            ],
            styles,
        ),
        *section_rule("Education", styles),
        Paragraph("<b>The University of Texas at Austin</b> - M.S., Artificial Intelligence, GPA: 4.0  |  Expected August 2026", styles["Education"]),
        Paragraph("<b>University of Maryland Global Campus</b> - B.S., Data Science, Summa Cum Laude  |  May 2024", styles["Education"]),
    ]

    doc.build(story)
    PUBLIC_COPY.write_bytes(OUTPUT.read_bytes())


if __name__ == "__main__":
    generate()
