import os
import re
import textwrap
from pathlib import Path

import streamlit as st
from dotenv import load_dotenv

import plotly.graph_objects as go

from utils.resume_parser import extract_text_from_pdf
from utils.ai_engine import (
    analyze_resume,
    generate_interview_questions,
    extract_questions,
    evaluate_answer,
    generate_interview_insights,
    generate_skill_gap_analysis,
    generate_improvement_roadmap
)
from utils.pdf_report import generate_interview_report

# =========================================================
# PAGE CONFIG
# =========================================================

st.set_page_config(
    page_title="InterviewAI",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="collapsed"
)


# =========================================================
# LOAD ENVIRONMENT VARIABLES
# =========================================================

load_dotenv()


# =========================================================
# HTML RENDER HELPER
# =========================================================

def render_html(html):

    dedented_html = textwrap.dedent(
        html
    ).strip()

    single_line_html = re.sub(
        r"\s+",
        " ",
        dedented_html
    )

    st.markdown(
        single_line_html,
        unsafe_allow_html=True
    )


# =========================================================
# LOAD CSS
# =========================================================

BASE_DIR = Path(__file__).resolve().parent

CSS_FILE = (
    BASE_DIR /
    "assets" /
    "style.css"
)


def load_css():

    if CSS_FILE.exists():

        with open(
            CSS_FILE,
            "r",
            encoding="utf-8"
        ) as file:

            css = file.read()

        st.markdown(
            f"<style>{css}</style>",
            unsafe_allow_html=True
        )

    else:

        st.warning(
            f"CSS file not found: {CSS_FILE}"
        )


load_css()


# =========================================================
# HELPER FUNCTIONS
# =========================================================

def safe_float(value, default=0.0):

    try:

        return float(value)

    except (
        TypeError,
        ValueError
    ):

        return default


def get_score_tier(score):

    score = safe_float(
        score,
        0
    )

    if score >= 8:

        return "excellent"

    elif score >= 5:

        return "average"

    else:

        return "needs-work"


def get_verdict_message(average_score):

    if average_score >= 8:

        return (
            "🌟 Outstanding performance! "
            "You're interview-ready."
        )

    elif average_score >= 6:

        return (
            "👍 Solid performance with room "
            "to sharpen a few areas."
        )

    elif average_score >= 4:

        return (
            "💪 Decent start — focus on the "
            "improvement areas below."
        )

    else:

        return (
            "📚 Keep practicing — review the "
            "feedback closely."
        )


# =========================================================
# VISUAL ANALYTICS CHART HELPERS
# =========================================================

def create_radar_chart(insights):

    categories = [
        "Technical Knowledge",
        "Communication",
        "Confidence",
        "Problem Solving"
    ]

    values = [
        safe_float(
            insights.get(
                "technical_score",
                0
            )
        ),
        safe_float(
            insights.get(
                "communication_score",
                0
            )
        ),
        safe_float(
            insights.get(
                "confidence_score",
                0
            )
        ),
        safe_float(
            insights.get(
                "problem_solving_score",
                0
            )
        )
    ]

    values.append(
        values[0]
    )

    categories.append(
        categories[0]
    )

    fig = go.Figure()

    fig.add_trace(
        go.Scatterpolar(
            r=values,
            theta=categories,
            fill="toself",
            name="Performance",
            line=dict(
                width=3
            ),
            hovertemplate=(
                "%{theta}: "
                "%{r:.0f}%"
                "<extra></extra>"
            )
        )
    )

    fig.update_layout(

        polar=dict(

            bgcolor="rgba(0,0,0,0)",

            radialaxis=dict(
                visible=True,
                range=[
                    0,
                    100
                ],
                gridcolor=(
                    "rgba(255,255,255,0.15)"
                ),
                linecolor=(
                    "rgba(255,255,255,0.15)"
                ),
                tickfont=dict(
                    color="#9CA3AF"
                )
            ),

            angularaxis=dict(
                gridcolor=(
                    "rgba(255,255,255,0.15)"
                ),
                linecolor=(
                    "rgba(255,255,255,0.15)"
                ),
                tickfont=dict(
                    color="#E5E7EB",
                    size=12
                )
            )
        ),

        paper_bgcolor=(
            "rgba(0,0,0,0)"
        ),

        font=dict(
            color="#E5E7EB",
            size=13
        ),

        margin=dict(
            l=40,
            r=40,
            t=40,
            b=40
        ),

        height=430,

        showlegend=False
    )

    return fig


def create_question_performance_chart(feedback):

    question_labels = []

    scores = []


    for index, item in enumerate(
        feedback
    ):

        if isinstance(
            item,
            dict
        ):

            score = safe_float(
                item.get(
                    "score",
                    0
                )
            )

            question_labels.append(
                f"Q{index + 1}"
            )

            scores.append(
                score
            )


    fig = go.Figure()


    fig.add_trace(

        go.Bar(

            x=question_labels,

            y=scores,

            text=[
                f"{score:.1f}/10"
                for score in scores
            ],

            textposition="outside",

            hovertemplate=(
                "<b>%{x}</b>"
                "<br>Score: "
                "%{y:.1f}/10"
                "<extra></extra>"
            )
        )
    )


    fig.update_layout(

        paper_bgcolor=(
            "rgba(0,0,0,0)"
        ),

        plot_bgcolor=(
            "rgba(0,0,0,0)"
        ),

        font=dict(
            color="#E5E7EB"
        ),

        xaxis=dict(

            title="Interview Questions",

            gridcolor=(
                "rgba(255,255,255,0.08)"
            ),

            tickfont=dict(
                color="#D1D5DB"
            )
        ),

        yaxis=dict(

            title="Score",

            range=[
                0,
                10.8
            ],

            gridcolor=(
                "rgba(255,255,255,0.12)"
            ),

            tickfont=dict(
                color="#D1D5DB"
            )
        ),

        margin=dict(
            l=40,
            r=30,
            t=40,
            b=40
        ),

        height=400,

        showlegend=False
    )


    return fig


