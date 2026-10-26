import io
from datetime import datetime

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import (
    getSampleStyleSheet,
    ParagraphStyle
)
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    PageBreak
)


# =========================================================
# COLORS
# =========================================================

PRIMARY = colors.HexColor("#6C63FF")
SECONDARY = colors.HexColor("#111827")
LIGHT_BG = colors.HexColor("#F8FAFC")
BORDER = colors.HexColor("#E5E7EB")
MUTED = colors.HexColor("#6B7280")


# =========================================================
# SAFE HELPERS
# =========================================================

def safe_text(value, default="N/A"):
    """Convert a value into safe text."""

    if value is None:
        return default

    text = str(value).strip()

    if not text:
        return default

    return text


def safe_list(value):
    """Return a list or an empty list."""

    if isinstance(value, list):
        return value

    return []


def safe_score(value, default=0.0):
    """Convert a value into a float score safely."""

    try:
        return float(value)

    except (TypeError, ValueError):
        return default


# =========================================================
# HEADER
# =========================================================

def add_header(story, styles):

    story.append(
        Paragraph(
            "INTERVIEWAI",
            styles["brand"]
        )
    )

    story.append(
        Paragraph(
            "AI-Powered Interview Performance Report",
            styles["subtitle"]
        )
    )

    story.append(
        Spacer(
            1,
            0.25 * inch
        )
    )


# =========================================================
# SECTION TITLE
# =========================================================

def add_section_title(story, title, styles):

    story.append(
        Spacer(
            1,
            0.18 * inch
        )
    )

    story.append(
        Paragraph(
            title,
            styles["section_title"]
        )
    )

    story.append(
        Spacer(
            1,
            0.08 * inch
        )
    )


# =========================================================
# BULLET LIST
# =========================================================

def add_bullet_list(
    story,
    items,
    styles,
    bullet="•"
):

    items = safe_list(items)

    if not items:

        story.append(
            Paragraph(
                "No data available.",
                styles["normal"]
            )
        )

        return

    for item in items:

        story.append(
            Paragraph(
                f"{bullet} {safe_text(item)}",
                styles["bullet"]
            )
        )

        story.append(
            Spacer(
                1,
                0.04 * inch
            )
        )


# =========================================================
# PDF GENERATOR
# =========================================================

