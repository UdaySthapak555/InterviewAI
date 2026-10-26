import os
import re
import textwrap
from io import BytesIO
from pathlib import Path

import streamlit as st

# Optional dependencies -------------------------------------------------
try:
    import speech_recognition as sr
    SPEECH_AVAILABLE = True
except Exception:
    SPEECH_AVAILABLE = False

try:
    import plotly.graph_objects as go
    PLOTLY_AVAILABLE = True
except Exception:
    PLOTLY_AVAILABLE = False

try:
    from dotenv import load_dotenv
    load_dotenv()
except Exception:
    pass

# Project utilities -----------------------------------------------------
try:
    from utils.resume_parser import extract_text_from_pdf
except Exception:
    extract_text_from_pdf = None

try:
    from utils.ai_engine import (
        analyze_resume,
        generate_interview_questions,
        extract_questions,
        evaluate_answer,
        generate_interview_insights,
        generate_skill_gap_analysis,
        generate_improvement_roadmap,
    )
    AI_ENGINE_AVAILABLE = True
except Exception:
    AI_ENGINE_AVAILABLE = False

try:
    from utils.pdf_report import generate_interview_report
except Exception:
    generate_interview_report = None


# ======================================================================
# PAGE CONFIG
# ======================================================================

st.set_page_config(
    page_title="InterviewAI | AI Interview Intelligence",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded",
)

# =========================================================
# HTML RENDER HELPER
# =========================================================

def render_html(html_content):
    st.html(
        textwrap.dedent(html_content)
    )
    
# ======================================================================
# PATHS + CSS
# ======================================================================

BASE_DIR = Path(__file__).resolve().parent
CSS_FILE = BASE_DIR / "assets" / "style.css"


def load_css():

    if CSS_FILE.exists():

        try:

            css = CSS_FILE.read_text(
                encoding="utf-8"
            )

            st.markdown(
                f"<style>{css}</style>",
                unsafe_allow_html=True
            )

        except Exception as error:

            st.error(
                f"Could not load CSS: {error}"
            )

    else:

        st.error(
            f"""
            ❌ CSS file not found.

            Expected location:

            {CSS_FILE}
            """
        )
load_css()

# ======================================================================
# DASHBOARD COMPONENT FALLBACK STYLES
# These styles only target the new premium dashboard components. The hero
# remains fully controlled by the existing style.css as requested.
# ======================================================================