def create_skill_gap_donut(skill_gap):

    strong_count = len(
        skill_gap.get(
            "strong_skills",
            []
        )
    )

    improve_count = len(
        skill_gap.get(
            "skills_to_improve",
            []
        )
    )

    missing_count = len(
        skill_gap.get(
            "missing_skills",
            []
        )
    )


    labels = [

        "Strong Skills",

        "Skills to Improve",

        "Missing Skills"
    ]


    values = [

        strong_count,

        improve_count,

        missing_count
    ]


    if sum(values) == 0:

        values = [

            1,

            1,

            1
        ]


    fig = go.Figure(

        data=[

            go.Pie(

                labels=labels,

                values=values,

                hole=0.62,

                textinfo=(
                    "label+percent"
                ),

                textposition=(
                    "outside"
                ),

                hovertemplate=(
                    "<b>%{label}</b>"
                    "<br>Count: "
                    "%{value}"
                    "<br>%{percent}"
                    "<extra></extra>"
                )
            )
        ]
    )


    fig.update_layout(

        paper_bgcolor=(
            "rgba(0,0,0,0)"
        ),

        font=dict(
            color="#E5E7EB",
            size=13
        ),

        margin=dict(
            l=20,
            r=20,
            t=40,
            b=20
        ),

        height=430,

        showlegend=False
    )


    return fig


def create_percentage_gauge(
    value,
    title
):

    value = max(
        0,
        min(
            100,
            safe_float(value)
        )
    )


    fig = go.Figure(

        go.Indicator(

            mode=(
                "gauge+number"
            ),

            value=value,

            number=dict(

                suffix="%",

                font=dict(
                    size=50
                )
            ),

            title=dict(
                text=title,
                font=dict(
                    size=16
                )
            ),

            gauge=dict(

                axis=dict(
                    range=[
                        0,
                        100
                    ],
                    tickwidth=1
                ),

                bar=dict(
                    thickness=0.75
                ),

                bgcolor=(
                    "rgba(255,255,255,0.05)"
                ),

                borderwidth=0,

                steps=[

                    dict(
                        range=[
                            0,
                            40
                        ],
                        color=(
                            "rgba(239,68,68,0.20)"
                        )
                    ),

                    dict(
                        range=[
                            40,
                            70
                        ],
                        color=(
                            "rgba(245,158,11,0.20)"
                        )
                    ),

                    dict(
                        range=[
                            70,
                            100
                        ],
                        color=(
                            "rgba(34,197,94,0.20)"
                        )
                    )
                ]
            )
        )
    )


    fig.update_layout(

        paper_bgcolor=(
            "rgba(0,0,0,0)"
        ),

        font=dict(
            color="#E5E7EB"
        ),

        margin=dict(
            l=20,
            r=20,
            t=50,
            b=20
        ),

        height=330
    )


    return fig


# =========================================================
# PREMIUM PERFORMANCE DASHBOARD HELPERS
# =========================================================

def get_performance_level(average_score):

    score = safe_float(average_score)

    if score >= 8:
        return "🏆", "Interview Ready", "excellent"

    if score >= 6:
        return "🚀", "Strong Candidate", "strong"

    if score >= 4:
        return "📈", "Developing", "developing"

    return "🌱", "Beginner", "beginner"


def create_score_trend_chart(scores):

    clean_scores = [
        max(0, min(10, safe_float(score)))
        for score in scores
    ]

    if not clean_scores:
        return None

    question_numbers = list(
        range(1, len(clean_scores) + 1)
    )

    fig = go.Figure()

    fig.add_trace(
        go.Scatter(
            x=question_numbers,
            y=clean_scores,
            mode="lines+markers",
            name="Score",
            hovertemplate=(
                "Question %{x}"
                "<br>Score: %{y:.1f}/10"
                "<extra></extra>"
            )
        )
    )

    fig.update_layout(
        title="Performance Trend",
        template="plotly_dark",
        height=380,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=30, r=30, t=60, b=40),
        xaxis=dict(
            title="Interview Question",
            tickmode="linear",
            dtick=1,
            gridcolor="rgba(255,255,255,0.08)"
        ),
        yaxis=dict(
            title="Score",
            range=[0, 10],
            dtick=1,
            gridcolor="rgba(255,255,255,0.08)"
        ),
        showlegend=False
    )

    return fig


def create_performance_distribution_chart(scores):

    clean_scores = [
        max(0, min(10, safe_float(score)))
        for score in scores
    ]

    if not clean_scores:
        return None

    excellent = sum(score >= 8 for score in clean_scores)
    average = sum(5 <= score < 8 for score in clean_scores)
    needs_work = sum(score < 5 for score in clean_scores)

    fig = go.Figure(
        data=[
            go.Pie(
                labels=[
                    "Excellent",
                    "Average",
                    "Needs Work"
                ],
                values=[
                    excellent,
                    average,
                    needs_work
                ],
                hole=0.62,
                textinfo="label+percent",
                hovertemplate=(
                    "%{label}"
                    "<br>%{value} Questions"
                    "<extra></extra>"
                )
            )
        ]
    )

    fig.update_layout(
        title="Performance Distribution",
        template="plotly_dark",
        height=380,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=20, r=20, t=60, b=20),
        showlegend=False
    )

    return fig


def create_best_vs_weakest_chart(scores):

    clean_scores = [
        max(0, min(10, safe_float(score)))
        for score in scores
    ]

    if not clean_scores:
        return None

    best_score = max(clean_scores)
    weakest_score = min(clean_scores)

    best_question = clean_scores.index(best_score) + 1
    weakest_question = clean_scores.index(weakest_score) + 1

    fig = go.Figure(
        data=[
            go.Bar(
                x=[
                    f"Best (Q{best_question})",
                    f"Weakest (Q{weakest_question})"
                ],
                y=[
                    best_score,
                    weakest_score
                ],
                text=[
                    f"{best_score:.1f}/10",
                    f"{weakest_score:.1f}/10"
                ],
                textposition="auto",
                hovertemplate=(
                    "%{x}"
                    "<br>Score: %{y:.1f}/10"
                    "<extra></extra>"
                )
            )
        ]
    )

    fig.update_layout(
        title="Best vs Weakest Performance",
        template="plotly_dark",
        height=350,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=30, r=30, t=60, b=40),
        yaxis=dict(
            title="Score",
            range=[0, 10],
            dtick=1,
            gridcolor="rgba(255,255,255,0.08)"
        ),
        showlegend=False
    )

    return fig


# =========================================================
# SESSION STATE
# =========================================================

if "interview_started" not in st.session_state:

    st.session_state.interview_started = False


