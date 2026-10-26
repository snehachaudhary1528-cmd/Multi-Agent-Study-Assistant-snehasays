import streamlit as st

from agent_handler import StudyAssistantHandler
from config import ConfigManager
from parsers import split_sections
from ui import (bump, chips, esc, goto, html, log_activity, nav_button,
                ornament, page_header)

TIME_OPTIONS = [
    "1-2 hours per week", "3-5 hours per week", "6-10 hours per week",
    "10+ hours per week", "Full-time (30+ hours per week)",
]
CATEGORY_LABELS = {
    "programming": "Programming", "mathematics": "Mathematics", "science": "Science",
    "languages": "Languages", "business": "Business", "test_preparation": "Test Preparation",
}


def run_pipeline() -> bool:
    """
    Same sequence as the original step 3: build the handler, analyse the student,
    create the roadmap, find resources. The handler methods own their st.status UI.
    """
    ss = st.session_state
    try:
        if not ss.handler:
            ss.handler = StudyAssistantHandler(
                topic=ss.topic, subject_category=ss.subject_category,
                knowledge_level=ss.knowledge_level, learning_goal=ss.learning_goal,
                time_available=ss.time_available, learning_style=ss.learning_style,
                model_name=ss.selected_model, provider=ss.provider,
            )
        if not ss.student_analysis:
            ss.handler.analyze_student()
            log_activity("Student analysis completed")
        if ss.student_analysis and not ss.learning_roadmap:
            ss.handler.create_roadmap(ss.student_analysis)
            ss.phase_done = {}
            log_activity("Learning roadmap created")
        if ss.learning_roadmap and not ss.learning_resources:
            ss.handler.find_resources()
            log_activity("Learning resources found")
    except Exception as exc:  # network/API/key problems surface here
        st.error(
            f"The agents could not finish: {exc}. Check that the API key for "
            f"'{ss.provider}' is set in your .env file, then try again."
        )
        return False
    if ss.student_analysis and ss.learning_roadmap and ss.learning_resources:
        ss.step = 4
        return True
    return False


def _analysis_cards(md: str) -> None:
    sections = split_sections(md)
    if not sections:
        with st.container(key="card_analysis_all"):
            st.markdown(md)
        return
    cols = st.columns(2)
    for i, sec in enumerate(sections):
        with cols[i % 2]:
            with st.container(key=f"card_analysis_{i}"):
                html(f'<div class="card-title">{esc(sec["title"])}</div>')
                st.markdown(sec["body"])


def render():
    ss = st.session_state
    page_header(
        "Agent 01 · Student Analyzer",
        "Tell us how you <em>learn</em>",
        "Share your topic, level and goals. The analyzer reads your profile, then the roadmap and "
        "resource agents build on it.",
    )

    cfg = ConfigManager()

    with st.container(key="card_profile_form"):
        categories = cfg.get_all_subject_categories()
        cat_idx = categories.index(ss.subject_category) if ss.subject_category in categories else 0
        c1, c2 = st.columns(2, gap="large")
        with c1:
            category = st.selectbox(
                "Subject category", categories, index=cat_idx,
                format_func=lambda c: CATEGORY_LABELS.get(c, c.replace("_", " ").title()),
            )
            info = cfg.get_subject_category_info(category)
            if info:
                st.caption(
                    f"Topics include: {', '.join(info.get('topics', []))} · "
                    f"Typical duration: {info.get('typical_duration', 'Varies')}"
                )
            topic = st.text_input(
                "Specific topic", value=ss.topic or "",
                placeholder="e.g., Python for Data Science, Operating Systems, Computer Networks",
            )
            levels = cfg.get_all_knowledge_levels()
            lv_idx = levels.index(ss.knowledge_level) if ss.knowledge_level in levels else 0
            level = st.selectbox("Current knowledge level", levels, index=lv_idx, format_func=str.title)
            li = cfg.get_knowledge_level_info(level)
            if li:
                st.caption(li.get("description", ""))
        with c2:
            goal = st.text_area(
                "What do you want to achieve?", value=ss.learning_goal or "", height=118,
                placeholder="e.g., Prepare for AKTU semester exams, build a major project, core concept clarity",
            )
            t_idx = TIME_OPTIONS.index(ss.time_available) if ss.time_available in TIME_OPTIONS else 0
            time_available = st.selectbox("Time you can dedicate", TIME_OPTIONS, index=t_idx)
            styles = cfg.get_all_learning_styles()
            s_idx = styles.index(ss.learning_style) if ss.learning_style in styles else 0
            style = st.selectbox(
                "Preferred learning style", styles, index=s_idx,
                format_func=lambda s: s.replace("_", " ").title(),
            )
            si = cfg.get_learning_style_info(style)
            if si:
                st.caption(si.get("description", ""))

        existing = bool(ss.student_analysis)
        label = "Re-analyse and rebuild my plan" if existing else "Analyze & build my learning plan"
        clicked = st.button(label, type="primary", disabled=not (topic.strip() and goal.strip()))
        if existing:
            st.caption("Re-analysing replaces your current analysis, roadmap and resources.")

    if clicked:
        if existing:  # same reset the original 'start new plan' performed for plan data
            for k in ("student_analysis", "learning_roadmap", "learning_resources", "handler"):
                ss[k] = None
            ss.phase_done = {}
            ss.quiz_questions, ss.quiz_answers, ss.quiz_submitted, ss.quiz_pos = [], {}, False, 0
        ss.subject_category, ss.topic, ss.knowledge_level = category, topic.strip(), level
        ss.learning_goal, ss.time_available, ss.learning_style = goal.strip(), time_available, style
        ss.step = 3
        with st.container(key="card_pipeline"):
            html('<div class="card-title">Your agents are at work</div>')
            ok = run_pipeline()
        if ok:
            st.rerun()

    if ss.student_analysis:
        ornament("Analysis")
        html(
            f'<div style="margin-bottom:1rem">{chips([ss.topic, str(ss.knowledge_level).title(), ss.time_available, str(ss.learning_style).replace("_"," ").title()])}</div>'
        )
        _analysis_cards(ss.student_analysis)
        st.write("")
        a, b, _ = st.columns([1.3, 1.3, 2.4])
        with a:
            nav_button("View my roadmap", "Roadmap Creator", "an_to_roadmap", kind="primary", use_container_width=True)
        with b:
            nav_button("Open dashboard", "Dashboard", "an_to_dash", use_container_width=True)
        if not ss.learning_roadmap or not ss.learning_resources:
            st.warning("Your plan is incomplete. The remaining agents can pick up where they stopped.")
            if st.button("Run the remaining agents", type="primary"):
                if run_pipeline():
                    st.rerun()