def generate_interview_report(
    average_score,
    job_role,
    interview_type,
    difficulty,
    questions,
    answers,
    feedback,
    interview_insights=None,
    skill_gap_analysis=None,
    improvement_roadmap=None
):

    # -----------------------------------------------------
    # PDF BUFFER
    # -----------------------------------------------------

    buffer = io.BytesIO()

    document = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=42,
        leftMargin=42,
        topMargin=42,
        bottomMargin=42
    )


    # -----------------------------------------------------
    # STYLES
    # -----------------------------------------------------

    styles = getSampleStyleSheet()


    styles.add(
        ParagraphStyle(
            name="brand",
            parent=styles["Title"],
            fontSize=26,
            leading=30,
            alignment=TA_CENTER,
            textColor=PRIMARY,
            spaceAfter=8
        )
    )


    styles.add(
        ParagraphStyle(
            name="subtitle",
            parent=styles["Normal"],
            fontSize=11,
            leading=15,
            alignment=TA_CENTER,
            textColor=MUTED
        )
    )


    styles.add(
        ParagraphStyle(
            name="section_title",
            parent=styles["Heading2"],
            fontSize=16,
            leading=20,
            textColor=SECONDARY,
            spaceBefore=8,
            spaceAfter=8
        )
    )


    styles.add(
        ParagraphStyle(
            name="normal",
            parent=styles["Normal"],
            fontSize=10,
            leading=15,
            textColor=SECONDARY
        )
    )


    styles.add(
        ParagraphStyle(
            name="bullet",
            parent=styles["Normal"],
            fontSize=10,
            leading=15,
            leftIndent=12,
            textColor=SECONDARY
        )
    )


    styles.add(
        ParagraphStyle(
            name="small",
            parent=styles["Normal"],
            fontSize=9,
            leading=13,
            textColor=MUTED
        )
    )


    story = []


    # =====================================================
    # HEADER
    # =====================================================

    add_header(
        story,
        styles
    )


    # =====================================================
    # REPORT DATE
    # =====================================================

    report_date = datetime.now().strftime(
        "%d %B %Y"
    )


    # =====================================================
    # INTERVIEW SUMMARY
    # =====================================================

    add_section_title(
        story,
        "Interview Summary",
        styles
    )


    summary_data = [

        [
            "Target Role",
            safe_text(job_role)
        ],

        [
            "Interview Type",
            safe_text(interview_type)
        ],

        [
            "Difficulty",
            safe_text(difficulty)
        ],

        [
            "Report Date",
            report_date
        ],

        [
            "Questions Answered",
            str(len(safe_list(answers)))
        ]

    ]


    summary_table = Table(
        summary_data,
        colWidths=[
            2.0 * inch,
            4.0 * inch
        ]
    )


    summary_table.setStyle(
        TableStyle(
            [

                (
                    "BACKGROUND",
                    (0, 0),
                    (0, -1),
                    LIGHT_BG
                ),

                (
                    "GRID",
                    (0, 0),
                    (-1, -1),
                    0.5,
                    BORDER
                ),

                (
                    "FONTNAME",
                    (0, 0),
                    (0, -1),
                    "Helvetica-Bold"
                ),

                (
                    "FONTSIZE",
                    (0, 0),
                    (-1, -1),
                    10
                ),

                (
                    "VALIGN",
                    (0, 0),
                    (-1, -1),
                    "MIDDLE"
                ),

                (
                    "TOPPADDING",
                    (0, 0),
                    (-1, -1),
                    8
                ),

                (
                    "BOTTOMPADDING",
                    (0, 0),
                    (-1, -1),
                    8
                )

            ]
        )
    )


    story.append(summary_table)


    # =====================================================
    # OVERALL PERFORMANCE
    # =====================================================

    add_section_title(
        story,
        "Overall Performance",
        styles
    )


    score_value = safe_score(
        average_score
    )


    if score_value >= 8:

        verdict = (
            "Excellent performance. You demonstrate "
            "strong interview readiness."
        )

    elif score_value >= 6:

        verdict = (
            "Good performance with clear strengths and "
            "some areas to improve."
        )

    elif score_value >= 4:

        verdict = (
            "Developing performance. Focused practice "
            "can significantly improve your readiness."
        )

    else:

        verdict = (
            "Your interview skills are still developing. "
            "Regular practice and structured preparation "
            "are recommended."
        )


    score_data = [

        [
            "OVERALL SCORE",
            f"{score_value:.1f}/10"
        ],

        [
            "AI VERDICT",
            verdict
        ]

    ]


    score_table = Table(
        score_data,
        colWidths=[
            2.0 * inch,
            4.0 * inch
        ]
    )


    score_table.setStyle(
        TableStyle(
            [

                (
                    "BACKGROUND",
                    (0, 0),
                    (0, -1),
                    LIGHT_BG
                ),

                (
                    "BOX",
                    (0, 0),
                    (-1, -1),
                    1,
                    PRIMARY
                ),

                (
                    "INNERGRID",
                    (0, 0),
                    (-1, -1),
                    0.5,
                    BORDER
                ),

                (
                    "FONTNAME",
                    (0, 0),
                    (0, -1),
                    "Helvetica-Bold"
                ),

                (
                    "FONTSIZE",
                    (0, 0),
                    (-1, -1),
                    10
                ),

                (
                    "VALIGN",
                    (0, 0),
                    (-1, -1),
                    "MIDDLE"
                ),

                (
                    "TOPPADDING",
                    (0, 0),
                    (-1, -1),
                    10
                ),

                (
                    "BOTTOMPADDING",
                    (0, 0),
                    (-1, -1),
                    10
                )

            ]
        )
    )


    story.append(score_table)


    # =====================================================
    # QUESTION-WISE PERFORMANCE
    # =====================================================

    add_section_title(
        story,
        "Question-wise Performance",
        styles
    )


    feedback_list = safe_list(
        feedback
    )


    question_rows = [

        [
            "Question",
            "Score",
            "Performance"
        ]

    ]


    for index, item in enumerate(
        feedback_list
    ):

        if not isinstance(item, dict):
            continue


        numeric_score = safe_score(
            item.get(
                "score",
                0
            )
        )


        if numeric_score >= 8:

            performance = "Excellent"

        elif numeric_score >= 6:

            performance = "Good"

        elif numeric_score >= 4:

            performance = "Developing"

        else:

            performance = "Needs Improvement"


        question_rows.append(

            [
                f"Question {index + 1}",
                f"{numeric_score:.1f}/10",
                performance
            ]

        )


    if len(question_rows) > 1:

        question_table = Table(
            question_rows,
            colWidths=[
                2.0 * inch,
                1.3 * inch,
                2.7 * inch
            ]
        )


        question_table.setStyle(
            TableStyle(
                [

                    (
                        "BACKGROUND",
                        (0, 0),
                        (-1, 0),
                        PRIMARY
                    ),

                    (
                        "TEXTCOLOR",
                        (0, 0),
                        (-1, 0),
                        colors.white
                    ),

                    (
                        "FONTNAME",
                        (0, 0),
                        (-1, 0),
                        "Helvetica-Bold"
                    ),

                    (
                        "GRID",
                        (0, 0),
                        (-1, -1),
                        0.5,
                        BORDER
                    ),

                    (
                        "FONTSIZE",
                        (0, 0),
                        (-1, -1),
                        9
                    ),

                    (
                        "TOPPADDING",
                        (0, 0),
                        (-1, -1),
                        7
                    ),

                    (
                        "BOTTOMPADDING",
                        (0, 0),
                        (-1, -1),
                        7
                    )

                ]
            )
        )


        story.append(question_table)


    # =====================================================
    # DETAILED FEEDBACK
    # =====================================================

    add_section_title(
        story,
        "Detailed Answer Feedback",
        styles
    )


    for index, item in enumerate(
        feedback_list
    ):

        if not isinstance(item, dict):
            continue


        story.append(

            Paragraph(
                f"<b>Question {index + 1}</b>",
                styles["normal"]
            )

        )


        if index < len(questions):

            story.append(

                Paragraph(
                    safe_text(
                        questions[index]
                    ),
                    styles["normal"]
                )

            )


        story.append(

            Paragraph(
                (
                    f"<b>Score:</b> "
                    f"{safe_text(item.get('score', 'N/A'))}/10"
                ),
                styles["normal"]
            )

        )


        strengths = safe_list(
            item.get(
                "strengths",
                []
            )
        )


        improvements = safe_list(
            item.get(
                "improvements",
                []
            )
        )


        better_answer = safe_text(
            item.get(
                "better_answer",
                ""
            ),
            default=""
        )


        if strengths:

            story.append(

                Paragraph(
                    "<b>Strengths</b>",
                    styles["normal"]
                )

            )


            add_bullet_list(
                story,
                strengths,
                styles,
                bullet="•"
            )


        if improvements:

            story.append(

                Paragraph(
                    "<b>Areas to Improve</b>",
                    styles["normal"]
                )

            )


            add_bullet_list(
                story,
                improvements,
                styles,
                bullet="•"
            )


        if better_answer:

            story.append(

                Paragraph(
                    "<b>Better Answer Approach</b>",
                    styles["normal"]
                )

            )


            story.append(

                Paragraph(
                    better_answer,
                    styles["normal"]
                )

            )


        story.append(

            Spacer(
                1,
                0.15 * inch
            )

        )


    # =====================================================
    # ADVANCED ANALYTICS
    # =====================================================

    if isinstance(
        interview_insights,
        dict
    ) and interview_insights:


        story.append(
            PageBreak()
        )


        add_section_title(
            story,
            "Advanced Performance Analytics",
            styles
        )


        analytics_data = [

            [
                "Technical Knowledge",
                f"{safe_text(interview_insights.get('technical_score', 0))}%"
            ],

            [
                "Communication",
                f"{safe_text(interview_insights.get('communication_score', 0))}%"
            ],

            [
                "Confidence",
                f"{safe_text(interview_insights.get('confidence_score', 0))}%"
            ],

            [
                "Problem Solving",
                f"{safe_text(interview_insights.get('problem_solving_score', 0))}%"
            ],

            [
                "Interview Readiness",
                safe_text(
                    interview_insights.get(
                        "interview_readiness",
                        "Developing"
                    )
                )
            ]

        ]


        analytics_table = Table(
            analytics_data,
            colWidths=[
                3.2 * inch,
                2.8 * inch
            ]
        )


        analytics_table.setStyle(
            TableStyle(
                [

                    (
                        "BACKGROUND",
                        (0, 0),
                        (0, -1),
                        LIGHT_BG
                    ),

                    (
                        "GRID",
                        (0, 0),
                        (-1, -1),
                        0.5,
                        BORDER
                    ),

                    (
                        "FONTNAME",
                        (0, 0),
                        (0, -1),
                        "Helvetica-Bold"
                    ),

                    (
                        "FONTSIZE",
                        (0, 0),
                        (-1, -1),
                        10
                    ),

                    (
                        "TOPPADDING",
                        (0, 0),
                        (-1, -1),
                        8
                    ),

                    (
                        "BOTTOMPADDING",
                        (0, 0),
                        (-1, -1),
                        8
                    )

                ]
            )
        )


        story.append(
            analytics_table
        )


        overall_summary = safe_text(
            interview_insights.get(
                "overall_summary",
                ""
            ),
            default=""
        )


        if overall_summary:

            story.append(

                Spacer(
                    1,
                    0.12 * inch
                )

            )


            story.append(

                Paragraph(
                    "<b>AI Performance Summary</b>",
                    styles["normal"]
                )

            )


            story.append(

                Paragraph(
                    overall_summary,
                    styles["normal"]
                )

            )


        strong_areas = safe_list(
            interview_insights.get(
                "strong_areas",
                []
            )
        )


        weak_areas = safe_list(
            interview_insights.get(
                "weak_areas",
                []
            )
        )


        story.append(

            Paragraph(
                "<b>Strong Areas</b>",
                styles["normal"]
            )

        )


        add_bullet_list(
            story,
            strong_areas,
            styles,
            bullet="•"
        )


        story.append(

            Paragraph(
                "<b>Areas to Improve</b>",
                styles["normal"]
            )

        )


        add_bullet_list(
            story,
            weak_areas,
            styles,
            bullet="•"
        )


    # =====================================================
    # SKILL GAP ANALYSIS
    # =====================================================

    if isinstance(
        skill_gap_analysis,
        dict
    ) and skill_gap_analysis:


        story.append(
            PageBreak()
        )


        add_section_title(
            story,
            "AI Skill Gap Analysis",
            styles
        )


        skill_match = safe_text(
            skill_gap_analysis.get(
                "skill_match_percentage",
                0
            )
        )


        story.append(

            Paragraph(
                (
                    f"<b>Role Skill Match:</b> "
                    f"{skill_match}%"
                ),
                styles["normal"]
            )

        )


        skill_sections = [

            (
                "Strong Skills",
                skill_gap_analysis.get(
                    "strong_skills",
                    []
                )
            ),

            (
                "Skills to Improve",
                skill_gap_analysis.get(
                    "skills_to_improve",
                    []
                )
            ),

            (
                "Missing Skills",
                skill_gap_analysis.get(
                    "missing_skills",
                    []
                )
            ),

            (
                "Recommended Next Skills",
                skill_gap_analysis.get(
                    "recommended_skills",
                    []
                )
            )

        ]


        for title, items in skill_sections:

            story.append(

                Spacer(
                    1,
                    0.10 * inch
                )

            )


            story.append(

                Paragraph(
                    f"<b>{title}</b>",
                    styles["normal"]
                )

            )


            add_bullet_list(
                story,
                items,
                styles,
                bullet="•"
            )


        career_advice = safe_text(
            skill_gap_analysis.get(
                "career_advice",
                ""
            ),
            default=""
        )


        if career_advice:

            story.append(

                Paragraph(
                    "<b>AI Career Advice</b>",
                    styles["normal"]
                )

            )


            story.append(

                Paragraph(
                    career_advice,
                    styles["normal"]
                )

            )


    # =====================================================
    # PERSONALIZED ROADMAP
    # =====================================================

    if isinstance(
        improvement_roadmap,
        dict
    ) and improvement_roadmap:


        story.append(
            PageBreak()
        )


        add_section_title(
            story,
            "Personalized 4-Week Improvement Roadmap",
            styles
        )


        roadmap_weeks = [

            (
                "week_1",
                "Week 1"
            ),

            (
                "week_2",
                "Week 2"
            ),

            (
                "week_3",
                "Week 3"
            ),

            (
                "week_4",
                "Week 4"
            )

        ]


        for week_key, week_label in roadmap_weeks:


            week_data = improvement_roadmap.get(
                week_key,
                {}
            )


            if not isinstance(
                week_data,
                dict
            ):

                continue


            title = safe_text(
                week_data.get(
                    "title",
                    week_label
                )
            )


            focus_items = safe_list(
                week_data.get(
                    "focus",
                    []
                )
            )


            story.append(

                Paragraph(
                    (
                        f"<b>{week_label}: "
                        f"{title}</b>"
                    ),
                    styles["normal"]
                )

            )


            add_bullet_list(
                story,
                focus_items,
                styles,
                bullet="•"
            )


        final_advice = safe_text(
            improvement_roadmap.get(
                "final_advice",
                ""
            ),
            default=""
        )


        if final_advice:

            story.append(

                Spacer(
                    1,
                    0.10 * inch
                )

            )


            story.append(

                Paragraph(
                    "<b>Your Next Step</b>",
                    styles["normal"]
                )

            )


            story.append(

                Paragraph(
                    final_advice,
                    styles["normal"]
                )

            )


    # =====================================================
    # FOOTER
    # =====================================================

    story.append(

        Spacer(
            1,
            0.30 * inch
        )

    )


    story.append(

        Paragraph(
            (
                "Generated by InterviewAI — "
                "Your AI-Powered Interview Coach"
            ),
            styles["subtitle"]
        )

    )


    # =====================================================
    # BUILD PDF
    # =====================================================

    document.build(
        story
    )


    buffer.seek(
        0
    )


    return buffer.getvalue()