if "questions" not in st.session_state:

    st.session_state.questions = []


if "current_question" not in st.session_state:

    st.session_state.current_question = 0


if "answers" not in st.session_state:

    st.session_state.answers = []


if "feedback" not in st.session_state:

    st.session_state.feedback = []


if "resume_text" not in st.session_state:

    st.session_state.resume_text = ""


if "resume_analysis" not in st.session_state:

    st.session_state.resume_analysis = ""


if "job_role" not in st.session_state:

    st.session_state.job_role = ""


if "interview_type" not in st.session_state:

    st.session_state.interview_type = ""


if "difficulty" not in st.session_state:

    st.session_state.difficulty = ""


if "answer_submitted" not in st.session_state:

    st.session_state.answer_submitted = False


if "celebration_shown" not in st.session_state:

    st.session_state.celebration_shown = False


# =========================================================
# ADVANCED ANALYTICS SESSION STATE
# =========================================================

if "interview_insights" not in st.session_state:

    st.session_state.interview_insights = None


if "skill_gap_analysis" not in st.session_state:

    st.session_state.skill_gap_analysis = None


if "improvement_roadmap" not in st.session_state:

    st.session_state.improvement_roadmap = None


if "analytics_generated" not in st.session_state:

    st.session_state.analytics_generated = False


# =========================================================
# SIDEBAR
# =========================================================

with st.sidebar:

    st.markdown(
        "## 🤖 InterviewAI"
    )

    st.markdown(
        "Your AI-powered interview "
        "practice platform."
    )

    st.divider()


    if st.session_state.interview_started:

        if st.button(
            "🔄 Start New Interview",
            use_container_width=True
        ):

            st.session_state.interview_started = False

            st.session_state.questions = []

            st.session_state.current_question = 0

            st.session_state.answers = []

            st.session_state.feedback = []

            st.session_state.answer_submitted = False

            st.session_state.celebration_shown = False

            st.session_state.interview_insights = None

            st.session_state.skill_gap_analysis = None

            st.session_state.improvement_roadmap = None

            st.session_state.analytics_generated = False

            st.rerun()


# =========================================================
# HOME PAGE
# =========================================================

if not st.session_state.interview_started:


    # =====================================================
    # HERO
    # =====================================================

    render_html(
        """
        <div class="bg-wordmark">
            INTERVIEWAI
        </div>
        """
    )


    render_html(
        """
        <div class="ai-badge">
            🤖 POWERED BY GENERATIVE AI
        </div>
        """
    )


    render_html(
        """
        <div class="hero-title">
            InterviewAI
        </div>
        """
    )


    render_html(
        """
        <div class="hero-subtitle">
            Your Personal AI-Powered Interview Coach.<br>
            Practice smarter, receive personalized feedback,
            and improve your interview performance.
        </div>
        """
    )


    render_html(
        """
        <div class="trust-badges">

            <div class="trust-badge">
                🧠 Gemini AI Powered
            </div>

            <div class="trust-badge">
                🎯 Role-Specific Questions
            </div>

            <div class="trust-badge">
                ⚡ Instant Feedback
            </div>

            <div class="trust-badge">
                🔒 Private Session
            </div>

        </div>
        """
    )


    st.divider()


    # =====================================================
    # METRIC CARDS
    # =====================================================

    col1, col2, col3, col4 = st.columns(
        4
    )


    with col1:

        render_html(
            """
            <div class="metric-card">

                <div class="metric-icon">
                    🤖
                </div>

                <div class="metric-value">
                    AI
                </div>

                <div class="metric-label">
                    AI Powered
                </div>

            </div>
            """
        )


    with col2:

        render_html(
            """
            <div class="metric-card">

                <div class="metric-icon">
                    🎯
                </div>

                <div class="metric-value">
                    10
                </div>

                <div class="metric-label">
                    Interview Questions
                </div>

            </div>
            """
        )


    with col3:

        render_html(
            """
            <div class="metric-card">

                <div class="metric-icon">
                    📄
                </div>

                <div class="metric-value">
                    CV
                </div>

                <div class="metric-label">
                    Resume Based
                </div>

            </div>
            """
        )


    with col4:

        render_html(
            """
            <div class="metric-card">

                <div class="metric-icon">
                    📊
                </div>

                <div class="metric-value">
                    AI
                </div>

                <div class="metric-label">
                    Smart Feedback
                </div>

            </div>
            """
        )


    render_html(
        "<br>"
    )


    # =====================================================
    # RESUME + SETTINGS
    # =====================================================

    left_col, right_col = st.columns(
        2
    )


    # =====================================================
    # RESUME SECTION
    # =====================================================

    with left_col:

        render_html(
            """
            <div class="section-heading">
                📄 Resume Intelligence
            </div>
            """
        )


        render_html(
            """
            <div class="section-description">
                Upload your resume and let our AI understand
                your skills, projects, programming experience,
                and technical background.
            </div>
            """
        )


        uploaded_resume = st.file_uploader(
            "Upload your resume in PDF format",
            type=["pdf"],
            label_visibility="visible"
        )


    # =====================================================
    # INTERVIEW CONFIGURATION
    # =====================================================

    with right_col:

        render_html(
            """
            <div class="section-heading">
                🎯 Interview Configuration
            </div>
            """
        )


        render_html(
            """
            <div class="section-description">
                Customize your interview experience according
                to your target career goals and preparation level.
            </div>
            """
        )


        job_role = st.selectbox(
            "Target Job Role",
            [
                "Python Developer",
                "AI/ML Engineer",
                "Data Scientist",
                "Data Analyst",
                "Software Developer",
                "Backend Developer"
            ]
        )


        interview_type = st.selectbox(
            "Interview Type",
            [
                "Technical Interview",
                "HR Interview",
                "Mixed Interview"
            ]
        )


        difficulty = st.selectbox(
            "Difficulty Level",
            [
                "Beginner",
                "Intermediate",
                "Advanced"
            ]
        )


    st.divider()


    # =====================================================
    # AI RESUME INTELLIGENCE
    # =====================================================

    render_html(
        """
        <div class="feature-panel">

            <div class="section-heading">
                🧠 AI Resume Intelligence
            </div>

            <div class="section-description">
                InterviewAI analyzes your technical skills,
                programming experience, projects, and technologies
                to generate personalized interview questions
                specifically tailored to your resume.
            </div>

        </div>
        """
    )


    st.divider()


    # =====================================================
    # START SECTION
    # =====================================================

    render_html(
        """
        <div class="section-heading">
            🚀 Ready to Begin?
        </div>
        """
    )


    render_html(
        """
        <div class="section-description">
            Generate a personalized AI-powered interview based
            on your resume and selected interview preferences.
        </div>
        """
    )


    # =====================================================
    # GENERATE INTERVIEW
    # =====================================================

    if st.button(
        "🚀 Generate My AI Interview",
        use_container_width=True,
        type="primary"
    ):

        if uploaded_resume is None:

            st.warning(
                "⚠️ Please upload your resume first."
            )

        else:

            status_box = st.status(
                "🧠 Reading your resume...",
                expanded=True
            )

            try:

                with status_box:

                    resume_text = (
                        extract_text_from_pdf(
                            uploaded_resume
                        )
                    )


                    if not resume_text.strip():

                        status_box.update(
                            label=(
                                "❌ Could not read resume"
                            ),
                            state="error",
                            expanded=True
                        )

                        st.error(
                            "Could not extract any text from "
                            "this PDF. Please upload a "
                            "text-based resume."
                        )

                        st.stop()


                    st.session_state.resume_text = (
                        resume_text
                    )


                    st.write(
                        "✅ Resume text extracted "
                        f"({len(resume_text.split())} words)"
                    )


                    # =====================================
                    # ANALYZE RESUME
                    # =====================================

                    status_box.update(
                        label=(
                            "🔍 Analyzing skills, projects "
                            "and experience..."
                        )
                    )


                    resume_analysis = analyze_resume(
                        resume_text=resume_text,
                        job_role=job_role
                    )


                    st.session_state.resume_analysis = (
                        resume_analysis
                    )


                    st.write(
                        "✅ Resume analysis complete"
                    )


                    # =====================================
                    # GENERATE QUESTIONS
                    # =====================================

                    status_box.update(
                        label=(
                            f"🎯 Crafting "
                            f"{difficulty.lower()} "
                            f"{interview_type.lower()} "
                            "questions for you..."
                        )
                    )


                    raw_questions_text = (
                        generate_interview_questions(
                            resume_text=resume_text,
                            resume_analysis=(
                                resume_analysis
                            ),
                            job_role=job_role,
                            interview_type=(
                                interview_type
                            ),
                            difficulty=difficulty
                        )
                    )


                    questions = extract_questions(
                        raw_questions_text
                    )


                    if not questions:

                        status_box.update(
                            label=(
                                "❌ Question generation "
                                "failed"
                            ),
                            state="error",
                            expanded=True
                        )

                        st.error(
                            "The AI did not return usable "
                            "interview questions."
                        )

                        st.stop()


                    st.write(
                        f"✅ Generated "
                        f"{len(questions)} "
                        "personalized questions"
                    )


                    # =====================================
                    # FINALIZE INTERVIEW
                    # =====================================

                    status_box.update(
                        label=(
                            "🚀 Finalizing your interview..."
                        )
                    )


                    st.session_state.questions = (
                        questions
                    )

                    st.session_state.current_question = 0

                    st.session_state.answers = []

                    st.session_state.feedback = []

                    st.session_state.job_role = (
                        job_role
                    )

                    st.session_state.interview_type = (
                        interview_type
                    )

                    st.session_state.difficulty = (
                        difficulty
                    )

                    st.session_state.answer_submitted = (
                        False
                    )

                    st.session_state.celebration_shown = (
                        False
                    )


                    # Reset analytics

                    st.session_state.interview_insights = (
                        None
                    )

                    st.session_state.skill_gap_analysis = (
                        None
                    )

                    st.session_state.improvement_roadmap = (
                        None
                    )

                    st.session_state.analytics_generated = (
                        False
                    )


                    st.session_state.interview_started = (
                        True
                    )


                    status_box.update(
                        label=(
                            "✅ Your interview is ready!"
                        ),
                        state="complete",
                        expanded=False
                    )


                    st.rerun()


            except Exception as error:

                status_box.update(
                    label=(
                        "❌ Something went wrong"
                    ),
                    state="error",
                    expanded=True
                )

                st.error(
                    f"Error generating interview: {error}"
                )


