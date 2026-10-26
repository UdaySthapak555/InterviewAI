import os
import time
import json
import re

from dotenv import load_dotenv
from google import genai


# =========================================================
# LOAD ENVIRONMENT VARIABLES
# =========================================================

load_dotenv()


# =========================================================
# GEMINI API KEY
# =========================================================

api_key = os.getenv("GEMINI_API_KEY")


if not api_key:

    raise ValueError(
        "GEMINI_API_KEY was not found in the .env file."
    )


# =========================================================
# GEMINI CLIENT
# =========================================================

client = genai.Client(
    api_key=api_key
)


# =========================================================
# MODEL
# =========================================================

MODEL_NAME = "gemini-3.1-flash-lite"


# =========================================================
# AI RESPONSE HELPER
# =========================================================

def generate_ai_response(
    prompt,
    retries=3
):

    last_error = None


    for attempt in range(retries):

        try:

            response = client.models.generate_content(
                model=MODEL_NAME,
                contents=prompt
            )


            response_text = getattr(
                response,
                "text",
                None
            )


            if not response_text:

                raise ValueError(
                    "Empty response received from Gemini."
                )


            return response_text.strip()


        except Exception as error:

            last_error = error


            if attempt < retries - 1:

                time.sleep(
                    3 * (attempt + 1)
                )


    raise last_error


# =========================================================
# JSON CLEANER
# =========================================================

def clean_json_response(
    response_text
):

    response_text = (
        response_text.strip()
    )


    # Remove markdown opening fence

    response_text = re.sub(
        r"^```(?:json)?\s*",
        "",
        response_text,
        flags=re.IGNORECASE
    )


    # Remove markdown closing fence

    response_text = re.sub(
        r"\s*```$",
        "",
        response_text
    )


    # Find JSON object

    json_match = re.search(
        r"\{.*\}",
        response_text,
        flags=re.DOTALL
    )


    if json_match:

        response_text = (
            json_match.group(0)
        )


    return json.loads(
        response_text
    )


# =========================================================
# NORMALIZE LIST ITEMS
# =========================================================

def normalize_string_list(
    items
):

    if not items:

        return []


    if not isinstance(
        items,
        list
    ):

        items = [items]


    normalized = []


    for item in items:

        if isinstance(
            item,
            dict
        ):

            skill = item.get(
                "skill",
                item.get(
                    "name",
                    str(item)
                )
            )


            normalized.append(
                str(skill)
            )


        else:

            normalized.append(
                str(item)
            )


    return normalized


# =========================================================
# RESUME ANALYSIS
# =========================================================

def analyze_resume(
    resume_text,
    job_role
):

    prompt = f"""
You are an expert technical recruiter and interview preparation assistant.

Analyze the following candidate resume for the target job role.

TARGET JOB ROLE:
{job_role}

RESUME:
{resume_text}

Provide the analysis using these headings:

## Candidate Summary

## Technical Skills

## Projects

## Strong Areas

## Interview Focus Areas

Keep the response clear, structured and concise.
"""


    return generate_ai_response(
        prompt
    )


# =========================================================
# QUESTION GENERATION
# =========================================================

def generate_interview_questions(

    resume_text,

    resume_analysis,

    job_role,

    interview_type,

    difficulty

):

    prompt = f"""
You are an expert AI interviewer.

Create a personalized mock interview.

TARGET JOB ROLE:
{job_role}

INTERVIEW TYPE:
{interview_type}

DIFFICULTY:
{difficulty}

CANDIDATE RESUME:
{resume_text}

RESUME ANALYSIS:
{resume_analysis}

Generate exactly 10 interview questions.

RULES:

1. Personalize questions using the candidate's actual skills.
2. Use the candidate's projects where relevant.
3. Match the selected job role.
4. Match the selected interview type.
5. Match the selected difficulty.
6. Avoid duplicate questions.
7. Include practical and scenario-based questions.
8. Do not generate headings.

Return only a numbered list:

1. Question
2. Question
...
10. Question
"""


    return generate_ai_response(
        prompt
    )


# =========================================================
# EXTRACT QUESTIONS
# =========================================================

def extract_questions(
    response_text
):

    if not response_text:

        return []


    questions = []


    lines = (
        response_text.splitlines()
    )


    for line in lines:

        line = line.strip()


        if not line:

            continue


        match = re.match(
            r"^\s*\d+\s*[\.\)\:\-]\s*(.+)",
            line
        )


        if match:

            question = (
                match.group(1).strip()
            )


            if question:

                questions.append(
                    question
                )


    # Fallback

    if not questions:

        parts = re.split(
            r"\n?\s*\d+\s*[\.\)\:\-]\s*",
            response_text
        )


        for part in parts:

            part = part.strip()


            if len(part) > 10:

                questions.append(
                    part.replace(
                        "\n",
                        " "
                    )
                )


    # Remove duplicates

    unique_questions = []


    for question in questions:

        if question not in unique_questions:

            unique_questions.append(
                question
            )


    return unique_questions[:10]