def load_dashboard_component_styles():
    st.markdown(
        """
        <style>
        .premium-section-header{display:flex;align-items:center;justify-content:space-between;gap:1rem;margin:1.4rem 0 1rem}.premium-section-kicker{font-size:.68rem;letter-spacing:.14em;font-weight:800;color:#a78bfa;text-transform:uppercase;margin-bottom:.45rem}.premium-section-title{font-size:1.45rem;font-weight:800;color:#f8fafc;letter-spacing:-.03em}.premium-section-status{display:flex;align-items:center;gap:.45rem;font-size:.7rem;letter-spacing:.08em;color:#a5b4fc;font-weight:800}.status-pulse{width:8px;height:8px;border-radius:50%;background:#22c55e;box-shadow:0 0 0 5px rgba(34,197,94,.08)}
        .premium-metric-card{position:relative;min-height:205px;padding:1.2rem;border-radius:20px;background:linear-gradient(145deg,rgba(24,29,43,.98),rgba(13,17,27,.98));border:1px solid rgba(99,102,241,.24);box-shadow:inset 0 1px 0 rgba(255,255,255,.03),0 16px 45px rgba(0,0,0,.16);overflow:hidden;transition:transform .22s ease,border-color .22s ease,box-shadow .22s ease}.premium-metric-card:hover{transform:translateY(-5px);border-color:rgba(139,92,246,.58);box-shadow:0 22px 60px rgba(76,29,149,.22)}.premium-metric-card:after{content:"";position:absolute;width:120px;height:120px;right:-55px;top:-55px;border-radius:50%;background:radial-gradient(circle,rgba(99,102,241,.2),transparent 68%);pointer-events:none}.metric-card-top{display:flex;justify-content:space-between;align-items:center;margin-bottom:1rem}.metric-icon-premium{width:42px;height:42px;border-radius:14px;display:grid;place-items:center;background:linear-gradient(135deg,rgba(124,58,237,.22),rgba(59,130,246,.18));border:1px solid rgba(139,92,246,.28);font-size:1.05rem}.metric-live-dot{width:7px;height:7px;border-radius:50%;background:#22c55e;box-shadow:0 0 16px rgba(34,197,94,.7)}.metric-value-premium{font-size:2rem;font-weight:850;color:#f8fafc;letter-spacing:-.04em;line-height:1.05}.metric-label-premium{margin-top:.55rem;font-size:.88rem;font-weight:750;color:#e5e7eb}.metric-description-premium{margin-top:.35rem;font-size:.73rem;line-height:1.5;color:#94a3b8}.metric-progress-track{height:5px;margin-top:1rem;border-radius:99px;background:rgba(148,163,184,.12);overflow:hidden}.metric-progress-fill{height:100%;border-radius:inherit;background:linear-gradient(90deg,#8b5cf6,#3b82f6)}
        .premium-intelligence-card{height:100%;padding:1.45rem;border-radius:22px;background:linear-gradient(145deg,rgba(22,27,40,.98),rgba(12,16,25,.98));border:1px solid rgba(100,116,139,.24);box-shadow:0 18px 55px rgba(0,0,0,.14)}.intelligence-card-header{display:flex;justify-content:space-between;gap:1rem;align-items:flex-start;margin-bottom:1.25rem}.intelligence-card-title{font-size:1.25rem;font-weight:800;color:#f8fafc;letter-spacing:-.025em}.intelligence-badge{padding:.45rem .65rem;border-radius:99px;background:rgba(124,58,237,.12);border:1px solid rgba(139,92,246,.25);color:#c4b5fd;font-size:.65rem;font-weight:800;letter-spacing:.06em;white-space:nowrap}.resume-intelligence-status{display:flex;align-items:center;gap:.85rem;padding:1rem;border-radius:16px;background:rgba(255,255,255,.025);border:1px solid rgba(148,163,184,.12)}.resume-status-icon{width:42px;height:42px;border-radius:13px;display:grid;place-items:center;background:linear-gradient(135deg,rgba(34,197,94,.16),rgba(59,130,246,.16));color:#bbf7d0;font-weight:900}.resume-status-title{font-weight:800;color:#f1f5f9;font-size:.9rem}.resume-status-description{margin-top:.22rem;color:#94a3b8;font-size:.74rem;line-height:1.45}.premium-stat-grid{display:grid;grid-template-columns:repeat(3,1fr);gap:.7rem;margin-top:1rem}.premium-mini-stat{padding:.9rem;border-radius:14px;background:rgba(255,255,255,.025);border:1px solid rgba(148,163,184,.1)}.mini-stat-value{font-size:1.05rem;font-weight:850;color:#e9e7ff}.mini-stat-label{margin-top:.28rem;font-size:.67rem;color:#94a3b8;line-height:1.35}.coach-avatar{width:42px;height:42px;border-radius:14px;display:grid;place-items:center;background:linear-gradient(135deg,rgba(236,72,153,.16),rgba(139,92,246,.18));border:1px solid rgba(192,132,252,.22)}.premium-insight-row{display:flex;gap:.85rem;padding:.82rem 0;border-top:1px solid rgba(148,163,184,.1)}.premium-insight-row:first-of-type{border-top:0}.insight-icon{width:36px;height:36px;flex:0 0 36px;border-radius:12px;display:grid;place-items:center;background:rgba(255,255,255,.035)}.insight-title{font-size:.67rem;font-weight:850;letter-spacing:.08em;color:#a5b4fc}.insight-description{margin-top:.28rem;font-size:.78rem;line-height:1.5;color:#cbd5e1}
        .premium-workspace-card{position:relative;padding:1.5rem;border-radius:24px;background:linear-gradient(135deg,rgba(20,25,42,.98),rgba(15,18,30,.98));border:1px solid rgba(99,102,241,.3);overflow:hidden;box-shadow:0 22px 70px rgba(0,0,0,.2)}.workspace-glow{position:absolute;width:300px;height:300px;right:-110px;bottom:-180px;border-radius:50%;background:radial-gradient(circle,rgba(124,58,237,.25),transparent 68%)}.workspace-content{position:relative;display:flex;justify-content:space-between;align-items:center;gap:1.5rem}.workspace-left-premium{display:flex;align-items:center;gap:1rem}.workspace-icon{width:56px;height:56px;border-radius:18px;display:grid;place-items:center;font-size:1.45rem;background:linear-gradient(135deg,#7c3aed,#2563eb);box-shadow:0 10px 30px rgba(76,29,149,.28)}.workspace-kicker{font-size:.67rem;letter-spacing:.12em;font-weight:850;color:#a5b4fc}.workspace-title{margin-top:.3rem;font-size:1.35rem;font-weight:850;color:#f8fafc}.workspace-description{margin-top:.4rem;max-width:620px;font-size:.8rem;line-height:1.55;color:#94a3b8}.workspace-right-premium{display:flex;flex-wrap:wrap;justify-content:flex-end;gap:.5rem}.workspace-meta-pill{padding:.55rem .7rem;border-radius:99px;background:rgba(255,255,255,.045);border:1px solid rgba(148,163,184,.16);color:#cbd5e1;font-size:.7rem;white-space:nowrap}.premium-history-card{display:flex;justify-content:space-between;align-items:center;gap:1rem;padding:1.25rem 1.35rem;margin:.8rem 0;border-radius:18px;background:linear-gradient(145deg,rgba(23,28,42,.96),rgba(14,18,28,.96));border:1px solid rgba(100,116,139,.22)}.history-title{font-size:1.1rem;font-weight:800;color:#f8fafc}.history-meta{margin-top:.35rem;font-size:.76rem;color:#94a3b8}.history-score{padding:.75rem 1rem;border-radius:14px;background:rgba(124,58,237,.12);border:1px solid rgba(139,92,246,.25);font-weight:850;color:#ddd6fe;white-space:nowrap}
        @media(max-width:900px){.premium-stat-grid{grid-template-columns:1fr}.workspace-content{align-items:flex-start;flex-direction:column}.workspace-right-premium{justify-content:flex-start}.premium-section-header{align-items:flex-start;flex-direction:column}}
        </style>
        """,
        unsafe_allow_html=True,
    )


load_dashboard_component_styles()

# ======================================================================
# SESSION STATE
# ======================================================================

DEFAULTS = {
    "current_page": "Dashboard",
    "interview_started": False,
    "questions": [],
    "current_question": 0,
    "answers": [],
    "feedback": [],
    "answer_submitted": False,
    "resume_text": "",
    "resume_analysis": "",
    "job_role": "Python Developer",
    "interview_type": "Technical Interview",
    "difficulty": "Beginner",
    "question_count": 5,
    "interview_complete": False,
    "webcam_images": [],
    "interview_insights": None,
    "skill_gap_analysis": None,
    "improvement_roadmap": None,
    "interview_history": [],
    "history_saved": False,
    "captured_photo_questions": [],
}

