"""state.py - session-state defaults. Original keys are preserved unchanged."""
import streamlit as st

# Keys that existed in the original app.py
ORIGINAL_DEFAULTS = {
    "step": 1,
    "subject_category": None,
    "topic": None,
    "knowledge_level": None,
    "learning_goal": None,
    "time_available": None,
    "learning_style": None,
    "student_analysis": None,
    "learning_roadmap": None,
    "learning_resources": None,
    "handler": None,
    "uploaded_files_count": 0,
}

# New keys used by the redesigned interface
UI_DEFAULTS = {
    "page": "Home",
    "nav_radio": "Home",
    "provider": "groq",
    "selected_model": "llama-3.3-70b-versatile",
    "activity_log": [],
    "tutor_messages": [],
    "rag_docs": [],          # [{name, size, status}] for this session
    "rag_seen": [],          # fingerprints already ingested (prevents duplicate chunks)
    "rag_history": [],       # [{q, a}]
    "phase_done": {},        # {phase_index: bool} ticked by the student
    "quiz_questions": [],
    "quiz_answers": {},
    "quiz_pos": 0,
    "quiz_submitted": False,
    "n_quizzes": 0,
    "n_quizzes_completed": 0,
    "n_tutor": 0,
    "n_rag": 0,
}


def init_state() -> None:
    for k, v in {**ORIGINAL_DEFAULTS, **UI_DEFAULTS}.items():
        if k not in st.session_state:
            st.session_state[k] = list(v) if isinstance(v, list) else dict(v) if isinstance(v, dict) else v


def reset_plan() -> None:
    """Equivalent of the original 'Start New Learning Plan' button."""
    keep = {"provider", "selected_model"}
    for k in list(st.session_state.keys()):
        if k not in keep:
            del st.session_state[k]
    init_state()
    st.session_state.page = "Student Analyzer"
    st.session_state.nav_radio = "Student Analyzer"