# =========================================================
# ACTIVE INTERVIEW
# =========================================================

else:

    questions = (
        st.session_state.questions
    )


    current_index = (
        st.session_state.current_question
    )


    # =====================================================
    # SAFETY CHECK
    # =====================================================

    if not questions:

        st.error(
            "No interview questions were generated."
        )


        if st.button(
            "⬅️ Go Back"
        ):

            st.session_state.interview_started = (
                False
            )

            st.rerun()


    # =====================================================
    # INTERVIEW COMPLETED
    # =====================================================

    elif current_index >= len(
        questions
    ):


        # =================================================
        # CALCULATE SCORES
        # =================================================

        scores = []


        for item in (
            st.session_state.feedback
        ):

            if isinstance(
                item,
                dict
            ):

                score = safe_float(
                    item.get(
                        "score",
                        0
                    )
                )

                scores.append(
                    score
                )


        if scores:

            average_score = (
                sum(scores) /
                len(scores)
            )

        else:

            average_score = 0


        # =================================================
        # GENERATE ADVANCED AI ANALYTICS
        # =================================================

        if not (
            st.session_state.analytics_generated
        ):

            with st.spinner(
                "🧠 AI is generating your personalized "
                "performance analytics..."
            ):

                try:

                    interview_insights = (
                        generate_interview_insights(
                            questions=questions,
                            answers=(
                                st.session_state.answers
                            ),
                            feedback=(
                                st.session_state.feedback
                            ),
                            job_role=(
                                st.session_state.job_role
                            )
                        )
                    )


                    skill_gap_analysis = (
                        generate_skill_gap_analysis(
                            resume_text=(
                                st.session_state.resume_text
                            ),
                            resume_analysis=(
                                st.session_state
                                .resume_analysis
                            ),
                            job_role=(
                                st.session_state.job_role
                            ),
                            questions=questions,
                            feedback=(
                                st.session_state.feedback
                            )
                        )
                    )


                    improvement_roadmap = (
                        generate_improvement_roadmap(
                            job_role=(
                                st.session_state.job_role
                            ),
                            interview_insights=(
                                interview_insights
                            ),
                            skill_gap=(
                                skill_gap_analysis
                            )
                        )
                    )


                    st.session_state.interview_insights = (
                        interview_insights
                    )

                    st.session_state.skill_gap_analysis = (
                        skill_gap_analysis
                    )

                    st.session_state.improvement_roadmap = (
                        improvement_roadmap
                    )

                    st.session_state.analytics_generated = (
                        True
                    )


                except Exception as error:

                    st.warning(
                        "Advanced analytics could not be "
                        f"generated: {error}"
                    )

                    st.session_state.analytics_generated = (
                        True
                    )


        # =================================================
        # CELEBRATION
        # =================================================

        if not st.session_state.get(
            "celebration_shown",
            False
        ):

            st.balloons()

            st.session_state.celebration_shown = (
                True
            )


        # =================================================
        # FINAL HEADER
        # =================================================

        render_html(
            """
            <div class="completion-badge">
                🎉 INTERVIEW COMPLETED
            </div>
            """
        )


        render_html(
            """
            <div class="final-title">
                Your Interview Performance Report
            </div>
            """
        )


        final_tier = get_score_tier(
            average_score
        )


        render_html(
            f"""
            <div class="final-score-card final-{final_tier}">

                <div class="final-score-label">
                    OVERALL PERFORMANCE
                </div>

                <div class="final-score-value">
                    {average_score:.1f}/10
                </div>

                <div class="verdict-text">
                    {get_verdict_message(average_score)}
                </div>

            </div>
            """
        )


        # =================================================
        # OVERALL PERFORMANCE GAUGE
        # =================================================

        st.markdown(
            "### 📈 Overall Performance Visualization"
        )


        overall_gauge = (
            create_percentage_gauge(
                average_score * 10,
                "Overall Interview Score"
            )
        )


        st.plotly_chart(
            overall_gauge,
            use_container_width=True,
            config={
                "displayModeBar": False
            }
        )


        # =================================================
        # BEST / WEAKEST QUESTION
        # =================================================

        indexed_feedback = []


        for i, feedback_item in enumerate(
            st.session_state.feedback
        ):

            if isinstance(
                feedback_item,
                dict
            ):

                indexed_feedback.append(
                    (
                        i,
                        feedback_item
                    )
                )


        if len(indexed_feedback) >= 2:

            best_index, best_feedback = max(

                indexed_feedback,

                key=lambda pair: safe_float(
                    pair[1].get(
                        "score",
                        0
                    )
                )
            )


            weak_index, weak_feedback = min(

                indexed_feedback,

                key=lambda pair: safe_float(
                    pair[1].get(
                        "score",
                        0
                    )
                )
            )


            callout_col1, callout_col2 = (
                st.columns(2)
            )


            with callout_col1:

                render_html(
                    f"""
                    <div class="callout-card callout-best">

                        <div class="callout-label">
                            🏆 STRONGEST ANSWER
                        </div>

                        <div class="callout-question">
                            Question {best_index + 1}
                        </div>

                        <div class="callout-score">
                            {best_feedback.get(
                                'score',
                                'N/A'
                            )}/10
                        </div>

                    </div>
                    """
                )


            with callout_col2:

                render_html(
                    f"""
                    <div class="callout-card callout-weak">

                        <div class="callout-label">
                            🎯 FOCUS AREA
                        </div>

                        <div class="callout-question">
                            Question {weak_index + 1}
                        </div>

                        <div class="callout-score">
                            {weak_feedback.get(
                                'score',
                                'N/A'
                            )}/10
                        </div>

                    </div>
                    """
                )


        render_html(
            "<br>"
        )


        # =================================================
        # QUESTION-WISE PERFORMANCE
        # =================================================

        st.subheader(
            "📊 Question-wise Performance"
        )


        for index, feedback in enumerate(
            st.session_state.feedback
        ):

            if not isinstance(
                feedback,
                dict
            ):

                continue


            score = feedback.get(
                "score",
                "N/A"
            )


            row_tier = get_score_tier(
                score
            )


            render_html(
                f"""
                <div class="performance-row row-{row_tier}">

                    <div>
                        Question {index + 1}
                    </div>

                    <div class="performance-score">
                        {score}/10
                    </div>

                </div>
                """
            )


        # =================================================
        # QUESTION PERFORMANCE BAR CHART
        # =================================================

        st.markdown(
            "### 📊 Performance Visualization"
        )


        question_chart = (
            create_question_performance_chart(
                st.session_state.feedback
            )
        )


        st.plotly_chart(
            question_chart,
            use_container_width=True,
            config={
                "displayModeBar": False
            }
        )


        # =================================================
        # PREMIUM VISUAL PERFORMANCE DASHBOARD
        # =================================================

        st.divider()


        render_html(
            """
            <div class="analytics-main-heading">
                📈 Premium Performance Dashboard
            </div>
            """
        )


        render_html(
            """
            <div class="analytics-subtitle">
                A visual breakdown of your interview performance,
                strengths, consistency and improvement areas.
            </div>
            """
        )


        dashboard_scores = []


        for feedback_item in st.session_state.feedback:

            if isinstance(
                feedback_item,
                dict
            ):

                dashboard_scores.append(
                    max(
                        0,
                        min(
                            10,
                            safe_float(
                                feedback_item.get(
                                    "score",
                                    0
                                )
                            )
                        )
                    )
                )


        level_icon, level_name, level_class = (
            get_performance_level(
                average_score
            )
        )


        render_html(
            f"""
            <div class="performance-level-card level-{level_class}">

                <div class="performance-level-icon">
                    {level_icon}
                </div>

                <div>

                    <div class="performance-level-label">
                        PERFORMANCE LEVEL
                    </div>

                    <div class="performance-level-name">
                        {level_name}
                    </div>

                    <div class="performance-level-score">
                        Overall Score: {average_score:.1f}/10
                    </div>

                </div>

            </div>
            """
        )


        if dashboard_scores:

            dashboard_col1, dashboard_col2 = (
                st.columns(2)
            )


            with dashboard_col1:

                trend_chart = (
                    create_score_trend_chart(
                        dashboard_scores
                    )
                )


                if trend_chart is not None:

                    st.plotly_chart(
                        trend_chart,
                        use_container_width=True,
                        config={
                            "displayModeBar": False
                        },
                        key="premium_score_trend_chart"
                    )


            with dashboard_col2:

                distribution_chart = (
                    create_performance_distribution_chart(
                        dashboard_scores
                    )
                )


                if distribution_chart is not None:

                    st.plotly_chart(
                        distribution_chart,
                        use_container_width=True,
                        config={
                            "displayModeBar": False
                        },
                        key="premium_performance_distribution_chart"
                    )


            comparison_chart = (
                create_best_vs_weakest_chart(
                    dashboard_scores
                )
            )


            if comparison_chart is not None:

                st.plotly_chart(
                    comparison_chart,
                    use_container_width=True,
                    config={
                        "displayModeBar": False
                    },
                    key="premium_best_vs_weakest_chart"
                )


        # =================================================
        # ADVANCED ANALYTICS
        # =================================================

        insights = (
            st.session_state
            .interview_insights
        )


        if insights:

            st.divider()


            render_html(
                """
                <div class="analytics-main-heading">
                    📊 Advanced Performance Analytics
                </div>
                """
            )


            render_html(
                """
                <div class="analytics-subtitle">
                    AI-powered analysis of your technical
                    performance, communication, confidence,
                    and problem-solving ability.
                </div>
                """
            )


            # =============================================
            # PERFORMANCE RADAR CHART
            # =============================================

            st.markdown(
                "### 🕸️ Performance Radar"
            )


            radar_chart = (
                create_radar_chart(
                    insights
                )
            )


            st.plotly_chart(
                radar_chart,
                use_container_width=True,
                config={
                    "displayModeBar": False
                }
            )


            technical_score = safe_float(
                insights.get(
                    "technical_score",
                    0
                )
            )


            communication_score = safe_float(
                insights.get(
                    "communication_score",
                    0
                )
            )


            confidence_score = safe_float(
                insights.get(
                    "confidence_score",
                    0
                )
            )


            problem_solving_score = safe_float(
                insights.get(
                    "problem_solving_score",
                    0
                )
            )


            col1, col2 = st.columns(
                2
            )


            with col1:

                render_html(
                    f"""
                    <div class="analytics-card">

                        <div class="analytics-icon">
                            🧠
                        </div>

                        <div class="analytics-content">

                            <div class="analytics-label">
                                TECHNICAL KNOWLEDGE
                            </div>

                            <div class="analytics-value">
                                {technical_score:.0f}%
                            </div>

                        </div>

                    </div>
                    """
                )


            with col2:

                render_html(
                    f"""
                    <div class="analytics-card">

                        <div class="analytics-icon">
                            💬
                        </div>

                        <div class="analytics-content">

                            <div class="analytics-label">
                                COMMUNICATION
                            </div>

                            <div class="analytics-value">
                                {communication_score:.0f}%
                            </div>

                        </div>

                    </div>
                    """
                )


            col3, col4 = st.columns(
                2
            )


            with col3:

                render_html(
                    f"""
                    <div class="analytics-card">

                        <div class="analytics-icon">
                            🔥
                        </div>

                        <div class="analytics-content">

                            <div class="analytics-label">
                                CONFIDENCE
                            </div>

                            <div class="analytics-value">
                                {confidence_score:.0f}%
                            </div>

                        </div>

                    </div>
                    """
                )


            with col4:

                render_html(
                    f"""
                    <div class="analytics-card">

                        <div class="analytics-icon">
                            🧩
                        </div>

                        <div class="analytics-content">

                            <div class="analytics-label">
                                PROBLEM SOLVING
                            </div>

                            <div class="analytics-value">
                                {problem_solving_score:.0f}%
                            </div>

                        </div>

                    </div>
                    """
                )


            readiness = insights.get(
                "interview_readiness",
                "Developing"
            )


            summary = insights.get(
                "overall_summary",
                ""
            )


            render_html(
                f"""
                <div class="readiness-card">

                    <div class="readiness-label">
                        🎯 INTERVIEW READINESS
                    </div>

                    <div class="readiness-value">
                        {readiness}
                    </div>

                    <div class="readiness-summary">
                        {summary}
                    </div>

                </div>
                """
            )


            strong_col, weak_col = (
                st.columns(2)
            )


            with strong_col:

                strong_html = """
                <div class="insight-panel insight-strong">

                    <div class="insight-panel-title">
                        💪 Your Strong Areas
                    </div>
                """


                for item in insights.get(
                    "strong_areas",
                    []
                ):

                    strong_html += f"""
                    <div class="insight-item strong">
                        ✓ {item}
                    </div>
                    """


                strong_html += (
                    "</div>"
                )


                render_html(
                    strong_html
                )


            with weak_col:

                weak_html = """
                <div class="insight-panel insight-weak">

                    <div class="insight-panel-title">
                        🎯 Areas to Improve
                    </div>
                """


                for item in insights.get(
                    "weak_areas",
                    []
                ):

                    weak_html += f"""
                    <div class="insight-item weak">
                        ⚠ {item}
                    </div>
                    """


                weak_html += (
                    "</div>"
                )


                render_html(
                    weak_html
                )


        # =================================================
        # SKILL GAP ANALYSIS
        # =================================================

        skill_gap = (
            st.session_state
            .skill_gap_analysis
        )


        if skill_gap:

            st.divider()


            render_html(
                """
                <div class="analytics-main-heading">
                    🎯 AI Skill Gap Analysis
                </div>
                """
            )


            render_html(
                """
                <div class="analytics-subtitle">
                    Your resume and interview performance
                    compared with the requirements of your
                    selected career path.
                </div>
                """
            )


            skill_match = safe_float(
                skill_gap.get(
                    "skill_match_percentage",
                    0
                )
            )


            # =============================================
            # SKILL GAP VISUAL CHARTS
            # =============================================

            chart_col1, chart_col2 = (
                st.columns(2)
            )


            with chart_col1:

                st.markdown(
                    "### 🎯 Skill Distribution"
                )


                skill_gap_chart = (
                    create_skill_gap_donut(
                        skill_gap
                    )
                )


                st.plotly_chart(
                    skill_gap_chart,
                    use_container_width=True,
                    config={
                        "displayModeBar": False
                    }
                )


            with chart_col2:

                st.markdown(
                    "### 📈 Role Compatibility"
                )


                skill_match_chart = (
                    create_percentage_gauge(
                        skill_match,
                        "Role Skill Match"
                    )
                )


                st.plotly_chart(
                    skill_match_chart,
                    use_container_width=True,
                    config={
                        "displayModeBar": False
                    }
                )


            # =============================================
            # EXISTING SKILL MATCH CARD
            # =============================================

            render_html(
                f"""
                <div class="skill-match-card">

                    <div class="skill-match-label">
                        ROLE SKILL MATCH
                    </div>

                    <div class="skill-match-value">
                        {skill_match:.0f}%
                    </div>

                    <div class="skill-progress-track">

                        <div
                            class="skill-progress-fill"
                            style="
                                width:{skill_match}%;
                            ">
                        </div>

                    </div>

                </div>
                """
            )


            skill_col1, skill_col2 = (
                st.columns(2)
            )


            with skill_col1:

                strong_skills_html = """
                <div class="skill-category-card">

                    <div class="skill-category-title">
                        💪 Strong Skills
                    </div>
                """


                for skill in skill_gap.get(
                    "strong_skills",
                    []
                ):

                    strong_skills_html += f"""
                    <div class="skill-tag skill-strong">
                        ✓ {skill}
                    </div>
                    """


                strong_skills_html += (
                    "</div>"
                )


                render_html(
                    strong_skills_html
                )


            with skill_col2:

                improve_skills_html = """
                <div class="skill-category-card">

                    <div class="skill-category-title">
                        🚀 Skills to Improve
                    </div>
                """


                for skill in skill_gap.get(
                    "skills_to_improve",
                    []
                ):

                    improve_skills_html += f"""
                    <div class="skill-tag skill-improve">
                        ⚡ {skill}
                    </div>
                    """


                improve_skills_html += (
                    "</div>"
                )


                render_html(
                    improve_skills_html
                )


            missing_col, recommended_col = (
                st.columns(2)
            )


            with missing_col:

                missing_html = """
                <div class="skill-category-card">

                    <div class="skill-category-title">
                        ⚠ Missing Skills
                    </div>
                """


                for skill in skill_gap.get(
                    "missing_skills",
                    []
                ):

                    missing_html += f"""
                    <div class="skill-tag skill-missing">
                        + {skill}
                    </div>
                    """


                missing_html += (
                    "</div>"
                )


                render_html(
                    missing_html
                )


            with recommended_col:

                recommended_html = """
                <div class="skill-category-card">

                    <div class="skill-category-title">
                        🌟 Recommended Next Skills
                    </div>
                """


                for skill in skill_gap.get(
                    "recommended_skills",
                    []
                ):

                    recommended_html += f"""
                    <div class="skill-tag skill-recommended">
                        ✦ {skill}
                    </div>
                    """


                recommended_html += (
                    "</div>"
                )


                render_html(
                    recommended_html
                )


            career_advice = skill_gap.get(
                "career_advice",
                ""
            )


            if career_advice:

                render_html(
                    f"""
                    <div class="career-advice-card">

                        <div class="career-advice-title">
                            💡 AI Career Advice
                        </div>

                        <div class="career-advice-text">
                            {career_advice}
                        </div>

                    </div>
                    """
                )


        # =================================================
        # PERSONALIZED ROADMAP
        # =================================================

        roadmap = (
            st.session_state
            .improvement_roadmap
        )


        if roadmap:

            st.divider()


            render_html(
                """
                <div class="analytics-main-heading">
                    🧠 Your Personalized 4-Week Roadmap
                </div>
                """
            )


            render_html(
                """
                <div class="analytics-subtitle">
                    A practical AI-generated improvement plan
                    based on your interview performance and
                    career skill gaps.
                </div>
                """
            )


            roadmap_weeks = [

                (
                    "week_1",
                    "01",
                    "Foundation"
                ),

                (
                    "week_2",
                    "02",
                    "Core Skills"
                ),

                (
                    "week_3",
                    "03",
                    "Practical Growth"
                ),

                (
                    "week_4",
                    "04",
                    "Interview Ready"
                )
            ]


            for (
                week_key,
                week_number,
                default_title
            ) in roadmap_weeks:


                week_data = roadmap.get(
                    week_key,
                    {}
                )


                title = week_data.get(
                    "title",
                    default_title
                )


                focus_items = week_data.get(
                    "focus",
                    []
                )


                roadmap_html = f"""
                <div class="roadmap-card">

                    <div class="roadmap-week">
                        WEEK {week_number}
                    </div>

                    <div class="roadmap-title">
                        {title}
                    </div>
                """


                for item in focus_items:

                    roadmap_html += f"""
                    <div class="roadmap-task">

                        <span>
                            ✓
                        </span>

                        {item}

                    </div>
                    """


                roadmap_html += (
                    "</div>"
                )


                render_html(
                    roadmap_html
                )


            final_advice = roadmap.get(
                "final_advice",
                ""
            )


            if final_advice:

                render_html(
                    f"""
                    <div class="roadmap-final-advice">

                        <div class="roadmap-final-title">
                            🚀 Your Next Step
                        </div>

                        <div class="roadmap-final-text">
                            {final_advice}
                        </div>

                    </div>
                    """
                )
                        # =================================================
        # DOWNLOAD PDF INTERVIEW REPORT
        # =================================================

        st.divider()

        render_html(
            """
            <div class="analytics-main-heading">
                📄 Download Your Interview Report
            </div>
            """
        )

        render_html(
            """
            <div class="analytics-subtitle">
                Download a complete professional report containing
                your interview performance, AI analytics, skill gap
                analysis, and personalized improvement roadmap.
            </div>
            """
        )


        try:

            # Generate PDF report
            pdf_report = generate_interview_report(
                average_score=average_score,
                job_role=st.session_state.job_role,
                interview_type=st.session_state.interview_type,
                difficulty=st.session_state.difficulty,
                questions=st.session_state.questions,
                answers=st.session_state.answers,
                feedback=st.session_state.feedback,
                interview_insights=(
                    st.session_state.interview_insights
                ),
                skill_gap_analysis=(
                    st.session_state.skill_gap_analysis
                ),
                improvement_roadmap=(
                    st.session_state.improvement_roadmap
                )
            )


            # Download button
            st.download_button(
                label="📄 Download Full Interview Report",
                data=pdf_report,
                file_name="InterviewAI_Interview_Report.pdf",
                mime="application/pdf",
                use_container_width=True,
                type="primary"
            )


        except Exception as error:

            st.error(
                f"Unable to generate PDF report: {error}"
            )


        # =================================================
        # START NEW INTERVIEW
        # =================================================

        st.divider()


        if st.button(
            "🔄 Start New Interview",
            use_container_width=True,
            type="primary"
        ):

            st.session_state.interview_started = (
                False
            )

            st.session_state.questions = []

            st.session_state.current_question = 0

            st.session_state.answers = []

            st.session_state.feedback = []

            st.session_state.answer_submitted = False

            st.session_state.celebration_shown = False

            st.session_state.interview_insights = None

            st.session_state.skill_gap_analysis = None

            st.session_state.improvement_roadmap = None

            st.session_state.analytics_generated = False

            st.rerun()


    # =====================================================
    # ACTIVE QUESTION
    # =====================================================

    else:


        current_question = questions[
            current_index
        ]


        # =================================================
        # PROGRESS
        # =================================================

        progress_percentage = int(
            (
                current_index /
                len(questions)
            ) * 100
        )


        render_html(
            f"""
            <div class="progress-wrapper">

                <div class="live-label">
                    🎯 LIVE AI MOCK INTERVIEW
                </div>

                <div class="question-number">
                    Question {current_index + 1}
                    of {len(questions)}
                </div>

                <div class="progress-text">
                    {progress_percentage}% Completed
                </div>

            </div>
            """
        )


        st.progress(
            progress_percentage / 100
        )


        # =================================================
        # QUESTION DOTS
        # =================================================

        dots_html = (
            '<div class="question-dots">'
        )


        for i in range(
            len(questions)
        ):

            if i < len(
                st.session_state.feedback
            ):

                dot_class = (
                    "dot-answered"
                )

            elif i == current_index:

                dot_class = (
                    "dot-current"
                )

            else:

                dot_class = (
                    "dot-upcoming"
                )


            dots_html += (
                f'<div class="question-dot '
                f'{dot_class}" '
                f'title="Question '
                f'{i + 1}"></div>'
            )


        dots_html += (
            "</div>"
        )


        render_html(
            dots_html
        )


        render_html(
            "<br>"
        )


        # =================================================
        # QUESTION
        # =================================================

        render_html(
            f"""
            <div class="question-card">

                <div class="question-label">
                    AI INTERVIEW QUESTION
                </div>

                <div class="question-text">
                    {current_question}
                </div>

            </div>
            """
        )


        # =================================================
        # ANSWER SECTION
        # =================================================

        render_html(
            """
            <div class="answer-section">

                <div class="answer-title">
                    🗣️ Your Answer
                </div>

                <div class="answer-subtitle">
                    Explain your answer clearly and use examples
                    from your projects whenever possible.
                </div>

            </div>
            """
        )


        answer = st.text_area(
            "Type your answer here",
            height=220,
            placeholder=(
                "Start typing your answer..."
            ),
            label_visibility="collapsed",
            key=(
                f"answer_input_"
                f"{current_index}"
            )
        )


        # =================================================
        # SUBMIT ANSWER
        # =================================================

        if not (
            st.session_state.answer_submitted
        ):

            if st.button(
                "✨ Submit Answer & Get AI Feedback",
                use_container_width=True,
                type="primary"
            ):

                if not answer.strip():

                    st.warning(
                        "Please write an answer first."
                    )

                else:

                    with st.spinner(
                        "🤖 AI is evaluating your answer..."
                    ):

                        try:

                            feedback = (
                                evaluate_answer(
                                    question=(
                                        current_question
                                    ),
                                    answer=answer,
                                    resume_text=(
                                        st.session_state
                                        .resume_text
                                    ),
                                    job_role=(
                                        st.session_state
                                        .job_role
                                    ),
                                    difficulty=(
                                        st.session_state
                                        .difficulty
                                    )
                                )
                            )


                            st.session_state.answers.append(
                                answer
                            )


                            st.session_state.feedback.append(
                                feedback
                            )


                            st.session_state.answer_submitted = (
                                True
                            )


                            st.rerun()


                        except Exception as error:

                            st.error(
                                "Error evaluating answer: "
                                f"{error}"
                            )


        # =================================================
        # FEEDBACK
        # =================================================

        if (

            st.session_state.answer_submitted

            and st.session_state.feedback

            and len(
                st.session_state.feedback
            ) > current_index
        ):


            feedback = (
                st.session_state.feedback[
                    current_index
                ]
            )


            render_html(
                "<br>"
            )


            render_html(
                """
                <div class="feedback-heading">
                    🤖 AI Feedback
                </div>
                """
            )


            score = feedback.get(
                "score",
                "N/A"
            )


            score_tier = get_score_tier(
                score
            )


            score_percent = max(
                0,
                min(
                    100,
                    safe_float(score) * 10
                )
            )


            render_html(
                f"""
                <div class="score-card score-{score_tier}">

                    <div class="score-label">
                        ANSWER SCORE
                    </div>

                    <div class="score-value">
                        {score}/10
                    </div>

                    <div class="score-gauge">

                        <div
                            class="
                                score-gauge-fill
                                score-{score_tier}
                            "
                            style="
                                width:{score_percent}%;
                            ">
                        </div>

                    </div>

                </div>
                """
            )


            strengths = feedback.get(
                "strengths",
                []
            )


            improvements = feedback.get(
                "improvements",
                []
            )


            better_answer = feedback.get(
                "better_answer",
                ""
            )


            col1, col2 = st.columns(
                2
            )


            with col1:

                st.markdown(
                    "### 💪 Strengths"
                )


                for item in strengths:

                    render_html(
                        f"""
                        <div class="strength-item">
                            ✓ {item}
                        </div>
                        """
                    )


            with col2:

                st.markdown(
                    "### 🚀 Improvements"
                )


                for item in improvements:

                    render_html(
                        f"""
                        <div class="improvement-item">
                            ⚠ {item}
                        </div>
                        """
                    )


            st.markdown(
                "### ✨ Better Answer Approach"
            )


            render_html(
                f"""
                <div class="better-answer">
                    {better_answer}
                </div>
                """
            )


            render_html(
                "<br>"
            )


            if st.button(
                "➡️ Next Question",
                use_container_width=True,
                type="primary"
            ):

                st.session_state.current_question += 1

                st.session_state.answer_submitted = (
                    False
                )

                st.rerun()