for key, value in DEFAULTS.items():
    if key not in st.session_state:
        st.session_state[key] = value


# ======================================================================
# HELPERS
# ======================================================================

def reset_interview():
    st.session_state.interview_started = False
    st.session_state.questions = []
    st.session_state.current_question = 0
    st.session_state.answers = []
    st.session_state.feedback = []
    st.session_state.answer_submitted = False
    st.session_state.interview_complete = False
    st.session_state.webcam_images = []
    st.session_state.interview_insights = None
    st.session_state.skill_gap_analysis = None
    st.session_state.improvement_roadmap = None
    st.session_state.history_saved = False
    st.session_state.captured_photo_questions = []


def safe_text(value):
    if value is None:
        return ""
    if isinstance(value, str):
        return value
    return str(value)


def transcribe_audio(audio_file):
    if audio_file is None:
        return "", None

    if not SPEECH_AVAILABLE:
        return "", "SpeechRecognition is not installed."

    try:
        recognizer = sr.Recognizer()
        audio_bytes = BytesIO(audio_file.getvalue())

        with sr.AudioFile(audio_bytes) as source:
            audio_data = recognizer.record(source)

        transcript = recognizer.recognize_google(
            audio_data,
            language="en-IN",
        )
        return transcript, None

    except sr.UnknownValueError:
        return "", "The voice could not be understood. Please speak clearly."

    except sr.RequestError as error:
        return "", f"Speech recognition service error: {error}"

    except Exception as error:
        return "", f"Unable to process audio: {error}"


def fallback_questions(role, interview_type, difficulty, count, resume_text):
    skills_hint = "your projects and technical experience"
    if resume_text:
        skills_hint = "the skills and projects mentioned in your resume"

    bank = [
        f"Tell me about yourself and explain why you are interested in the {role} role.",
        f"Walk me through one important project from {skills_hint}. What problem did you solve?",
        f"What are the most important technical skills required for a {role}, and how have you used them?",
        "Describe a difficult technical problem you faced and explain your step-by-step approach.",
        "How do you debug an application when the expected output is not produced?",
        "How do you write clean, maintainable, and scalable code?",
        "Explain a concept from your technical background using a simple real-world example.",
        "Describe a time when you had to learn a new technology quickly.",
        "What would you improve in one of your existing projects if you had more time?",
        "Why should we hire you for this role?",
        "How do you handle feedback when someone points out a weakness in your work?",
        "Where do you see yourself developing professionally over the next few years?",
    ]

    prefix = {
        "Technical Interview": "Technical focus: ",
        "HR Interview": "Professional focus: ",
        "Mixed Interview": "",
    }.get(interview_type, "")

    return [prefix + bank[i % len(bank)] for i in range(count)]


def generate_questions_safely():
    role = st.session_state.job_role
    interview_type = st.session_state.interview_type
    difficulty = st.session_state.difficulty
    count = int(st.session_state.question_count)
    resume_text = st.session_state.resume_text
    analysis = st.session_state.resume_analysis

    if not AI_ENGINE_AVAILABLE:
        return fallback_questions(role, interview_type, difficulty, count, resume_text)

    generated = None

    attempts = [
        lambda: generate_interview_questions(
            resume_text,
            analysis,
            role,
            interview_type,
            difficulty,
            count,
        ),
        lambda: generate_interview_questions(
            resume_text=resume_text,
            resume_analysis=analysis,
            job_role=role,
            interview_type=interview_type,
            difficulty=difficulty,
            question_count=count,
        ),
        lambda: generate_interview_questions(
            resume_text,
            role,
            interview_type,
            difficulty,
            count,
        ),
    ]

    for attempt in attempts:
        try:
            generated = attempt()
            if generated:
                break
        except TypeError:
            continue
        except Exception:
            break

    if generated and "extract_questions" in globals() and callable(extract_questions):
        try:
            questions = extract_questions(generated)
            if isinstance(questions, list) and questions:
                return [safe_text(q) for q in questions[:count]]
        except Exception:
            pass

    if isinstance(generated, list) and generated:
        return [safe_text(q) for q in generated[:count]]

    if isinstance(generated, str):
        lines = [
            re.sub(r"^\s*(?:\d+[\).\-\:]|[-•])\s*", "", line).strip()
            for line in generated.splitlines()
        ]
        lines = [line for line in lines if len(line) > 10]
        if lines:
            return lines[:count]

    return fallback_questions(role, interview_type, difficulty, count, resume_text)


def analyze_resume_safely(resume_text):
    if not resume_text.strip() or not AI_ENGINE_AVAILABLE:
        return "Resume ready for role-specific interview generation."

    try:
        return safe_text(analyze_resume(resume_text))
    except Exception:
        return "Resume uploaded successfully. AI interview questions will be generated from the available resume content."


def evaluate_answer_safely(question, answer):
    if not answer.strip():
        return {
            "score": 0,
            "strengths": ["No answer was submitted."],
            "improvements": ["Provide a complete answer before continuing."],
            "summary": "No answer available for evaluation.",
        }

    if AI_ENGINE_AVAILABLE:
        attempts = [
            lambda: evaluate_answer(question, answer, st.session_state.job_role),
            lambda: evaluate_answer(
                question=question,
                answer=answer,
                job_role=st.session_state.job_role,
            ),
            lambda: evaluate_answer(question, answer),
        ]

        for attempt in attempts:
            try:
                result = attempt()
                if isinstance(result, dict):
                    score = result.get("score", result.get("overall_score", 7))
                    return {
                        "score": float(score),
                        "strengths": result.get("strengths", ["Answer submitted successfully."]),
                        "improvements": result.get(
                            "improvements",
                            result.get("areas_for_improvement", ["Add more specific examples."]),
                        ),
                        "summary": result.get(
                            "summary",
                            result.get("feedback", "AI evaluation generated."),
                        ),
                    }
            except TypeError:
                continue
            except Exception:
                break

    words = len(answer.split())
    score = min(10, max(4, round(words / 25 + 5, 1)))
    return {
        "score": score,
        "strengths": [
            "You provided a complete response.",
            "Your answer addressed the interview question.",
        ],
        "improvements": [
            "Use a clearer structure such as STAR or Problem → Action → Result.",
            "Add measurable outcomes and concrete examples.",
        ],
        "summary": "Your answer was recorded. Add more specific technical details and measurable impact for a stronger response.",
    }