# =========================================================
# ANSWER EVALUATION
# =========================================================

def evaluate_answer(

    question,

    answer,

    resume_text,

    job_role,

    difficulty

):

    prompt = f"""
You are an expert technical interviewer.

Evaluate the candidate's answer.

JOB ROLE:
{job_role}

DIFFICULTY:
{difficulty}

RESUME:
{resume_text}

QUESTION:
{question}

CANDIDATE ANSWER:
{answer}

Return ONLY valid JSON.

Use exactly this structure:

{{
    "score": 8.5,

    "strengths": [
        "Strength 1",
        "Strength 2",
        "Strength 3"
    ],

    "improvements": [
        "Improvement 1",
        "Improvement 2",
        "Improvement 3"
    ],

    "better_answer": "A stronger example answer."
}}

RULES:

1. Score must be between 0 and 10.
2. Evaluate correctness.
3. Evaluate technical depth.
4. Evaluate clarity.
5. Evaluate relevance.
6. Return JSON only.
"""


    try:

        response_text = (
            generate_ai_response(
                prompt
            )
        )


        evaluation = (
            clean_json_response(
                response_text
            )
        )


        evaluation["score"] = float(
            evaluation.get(
                "score",
                0
            )
        )


        evaluation["score"] = max(
            0,
            min(
                10,
                evaluation["score"]
            )
        )


        evaluation["strengths"] = (
            normalize_string_list(
                evaluation.get(
                    "strengths",
                    []
                )
            )
        )


        evaluation["improvements"] = (
            normalize_string_list(
                evaluation.get(
                    "improvements",
                    []
                )
            )
        )


        evaluation["better_answer"] = str(
            evaluation.get(
                "better_answer",
                ""
            )
        )


        return evaluation


    except Exception as error:

        return {

            "score": 0.0,

            "strengths": [
                "Answer was submitted successfully."
            ],

            "improvements": [
                "AI evaluation could not be processed. Please try again."
            ],

            "better_answer": (
                "Unable to generate an improved answer at this moment."
            )

        }


# =========================================================
# ADVANCED INTERVIEW INSIGHTS
# =========================================================

def generate_interview_insights(

    questions,

    answers,

    feedback,

    job_role

):

    prompt = f"""
You are an expert interview coach and technical recruiter.

Analyze this complete interview.

TARGET JOB ROLE:
{job_role}

QUESTIONS:
{json.dumps(questions, indent=2)}

CANDIDATE ANSWERS:
{json.dumps(answers, indent=2)}

QUESTION FEEDBACK:
{json.dumps(feedback, indent=2)}

Return ONLY valid JSON.

Use EXACTLY this structure:

{{
    "technical_score": 75,

    "communication_score": 70,

    "confidence_score": 65,

    "problem_solving_score": 72,

    "interview_readiness": "Developing",

    "overall_summary": "Brief performance summary.",

    "strong_areas": [
        "Area 1",
        "Area 2",
        "Area 3"
    ],

    "weak_areas": [
        "Area 1",
        "Area 2",
        "Area 3"
    ]
}}

RULES:

1. All score values must be between 0 and 100.
2. Use the candidate's actual answers and feedback.
3. Interview readiness must be one of:
   "Beginner",
   "Developing",
   "Interview Ready",
   "Highly Prepared".
4. Return only JSON.
"""


    try:

        response_text = (
            generate_ai_response(
                prompt
            )
        )


        insights = (
            clean_json_response(
                response_text
            )
        )


        score_keys = [

            "technical_score",

            "communication_score",

            "confidence_score",

            "problem_solving_score"

        ]


        for key in score_keys:

            try:

                value = float(
                    insights.get(
                        key,
                        0
                    )
                )


                insights[key] = max(
                    0,
                    min(
                        100,
                        value
                    )
                )


            except (
                TypeError,
                ValueError
            ):

                insights[key] = 0


        insights["strong_areas"] = (
            normalize_string_list(
                insights.get(
                    "strong_areas",
                    []
                )
            )
        )


        insights["weak_areas"] = (
            normalize_string_list(
                insights.get(
                    "weak_areas",
                    []
                )
            )
        )


        insights["overall_summary"] = str(
            insights.get(
                "overall_summary",
                ""
            )
        )


        return insights


    except Exception:

        return {

            "technical_score": 0,

            "communication_score": 0,

            "confidence_score": 0,

            "problem_solving_score": 0,

            "interview_readiness": "Developing",

            "overall_summary": (
                "Your interview has been completed. Continue "
                "practicing your technical and communication skills."
            ),

            "strong_areas": [],

            "weak_areas": []

        }


# =========================================================
# SKILL GAP ANALYSIS
# =========================================================

