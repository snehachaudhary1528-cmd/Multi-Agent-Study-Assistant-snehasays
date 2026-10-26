import streamlit as st

from art import AGENTS
from parsers import parse_resources, parse_roadmap
from state import reset_plan
from ui import (chips, esc, has_profile, html, icon, nav_button, ornament,
                page_header, stat_card)


def _next_steps():
    """Rule-based suggestions derived from what the student has actually done."""
    ss = st.session_state
    steps = []
    if not ss.learning_roadmap:
        steps.append(("roadmap", "Create your roadmap", "Your analysis is ready; turn it into phases.", "Roadmap Creator"))
    else:
        rm = parse_roadmap(ss.learning_roadmap)
        if rm and not any(ss.phase_done.values()):
            steps.append(("roadmap", "Start Phase 1", "Open the roadmap and begin with the first phase.", "Roadmap Creator"))
    if ss.n_quizzes == 0:
        steps.append(("quiz", "Take a first quiz", "Check where you stand before going deeper.", "Quiz Generator"))
    if ss.n_tutor == 0:
        steps.append(("tutor", "Ask the AI Tutor", "Bring one concept you find difficult.", "AI Tutor"))
    if ss.handler and ss.handler.get_document_count() == 0:
        steps.append(("rag", "Upload your notes", "Ask questions grounded in your own documents.", "Document Intelligence"))
    if not steps:
        steps.append(("resources", "Explore your resources", "Revisit the materials curated for you.", "Resource Finder"))
    return steps[:3]


def render():
    ss = st.session_state
    page_header(
        "Dashboard", "Welcome to your <em>learning space.</em>",
        "Every great achievement begins with a curious mind.",
    )

    if not has_profile():
        with st.container(key="card_dash_empty"):
            html(
                f"""<div class="empty-state" style="padding-top:1rem"><div class="empty-ic">{icon("book", 34)}</div>
                <h3>Your space is ready, and empty</h3>
                <p>Create a learning profile and this dashboard will fill with your plan, progress and activity.</p></div>"""
            )
            _, mid, _ = st.columns([1, 1.2, 1])
            with mid:
                nav_button("Begin with the Student Analyzer", "Student Analyzer", "dash_begin", kind="primary", use_container_width=True)
    else:
        left, right = st.columns([1.5, 1], gap="large")
        with left:
            html(
                f"""<div class="profile-card"><div class="eyebrow">Your learning profile</div>
                <h3>{esc(ss.topic)}</h3>
                {chips([str(ss.knowledge_level).title(), ss.time_available, str(ss.learning_style).replace("_", " ").title(), str(ss.subject_category).replace("_", " ").title()])}
                <p><b style="color:var(--gold)">Goal:</b> {esc(ss.learning_goal)}</p></div>"""
            )
        with right:
            with st.container(key="card_dash_actions"):
                html('<div class="card-title">Quick actions</div>')
                nav_button("Edit my profile", "Student Analyzer", "dash_edit", use_container_width=True)
                st.button("Start a new learning plan", key="dash_reset", on_click=reset_plan, use_container_width=True)

    # ---- Real statistics only ----
    st.write("")
    roadmap = parse_roadmap(ss.learning_roadmap) if ss.learning_roadmap else None
    n_phases = len(roadmap["phases"]) if roadmap else 0
    done = sum(1 for i in range(n_phases) if ss.phase_done.get(i))
    docs = ss.handler.get_document_count() if ss.handler else 0
    n_res = len(parse_resources(ss.learning_resources)) if ss.learning_resources else 0
    cols = st.columns(4)
    cards = [
        stat_card("Quizzes generated", ss.n_quizzes, "quiz", f"{ss.n_quizzes_completed} submitted this session"),
        stat_card("Tutor questions", ss.n_tutor, "tutor", "this session"),
        stat_card("Resources curated", n_res if ss.learning_resources else 0, "resources", "in your current list"),
        stat_card("Roadmap progress", f"{done}/{n_phases}" if n_phases else "—", "roadmap", "phases you marked complete" if n_phases else "no roadmap phases yet"),
    ]
    for col, c in zip(cols, cards):
        col.markdown(c, unsafe_allow_html=True)
    if n_phases:
        st.write("")
        st.progress(done / n_phases, text=f"{done} of {n_phases} roadmap phases complete")
    if docs:
        st.caption(f"{docs} passages from your documents are indexed for the RAG Tutor.")

    # ---- Activity + next steps ----
    st.write("")
    a, b = st.columns(2, gap="large")
    with a:
        with st.container(key="card_dash_activity"):
            html('<div class="card-title">Recent activity</div>')
            log = ss.activity_log
            if log:
                items = "".join(f"<li><time>{esc(e['t'])}</time><span>{esc(e['text'])}</span></li>" for e in log[:6])
                html(f'<ul class="activity">{items}</ul>')
            else:
                st.caption("Nothing yet. Your actions in this session will appear here.")
    with b:
        with st.container(key="card_dash_next"):
            html('<div class="card-title">Recommended next steps</div>')
            if has_profile():
                for n, (ic, t, d, target) in enumerate(_next_steps()):
                    c1, c2 = st.columns([3, 1.2], vertical_alignment="center")
                    c1.markdown(
                        f'<div class="next" style="border:none"><span class="agent-ic">{icon(ic, 18)}</span><div><b>{esc(t)}</b><span>{esc(d)}</span></div></div>',
                        unsafe_allow_html=True,
                    )
                    with c2:
                        nav_button("Open", target, f"next_{n}", use_container_width=True)
            else:
                st.caption("Suggestions appear once your learning profile exists.")

    # ---- Quick access to all agents ----
    ornament("Your agents")
    for row in (AGENTS[:3], AGENTS[3:]):
        cols = st.columns(3)
        for col, (num, name, ic, tag, _p, target, cta) in zip(cols, row):
            with col:
                with st.container(key=f"card_agent_dash_{num}"):
                    html(
                        f"""<div class="quick"><span class="agent-ic">{icon(ic, 20)}</span>
                        <div><div class="agent-num" style="font-size:1.1rem">{num}</div>
                        <b style="font-family:var(--serif);font-size:1.3rem;color:var(--burgundy)">{esc(name)}</b></div></div>
                        <div class="agent-tag" style="font-size:1rem">{esc(tag)}</div>"""
                    )
                    nav_button(cta, target, f"dash_agent_{num}", use_container_width=True)
        st.write("")