def average_score():
    scores = [
        float(item.get("score", 0))
        for item in st.session_state.feedback
        if isinstance(item, dict)
    ]
    return round(sum(scores) / len(scores), 1) if scores else 0.0


def completed_count():
    return len(st.session_state.feedback)


def save_interview_to_history():
    """Save the current interview once per session so dashboard/history stay accurate."""
    if st.session_state.history_saved:
        return

    valid_feedback = [
        item for item in st.session_state.feedback
        if isinstance(item, dict) and item
    ]

    if not valid_feedback:
        return

    record = {
        "job_role": st.session_state.job_role,
        "interview_type": st.session_state.interview_type,
        "difficulty": st.session_state.difficulty,
        "questions": list(st.session_state.questions),
        "answers": list(st.session_state.answers),
        "feedback": list(valid_feedback),
        "average_score": average_score(),
    }

    st.session_state.interview_history.append(record)
    st.session_state.history_saved = True


# ======================================================================
# SIDEBAR
# ======================================================================

with st.sidebar:
    render_html(
        """
        <div class="sidebar-brand">
            <div class="sidebar-logo-row">
                <div class="sidebar-logo-icon">🤖</div>
                <div>
                    <div class="sidebar-logo-title">InterviewAI</div>
                    <div class="sidebar-logo-subtitle">AI Interview Intelligence</div>
                </div>
            </div>
        </div>
        """
    )

    st.caption("MAIN MENU")

    nav_items = [
        ("🏠 Dashboard", "Dashboard"),
        ("🚀 New Interview", "New Interview"),
        ("🕘 Interview History", "Interview History"),
        ("📊 Analytics", "Analytics"),
    ]

    for label, page in nav_items:
        if st.button(label, use_container_width=True, key=f"nav_{page}"):
            st.session_state.current_page = page
            if page in ("Dashboard", "New Interview"):
                st.session_state.interview_started = False
            st.rerun()

    st.divider()
    st.caption("SYSTEM")

    if st.button("⚙️ Profile & Settings", use_container_width=True):
        st.session_state.current_page = "Settings"
        st.rerun()

    if st.session_state.interview_started:
        st.divider()
        if st.button("🔄 End & Start New Interview", use_container_width=True):
            reset_interview()
            st.session_state.current_page = "New Interview"
            st.rerun()

    st.divider()
    render_html(
        """
        <div class="sidebar-status">
            <div class="status-indicator">🟢 AI Systems Online</div>
            <div class="status-version">InterviewAI • SaaS Edition</div>
        </div>
        """
    )




    # =====================================================
    # DASHBOARD DATA
    # =====================================================