def generate_skill_gap_analysis(

    resume_text,

    resume_analysis,

    job_role,

    questions,

    feedback

):

    prompt = f"""
You are an expert technical recruiter and AI career coach.

Perform a skill gap analysis.

TARGET JOB ROLE:
{job_role}

CANDIDATE RESUME:
{resume_text}

RESUME ANALYSIS:
{resume_analysis}

INTERVIEW QUESTIONS:
{json.dumps(questions, indent=2)}

INTERVIEW FEEDBACK:
{json.dumps(feedback, indent=2)}

Return ONLY valid JSON.

Use EXACTLY this structure:

{{
    "skill_match_percentage": 70,

    "strong_skills": [
        "Skill 1",
        "Skill 2",
        "Skill 3"
    ],

    "skills_to_improve": [
        "Skill 1",
        "Skill 2",
        "Skill 3"
    ],

    "missing_skills": [
        "Skill 1",
        "Skill 2",
        "Skill 3"
    ],

    "recommended_skills": [
        "Skill 1",
        "Skill 2",
        "Skill 3"
    ],

    "career_advice": "Practical personalized career advice."
}}

RULES:

1. Skill match percentage must be between 0 and 100.
2. Use resume and interview performance.
3. Do not invent irrelevant skills.
4. Prioritize skills for the selected job role.
5. Return only JSON.
"""


    try:

        response_text = (
            generate_ai_response(
                prompt
            )
        )


        result = (
            clean_json_response(
                response_text
            )
        )


        try:

            result["skill_match_percentage"] = max(
                0,
                min(
                    100,
                    float(
                        result.get(
                            "skill_match_percentage",
                            0
                        )
                    )
                )
            )


        except (
            TypeError,
            ValueError
        ):

            result[
                "skill_match_percentage"
            ] = 0


        list_keys = [

            "strong_skills",

            "skills_to_improve",

            "missing_skills",

            "recommended_skills"

        ]


        for key in list_keys:

            result[key] = (
                normalize_string_list(
                    result.get(
                        key,
                        []
                    )
                )
            )


        result["career_advice"] = str(
            result.get(
                "career_advice",
                ""
            )
        )


        return result


    except Exception:

        return {

            "skill_match_percentage": 0,

            "strong_skills": [],

            "skills_to_improve": [],

            "missing_skills": [],

            "recommended_skills": [],

            "career_advice": (
                "Continue strengthening the skills required "
                "for your selected job role."
            )

        }


# =========================================================
# PERSONALIZED 4-WEEK ROADMAP
# =========================================================

def generate_improvement_roadmap(

    job_role,

    interview_insights,

    skill_gap

):

    prompt = f"""
You are an expert technical career mentor.

Create a personalized four-week improvement roadmap.

TARGET JOB ROLE:
{job_role}

INTERVIEW INSIGHTS:
{json.dumps(interview_insights, indent=2)}

SKILL GAP ANALYSIS:
{json.dumps(skill_gap, indent=2)}

Return ONLY valid JSON.

Use EXACTLY this structure:

{{
    "week_1": {{
        "title": "Foundation",
        "focus": [
            "Task 1",
            "Task 2",
            "Task 3"
        ]
    }},

    "week_2": {{
        "title": "Core Skills",
        "focus": [
            "Task 1",
            "Task 2",
            "Task 3"
        ]
    }},

    "week_3": {{
        "title": "Practical Growth",
        "focus": [
            "Task 1",
            "Task 2",
            "Task 3"
        ]
    }},

    "week_4": {{
        "title": "Interview Ready",
        "focus": [
            "Task 1",
            "Task 2",
            "Task 3"
        ]
    }},

    "final_advice": "Motivational and practical next step."
}}

RULES:

1. Create exactly four weeks.
2. Make tasks practical.
3. Focus on weak and missing skills.
4. Include technical preparation and interview preparation.
5. Keep each week realistic.
6. Return only JSON.
"""


    try:

        response_text = (
            generate_ai_response(
                prompt
            )
        )


        roadmap = (
            clean_json_response(
                response_text
            )
        )


        for week in [

            "week_1",

            "week_2",

            "week_3",

            "week_4"

        ]:

            if not isinstance(
                roadmap.get(
                    week
                ),
                dict
            ):

                roadmap[week] = {}


            roadmap[week]["title"] = str(
                roadmap[week].get(
                    "title",
                    ""
                )
            )


            roadmap[week]["focus"] = (
                normalize_string_list(
                    roadmap[week].get(
                        "focus",
                        []
                    )
                )
            )


        roadmap["final_advice"] = str(
            roadmap.get(
                "final_advice",
                ""
            )
        )


        return roadmap


    except Exception:

        return {

            "week_1": {
                "title": "Foundation",
                "focus": []
            },

            "week_2": {
                "title": "Core Skills",
                "focus": []
            },

            "week_3": {
                "title": "Practical Growth",
                "focus": []
            },

            "week_4": {
                "title": "Interview Ready",
                "focus": []
            },

            "final_advice": (
                f"Continue practicing consistently to prepare "
                f"for the {job_role} role."
            )

        }