import streamlit as st

from ui import bump, esc, html, icon, log_activity, page_header, require_profile

TUTOR_AVATAR = ":material/auto_stories:"
USER_AVATAR = ":material/person:"


def _clear():
    st.session_state.tutor_messages = []
    st.session_state.tutor_response = None  # original session key preserved


def render():
    ss = st.session_state
    page_header(
        "Agent 04 · AI Tutor", "Ask, and be <em>understood</em>",
        "Clear, step-by-step explanations adapted to your level and learning style.",
    )
    if not require_profile("tutor_empty"):
        return

    html(
        f"""<div class="tutor-head"><span class="agent-ic">{icon("tutor", 24)}</span>
        <div><b>Your AI Tutor</b><span>Teaching {esc(ss.topic)} at {esc(str(ss.knowledge_level))} level</span></div></div>"""
    )

    top_a, top_b = st.columns([3, 1], vertical_alignment="bottom")
    with top_a:
        context = st.text_input(
            "Additional context (optional)", key="tutor_context",
            placeholder="e.g., Preparing for AKTU end-sem exam question on OS memory management…",
        )
    with top_b:
        st.button("Clear conversation", on_click=_clear, disabled=not ss.tutor_messages, use_container_width=True)

    if not ss.tutor_messages:
        with st.container(key="card_tutor_hint"):
            html(
                '<div class="card-title">Where would you like to begin?</div>'
                '<p style="color:var(--muted);margin:0">Try: “Can you explain virtual memory and paging with an example?” '
                "Each question is answered on its own, so include the details the tutor needs.</p>"
            )

    for m in ss.tutor_messages:
        with st.chat_message(m["role"], avatar=TUTOR_AVATAR if m["role"] == "assistant" else USER_AVATAR):
            st.markdown(m["content"])

    question = st.chat_input("Ask your tutor anything about your topic…")
    if question:
        ss.tutor_messages.append({"role": "user", "content": question})
        with st.chat_message("user", avatar=USER_AVATAR):
            st.markdown(question)
        with st.chat_message("assistant", avatar=TUTOR_AVATAR):
            holder = st.empty()
            holder.markdown('<span class="typing"><i></i><i></i><i></i></span>', unsafe_allow_html=True)
            try:
                answer = ss.handler.get_tutoring(question, context)
            except Exception as exc:
                answer = None
                holder.error(f"The tutor could not answer: {exc}")
            if answer:
                holder.markdown(answer)
                ss.tutor_messages.append({"role": "assistant", "content": answer})
                ss.tutor_response = answer  # original session key preserved
                bump("n_tutor")
                log_activity("Asked the AI Tutor a question")
            else:
                ss.tutor_messages.pop()  # drop the unanswered question so it can be retried