def render_dashboard():
    avg = average_score()
    completed = completed_count()

    total_questions = max(1, int(st.session_state.question_count))
    readiness = min(100, int((completed / total_questions) * 100))

    if avg > 0:
        readiness = max(readiness, min(100, int(avg * 10)))

    resume_uploaded = bool(st.session_state.resume_text.strip())
    resume_analysis_available = bool(safe_text(st.session_state.resume_analysis).strip())
    interview_count = len(st.session_state.interview_history)

    # =====================================================
    # HERO SECTION — intentionally preserved as requested
    # =====================================================
    render_html(
        f"""
        <div class="dashboard-hero-premium">

            <div class="dashboard-hero-content">

                <div class="dashboard-kicker">
                    <span class="live-dot"></span>
                    AI INTERVIEW INTELLIGENCE PLATFORM
                </div>

                <h1 class="dashboard-title">
                    Practice Smarter.
                    <span>Perform Better.</span>
                </h1>

                <p class="dashboard-description">
                    Build interview confidence with AI-powered
                    questions, intelligent answer evaluation,
                    personalized feedback, and performance analytics.
                </p>

                <div class="dashboard-status-row">

                    <div class="dashboard-status-pill">
                        🤖 AI Engine Ready
                    </div>

                    <div class="dashboard-status-pill">
                        🎯 {st.session_state.job_role}
                    </div>

                    <div class="dashboard-status-pill">
                        📊 {completed} Answers Evaluated
                    </div>

                </div>

            </div>

            <div class="dashboard-hero-score">

                <div class="hero-score-label">
                    INTERVIEW READINESS
                </div>

                <div class="hero-score-value">
                    {readiness}%
                </div>

                <div class="hero-score-subtitle">
                    Based on your current performance
                </div>

                <div class="hero-progress-track">

                    <div
                        class="hero-progress-fill"
                        style="width:{readiness}%"
                    ></div>

                </div>

            </div>

        </div>
        """
    )

    st.write("")

    # =====================================================
    # PREMIUM QUICK ACTIONS
    # =====================================================
    action1, action2, action3 = st.columns([1.2, 1, 1])

    with action1:
        if st.button(
            "🚀 Start New Interview",
            type="primary",
            use_container_width=True,
            key="dashboard_start_interview",
        ):
            st.session_state.current_page = "New Interview"
            st.session_state.interview_started = False
            st.rerun()

    with action2:
        if st.button(
            "📊 View Analytics",
            use_container_width=True,
            key="dashboard_analytics",
        ):
            st.session_state.current_page = "Analytics"
            st.rerun()

    with action3:
        if st.button(
            "🕘 Interview History",
            use_container_width=True,
            key="dashboard_history",
        ):
            st.session_state.current_page = "Interview History"
            st.rerun()

    st.write("")

    # =====================================================
    # PERFORMANCE OVERVIEW
    # =====================================================
    render_html(
        """
        <div class="premium-section-header">
            <div>
                <div class="premium-section-kicker">PERFORMANCE INTELLIGENCE</div>
                <div class="premium-section-title">Your Interview Performance</div>
            </div>
            <div class="premium-section-status">
                <span class="status-pulse"></span>
                LIVE INSIGHTS
            </div>
        </div>
        """
    )

    metric_data = [
        ("🎯", f"{readiness}%", "Interview Readiness", "Your current preparation level", readiness),
        ("📈", f"{avg:.1f}/10" if avg else "—", "Average Score", "Based on AI-evaluated responses", None),
        ("🔥", str(interview_count), "Interviews Completed", "Sessions tracked in your history", None),
        ("🧠", str(completed), "Answers Analyzed", "Responses evaluated by AI", None),
    ]

    cols = st.columns(4)
    for column, (icon, value, label, description, progress) in zip(cols, metric_data):
        with column:
            progress_html = ""
            if progress is not None:
                progress_html = f"""
                    <div class="metric-progress-track">
                        <div class="metric-progress-fill" style="width:{progress}%"></div>
                    </div>
                """

            render_html(
                f"""
                <div class="premium-metric-card">
                    <div class="metric-card-top">
                        <div class="metric-icon-premium">{icon}</div>
                        <div class="metric-live-dot"></div>
                    </div>
                    <div class="metric-value-premium">{value}</div>
                    <div class="metric-label-premium">{label}</div>
                    <div class="metric-description-premium">{description}</div>
                    {progress_html}
                </div>
                """
            )

    st.write("")

    # =====================================================
    # RESUME INTELLIGENCE + AI COACH
    # =====================================================
    left_col, right_col = st.columns([1.05, 1])

    with left_col:
        resume_status = "Resume Connected" if resume_uploaded else "Resume Required"
        analysis_status = (
            "AI analysis is ready for personalized questions"
            if resume_analysis_available
            else "Upload your resume to unlock deeper personalization"
        )
        resume_icon = "✓" if resume_uploaded else "📄"

        render_html(
            f"""
            <div class="premium-intelligence-card">
                <div class="intelligence-card-header">
                    <div>
                        <div class="premium-section-kicker">RESUME INTELLIGENCE</div>
                        <div class="intelligence-card-title">AI Candidate Profile</div>
                    </div>
                    <div class="intelligence-badge">✦ AI POWERED</div>
                </div>

                <div class="resume-intelligence-status">
                    <div class="resume-status-icon">{resume_icon}</div>
                    <div>
                        <div class="resume-status-title">{resume_status}</div>
                        <div class="resume-status-description">{analysis_status}</div>
                    </div>
                </div>

                <div class="premium-stat-grid">
                    <div class="premium-mini-stat">
                        <div class="mini-stat-value">{completed}</div>
                        <div class="mini-stat-label">Responses Analyzed</div>
                    </div>
                    <div class="premium-mini-stat">
                        <div class="mini-stat-value">{total_questions}</div>
                        <div class="mini-stat-label">Questions Selected</div>
                    </div>
                    <div class="premium-mini-stat">
                        <div class="mini-stat-value">{st.session_state.difficulty}</div>
                        <div class="mini-stat-label">Difficulty</div>
                    </div>
                </div>
            </div>
            """
        )

    with right_col:
        if avg >= 8:
            strength = "Strong technical understanding and consistent answer quality"
            improvement = "Add deeper examples and more measurable outcomes"
            focus = "Practice advanced scenario-based interview questions"
        elif avg >= 6:
            strength = "Good foundation with a developing answer structure"
            improvement = "Improve technical depth and communication confidence"
            focus = "Explain your projects using clearer problem-action-result stories"
        elif completed > 0:
            strength = "You have started building real interview momentum"
            improvement = "Improve answer structure and technical accuracy"
            focus = "Practice role-specific fundamentals with concrete examples"
        else:
            strength = "Your personalized interview workspace is ready"
            improvement = "Complete your first interview to unlock detailed feedback"
            focus = "Start with a role-specific mock interview"

        render_html(
            f"""
            <div class="premium-intelligence-card ai-coach-card">
                <div class="intelligence-card-header">
                    <div>
                        <div class="premium-section-kicker">AI COACH</div>
                        <div class="intelligence-card-title">Your Next Best Move</div>
                    </div>
                    <div class="coach-avatar">✨</div>
                </div>

                <div class="premium-insight-row">
                    <div class="insight-icon strength-icon">💪</div>
                    <div>
                        <div class="insight-title">STRONG AREA</div>
                        <div class="insight-description">{strength}</div>
                    </div>
                </div>

                <div class="premium-insight-row">
                    <div class="insight-icon improve-icon">🎯</div>
                    <div>
                        <div class="insight-title">IMPROVEMENT AREA</div>
                        <div class="insight-description">{improvement}</div>
                    </div>
                </div>

                <div class="premium-insight-row">
                    <div class="insight-icon focus-icon">🚀</div>
                    <div>
                        <div class="insight-title">RECOMMENDED FOCUS</div>
                        <div class="insight-description">{focus}</div>
                    </div>
                </div>
            </div>
            """
        )

    st.write("")

    # =====================================================
    # PREMIUM WORKSPACE CTA
    # =====================================================
    render_html(
        f"""
        <div class="premium-workspace-card">
            <div class="workspace-glow"></div>
            <div class="workspace-content">
                <div class="workspace-left-premium">
                    <div class="workspace-icon">🤖</div>
                    <div>
                        <div class="workspace-kicker">YOUR AI WORKSPACE</div>
                        <div class="workspace-title">Ready to Practice?</div>
                        <div class="workspace-description">
                            Configure your interview and practice {total_questions} personalized questions with AI-powered evaluation and feedback.
                        </div>
                    </div>
                </div>
                <div class="workspace-right-premium">
                    <div class="workspace-meta-pill">💼 {st.session_state.job_role}</div>
                    <div class="workspace-meta-pill">🎯 {st.session_state.interview_type}</div>
                    <div class="workspace-meta-pill">⚡ {st.session_state.difficulty}</div>
                </div>
            </div>
        </div>
        """
    )


