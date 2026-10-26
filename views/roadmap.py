import streamlit as st

from parsers import parse_roadmap
from ui import esc, html, log_activity, nav_button, ornament, page_header, require_profile


def _regenerate():
    """Same behaviour as the original 'Regenerate Roadmap' button."""
    ss = st.session_state
    ss.learning_roadmap = None
    ss.phase_done = {}
    try:
        ss.handler.create_roadmap(ss.student_analysis)
        log_activity("Roadmap regenerated")
    except Exception as exc:
        st.error(f"The Roadmap Creator could not finish: {exc}")


def _toggle(i: int):
    ss = st.session_state
    ss.phase_done[i] = bool(ss[f"phase_cb_{i}"])
    if ss.phase_done[i]:
        log_activity(f"Completed roadmap phase {i + 1}")


def render():
    ss = st.session_state
    page_header(
        "Agent 02 · Roadmap Creator", "Your path, <em>phase by phase</em>",
        "A personalised study plan built from your analysis. Tick phases off as you complete them.",
    )
    if not require_profile("rm_empty"):
        return

    # Plan parameters (read from the profile the analyzer collected)
    html(
        f"""<div class="rm-overview">
        <div class="rm-fact"><small>Subject</small><b>{esc(ss.topic)}</b></div>
        <div class="rm-fact"><small>Current level</small><b>{esc(str(ss.knowledge_level).title())}</b></div>
        <div class="rm-fact"><small>Time available</small><b>{esc(ss.time_available)}</b></div>
        <div class="rm-fact"><small>Learning goal</small><b style="font-size:1.05rem">{esc(ss.learning_goal)}</b></div></div>"""
    )
    c1, c2, c3, _ = st.columns([1.2, 1.2, 1.4, 2])
    with c1:
        if st.button("Regenerate roadmap", use_container_width=True):
            with st.container(key="card_rm_regen"):
                _regenerate()
            st.rerun()
    with c2:
        st.download_button(
            "Download roadmap",
            data=f"# Learning Roadmap: {ss.topic}\n\n{ss.learning_roadmap}",
            file_name=f"roadmap_{ss.topic.replace(' ', '_')}.md", mime="text/markdown",
            use_container_width=True,
        )
    with c3:
        nav_button("Edit profile", "Student Analyzer", "rm_edit", use_container_width=True)

    if not ss.learning_roadmap:
        st.warning("No roadmap yet. Use “Regenerate roadmap” to create one.")
        return

    parsed = parse_roadmap(ss.learning_roadmap)
    if not parsed:  # unexpected format: show the agent's text untouched
        with st.container(key="card_rm_raw"):
            st.markdown(ss.learning_roadmap)
    else:
        phases = parsed["phases"]
        done = sum(1 for i in range(len(phases)) if ss.phase_done.get(i))
        st.progress(done / len(phases), text=f"{done} of {len(phases)} phases complete")

        if parsed["overview"]:
            with st.expander("Roadmap overview", expanded=False):
                st.markdown(parsed["overview"])

        ornament("The journey")
        for i, ph in enumerate(phases):
            is_done = bool(ss.phase_done.get(i))
            with st.container(key=f"phase_{i}"):
                html(f'<div class="ph-marker{" done" if is_done else ""}">{i + 1}</div>')
                with st.container(key=f"card_phase_{i}"):
                    meta = f'<span class="badge">{esc(ph["duration"])}</span>' if ph["duration"] else ""
                    status = '<span class="badge ok">Complete</span>' if is_done else '<span class="badge">In plan</span>'
                    html(f'<div class="ph-head"><h4>{esc(ph["title"])}</h4><div class="ph-meta">{meta}{status}</div></div>')
                    with st.expander("Objectives, activities and checkpoints"):
                        st.markdown(ph["body"] or "_No further detail was provided for this phase._")
                    st.checkbox("Mark this phase complete", value=is_done, key=f"phase_cb_{i}",
                                on_change=_toggle, args=(i,))

        if parsed["extras"]:
            ornament("Schedule & checkpoints")
            cols = st.columns(2)
            for k, sec in enumerate(parsed["extras"]):
                with cols[k % 2]:
                    with st.container(key=f"card_rm_extra_{k}"):
                        html(f'<div class="card-title">{esc(sec["title"])}</div>')
                        st.markdown(sec["body"])

    with st.expander("View student analysis"):
        st.markdown(ss.student_analysis)