# ======================================================================
# NEW INTERVIEW
# ======================================================================

def render_new_interview():
    render_html(
        """
        <div class="page-header">
            <div class="page-kicker">PERSONALIZED INTERVIEW SETUP</div>
            <h1>Build your next AI interview session</h1>
            <p>Configure your role, difficulty and question count. Add your resume for deeper personalization.</p>
        </div>
        """
    )

    left, right = st.columns([1.05, 1])

    with left:
        render_html("<div class='section-heading'>📄 Resume Intelligence</div>")
        st.caption("Upload a PDF resume to personalize questions using your experience and projects.")

        uploaded_resume = st.file_uploader(
            "Upload your resume (PDF)",
            type=["pdf"],
            key="resume_uploader",
        )

        if uploaded_resume is not None:
            if extract_text_from_pdf is None:
                st.warning("Resume parser is not available in utils/resume_parser.py.")
            else:
                try:
                    extracted = extract_text_from_pdf(uploaded_resume)
                    if extracted and extracted.strip():
                        st.session_state.resume_text = extracted
                        st.success("Resume processed successfully.")
                    else:
                        st.warning("No readable text was found in this PDF.")
                except Exception as error:
                    st.error(f"Could not process resume: {error}")

        if st.session_state.resume_text:
            st.caption(
                f"✓ Resume context loaded ({len(st.session_state.resume_text):,} characters)"
            )

    with right:
        render_html("<div class='section-heading'>🎯 Interview Configuration</div>")

        st.session_state.job_role = st.selectbox(
            "Target Job Role",
            [
                "Python Developer",
                "AI/ML Engineer",
                "Data Scientist",
                "Data Analyst",
                "Software Developer",
                "Backend Developer",
            ],
            index=[
                "Python Developer",
                "AI/ML Engineer",
                "Data Scientist",
                "Data Analyst",
                "Software Developer",
                "Backend Developer",
            ].index(st.session_state.job_role)
            if st.session_state.job_role
            in [
                "Python Developer",
                "AI/ML Engineer",
                "Data Scientist",
                "Data Analyst",
                "Software Developer",
                "Backend Developer",
            ]
            else 0,
        )

        st.session_state.interview_type = st.selectbox(
            "Interview Type",
            ["Technical Interview", "HR Interview", "Mixed Interview"],
        )

        st.session_state.difficulty = st.selectbox(
            "Difficulty Level",
            ["Beginner", "Intermediate", "Advanced"],
        )

        st.session_state.question_count = st.select_slider(
            "Number of Questions",
            options=[3, 5, 7, 10],
            value=int(st.session_state.question_count),
        )

    st.divider()

    render_html(
        """
        <div class="ai-intelligence-banner">
            <div>
                <div class="panel-kicker">GENERATIVE AI</div>
                <h2>🧠 AI-powered personalization</h2>
                <p>Questions are tailored around your selected role, interview type, difficulty and resume context.</p>
            </div>
            <div class="ai-status">● READY</div>
        </div>
        """
    )

    st.write("")

    if st.button(
        "🚀 Generate My AI Interview",
        type="primary",
        use_container_width=True,
    ):
        with st.status("🧠 Preparing your personalized interview...", expanded=True) as status:
            if st.session_state.resume_text:
                st.write("Analyzing resume context...")
                st.session_state.resume_analysis = analyze_resume_safely(
                    st.session_state.resume_text
                )

            st.write("Generating role-specific questions...")
            questions = generate_questions_safely()

            if not questions:
                status.update(
                    label="❌ Could not generate interview questions",
                    state="error",
                )
                st.stop()

            st.session_state.questions = questions
            st.session_state.current_question = 0
            st.session_state.answers = [""] * len(questions)
            st.session_state.feedback = []
            st.session_state.answer_submitted = False
            st.session_state.interview_complete = False
            st.session_state.history_saved = False
            st.session_state.captured_photo_questions = []
            st.session_state.webcam_images = []
            st.session_state.interview_started = True

            status.update(
                label="🚀 Your AI interview is ready!",
                state="complete",
            )

        st.rerun()


# ======================================================================
# LIVE INTERVIEW
# ======================================================================

def render_live_interview():
    questions = st.session_state.questions

    if not questions:
        st.warning("No active interview found.")
        if st.button("Create a New Interview"):
            reset_interview()
            st.session_state.current_page = "New Interview"
            st.rerun()
        return

    current_index = int(st.session_state.current_question)
    total_questions = len(questions)

    # Guard against undefined/out-of-range indexes.
    if current_index >= total_questions:
        st.session_state.interview_complete = True
        st.session_state.interview_started = False
        st.session_state.current_page = "Analytics"
        st.rerun()
        return

    progress_percentage = int(
        (current_index / max(1, total_questions)) * 100
    )

    render_html(
        f"""
        <div class="live-session-header">
            <div class="session-kicker">INTERVIEWAI • LIVE SESSION</div>
            <div class="session-title">AI Interview Workspace</div>
            <div class="session-meta-row">
                <div class="session-pill">{st.session_state.job_role}</div>
                <div class="session-pill">{st.session_state.interview_type}</div>
                <div class="session-pill">{st.session_state.difficulty}</div>
                <div class="session-pill session-pill-active">Question {current_index + 1} / {total_questions}</div>
            </div>
            <div class="session-progress-label">{progress_percentage}% completed</div>
        </div>
        """
    )

    st.progress(progress_percentage / 100)

    render_html(
        f"""
        <div class="question-card-premium">
            <div class="question-label">AI INTERVIEW QUESTION</div>
            <div class="question-number">QUESTION {current_index + 1:02d}</div>
            <div class="question-text">{questions[current_index]}</div>
        </div>
        """
    )

    voice_col, camera_col = st.columns(2)

    with voice_col:
        render_html(
            """
            <div class="workspace-card">
                <h2>🎙️ Voice Typing</h2>
                <p>Record your answer, convert it to text, then edit before submitting.</p>
            </div>
            """
        )

        audio = None
        if hasattr(st, "audio_input"):
            audio = st.audio_input(
                "Record your answer",
                key=f"audio_{current_index}",
            )
        else:
            st.info(
                "Your Streamlit version does not support audio_input. "
                "Update Streamlit for built-in voice recording."
            )

        if audio is not None:
            st.audio(audio)

            if st.button(
                "✨ Convert Voice to Text",
                use_container_width=True,
                key=f"transcribe_{current_index}",
            ):
                with st.spinner("Transcribing your response..."):
                    transcript, error = transcribe_audio(audio)

                if error:
                    st.warning(error)
                elif transcript:
                    st.session_state.answers[current_index] = transcript
                    st.success("Voice converted to text.")
                    st.rerun()

    with camera_col:
        render_html(
            """
            <div class="workspace-card">
                <h2>📷 Interview Webcam</h2>
                <p>Optional camera capture for a more realistic interview practice experience.</p>
            </div>
            """
        )

        photo = st.camera_input(
            "Enable webcam and capture",
            key=f"camera_{current_index}",
        )

        if photo is not None:
            if current_index not in st.session_state.captured_photo_questions:
                st.session_state.webcam_images.append(photo.getvalue())
                st.session_state.captured_photo_questions.append(current_index)
                st.success("Webcam image captured successfully.")
            else:
                st.caption("Webcam image already saved for this question.")

    st.divider()

    render_html(
        """
        <div class="answer-workspace-heading">
            <div class="panel-kicker">RESPONSE WORKSPACE</div>
            <h2>📝 Craft your answer</h2>
            <p>Use a clear structure, include technical details, and support your answer with real examples.</p>
        </div>
        """
    )

    answer = st.text_area(
        "Your Answer",
        value=st.session_state.answers[current_index],
        height=240,
        placeholder="Start typing your answer or use Voice Typing above...",
        key=f"answer_input_{current_index}",
        label_visibility="collapsed",
    )

    st.session_state.answers[current_index] = answer

    b1, b2 = st.columns([3, 1])

    with b1:
        submit_clicked = st.button(
            "✨ Submit Answer & Get AI Feedback",
            type="primary",
            use_container_width=True,
            key=f"submit_{current_index}",
        )

    with b2:
        end_clicked = st.button(
            "End Interview",
            use_container_width=True,
            key=f"end_{current_index}",
        )

    if end_clicked:
        save_interview_to_history()
        st.session_state.interview_started = False
        st.session_state.interview_complete = True
        st.session_state.current_page = "Analytics"
        st.rerun()

    if submit_clicked:
        if not answer.strip():
            st.warning("Please provide an answer before submitting.")
        else:
            with st.spinner("AI is evaluating your answer..."):
                result = evaluate_answer_safely(
                    questions[current_index],
                    answer,
                )

            # Replace existing feedback if user resubmits the same question.
            while len(st.session_state.feedback) <= current_index:
                st.session_state.feedback.append({})

            st.session_state.feedback[current_index] = result
            st.session_state.answer_submitted = True

    if (
        st.session_state.answer_submitted
        and len(st.session_state.feedback) > current_index
        and st.session_state.feedback[current_index]
    ):
        result = st.session_state.feedback[current_index]
        score = float(result.get("score", 0))

        render_html(
            f"""
            <div class="feedback-card">
                <div class="feedback-topline">
                    <span>AI FEEDBACK</span>
                    <strong>{score:.1f}/10</strong>
                </div>
                <p>{safe_text(result.get("summary", ""))}</p>
            </div>
            """
        )

        f1, f2 = st.columns(2)

        with f1:
            st.subheader("✅ Strengths")
            for item in result.get("strengths", []):
                st.write(f"• {safe_text(item)}")

        with f2:
            st.subheader("🚀 Improve Next")
            for item in result.get("improvements", []):
                st.write(f"• {safe_text(item)}")

        if current_index < total_questions - 1:
            if st.button(
                "Next Question →",
                type="primary",
                use_container_width=True,
                key=f"next_{current_index}",
            ):
                st.session_state.current_question += 1
                st.session_state.answer_submitted = False
                st.rerun()
        else:
            if st.button(
                "🏁 Finish Interview & View Analytics",
                type="primary",
                use_container_width=True,
                key="finish_interview",
            ):
                save_interview_to_history()
                st.session_state.interview_started = False
                st.session_state.interview_complete = True
                st.session_state.current_page = "Analytics"
                st.rerun()


# ======================================================================
# ANALYTICS
# ======================================================================

def render_analytics():
    render_html(
        """
        <div class="page-header">
            <div class="page-kicker">PERFORMANCE INTELLIGENCE</div>
            <h1>Your Interview Analytics</h1>
            <p>Review your scores and identify the next areas to improve.</p>
        </div>
        """
    )

    feedback = [
        item for item in st.session_state.feedback
        if isinstance(item, dict) and item
    ]

    if not feedback:
        st.info("Complete an interview to unlock personalized analytics.")
        if st.button("🚀 Start an Interview", type="primary"):
            st.session_state.current_page = "New Interview"
            st.rerun()
        return

    scores = [
        float(item.get("score", 0))
        for item in feedback
    ]
    avg = round(sum(scores) / len(scores), 1)
    best = max(scores)
    weakest = min(scores)

    c1, c2, c3, c4 = st.columns(4)
    for col, icon, value, label in [
        (c1, "🎯", f"{avg}/10", "Average Score"),
        (c2, "🏆", f"{best}/10", "Best Score"),
        (c3, "🔎", f"{weakest}/10", "Lowest Score"),
        (c4, "📝", str(len(scores)), "Answers Evaluated"),
    ]:
        with col:
            render_html(
                f"""
                <div class="saas-metric-card">
                    <div class="metric-icon">{icon}</div>
                    <div class="metric-value">{value}</div>
                    <div class="metric-label">{label}</div>
                </div>
                """
            )

    st.write("")

    if PLOTLY_AVAILABLE:
        fig = go.Figure(
            data=[
                go.Scatter(
                    x=[f"Q{i + 1}" for i in range(len(scores))],
                    y=scores,
                    mode="lines+markers",
                    fill="tozeroy",
                    hovertemplate="Question %{x}<br>Score %{y:.1f}/10<extra></extra>",
                )
            ]
        )
        fig.update_layout(
            title="Performance Across Questions",
            template="plotly_dark",
            height=380,
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            yaxis=dict(range=[0, 10], title="Score"),
            xaxis=dict(title="Question"),
            margin=dict(l=20, r=20, t=60, b=20),
        )
        st.plotly_chart(fig, use_container_width=True)

    st.subheader("🧠 AI Review")

    for index, item in enumerate(feedback, start=1):
        with st.expander(
            f"Question {index} • Score {float(item.get('score', 0)):.1f}/10"
        ):
            st.write("**Summary:**", safe_text(item.get("summary", "")))
            st.write("**Strengths:**")
            for strength in item.get("strengths", []):
                st.write(f"• {safe_text(strength)}")

            st.write("**Improve:**")
            for improvement in item.get("improvements", []):
                st.write(f"• {safe_text(improvement)}")

    st.divider()

    if generate_interview_report is not None:
        if st.button("📄 Generate Interview Report"):
            try:
                report = generate_interview_report(
                    st.session_state.questions,
                    st.session_state.answers,
                    st.session_state.feedback,
                )
                if report:
                    st.download_button(
                        "⬇️ Download Interview Report",
                        data=report,
                        file_name="InterviewAI_Interview_Report.pdf",
                        mime="application/pdf",
                    )
            except Exception as error:
                st.warning(f"Report generation is not available: {error}")


# ======================================================================
# HISTORY
# ======================================================================

def render_history():
    render_html(
        """
        <div class="page-header">
            <div class="page-kicker">SESSION HISTORY</div>
            <h1>Your Interview Activity</h1>
            <p>Review completed interview sessions and track your progress over time.</p>
        </div>
        """
    )

    history = list(reversed(st.session_state.interview_history))

    if not history:
        st.info("No completed interviews yet. Complete an interview to build your history.")
        if st.button("🚀 Start Your First Interview", type="primary"):
            st.session_state.current_page = "New Interview"
            st.rerun()
        return

    for display_index, record in enumerate(history, start=1):
        score = safe_text(record.get("average_score", 0))
        role = safe_text(record.get("job_role", "Interview"))
        interview_type = safe_text(record.get("interview_type", ""))
        difficulty = safe_text(record.get("difficulty", ""))
        question_total = len(record.get("questions", []))

        render_html(
            f"""
            <div class="premium-history-card">
                <div>
                    <div class="premium-section-kicker">COMPLETED SESSION {len(history) - display_index + 1}</div>
                    <div class="history-title">{role}</div>
                    <div class="history-meta">{interview_type} • {difficulty} • {question_total} questions</div>
                </div>
                <div class="history-score">{score}/10</div>
            </div>
            """
        )


# ======================================================================
# SETTINGS
# ======================================================================

def render_settings():
    render_html(
        """
        <div class="page-header">
            <div class="page-kicker">PRODUCT SETTINGS</div>
            <h1>Profile & Settings</h1>
            <p>Manage your InterviewAI experience.</p>
        </div>
        """
    )

    st.text_input("Display Name", value="InterviewAI User")
    st.toggle("Enable AI feedback", value=True)
    st.toggle("Enable webcam capture", value=True)
    st.toggle("Enable voice typing", value=True)

    if st.button("Save Settings", type="primary"):
        st.success("Settings saved for this session.")


# ======================================================================
# ROUTER
# ======================================================================

if st.session_state.interview_started:
    render_live_interview()
else:
    page = st.session_state.current_page

    if page == "Dashboard":
        render_dashboard()
    elif page == "New Interview":
        render_new_interview()
    elif page == "Interview History":
        render_history()
    elif page == "Analytics":
        render_analytics()
    elif page == "Settings":
        render_settings()
    else:
        st.session_state.current_page = "Dashboard"
        st.rerun()
