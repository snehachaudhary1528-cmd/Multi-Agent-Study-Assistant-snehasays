import os
import tempfile

import streamlit as st

from ui import bump, esc, html, icon, log_activity, page_header, require_profile


def _size(n: int) -> str:
    return f"{n / 1024:.0f} KB" if n < 1024 * 1024 else f"{n / (1024 * 1024):.1f} MB"


def _ingest(uploaded_files):
    """
    Same ingestion as the original (temp file -> handler.add_document_to_rag),
    but each file is processed once instead of on every rerun.
    """
    ss = st.session_state
    for f in uploaded_files:
        fp = f"{f.name}:{f.size}"
        if fp in ss.rag_seen:
            continue
        suffix = os.path.splitext(f.name)[1] or ".txt"
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            tmp.write(f.getbuffer())
            temp_path = tmp.name
        file_type = "pdf" if f.name.lower().endswith(".pdf") else "text"
        try:
            with st.spinner(f"Reading {f.name}…"):
                ok = ss.handler.add_document_to_rag(temp_path, file_type)
        except Exception as exc:
            ok = False
            st.error(f"{f.name}: {exc}")
        finally:
            if os.path.exists(temp_path):
                os.remove(temp_path)
        ss.rag_seen.append(fp)
        ss.rag_docs.append({"name": f.name, "size": f.size, "status": "Indexed" if ok else "Failed"})
        if ok:
            ss.uploaded_files_count += 1
            log_activity(f"Added document: {f.name}")


def _clear():
    ss = st.session_state
    ss.handler.clear_documents()
    ss.uploaded_files_count = 0
    ss.rag_docs, ss.rag_seen, ss.rag_history = [], [], []
    ss.rag_answer = None  # original session key preserved
    ss.rag_uploader_n = ss.get("rag_uploader_n", 0) + 1  # resets the uploader widget
    log_activity("Cleared all documents")


def render():
    ss = st.session_state
    page_header(
        "Agent 06 · RAG Tutor", "Converse with your <em>own documents</em>",
        "Upload notes, papers or chapters. Answers are retrieved from your files, then explained by the tutor.",
    )
    if not require_profile("rag_empty"):
        return

    left, right = st.columns([1.5, 1], gap="large")
    with left:
        uploaded = st.file_uploader(
            "Drop study materials here", type=["pdf", "txt"], accept_multiple_files=True,
            key=f"rag_uploader_{ss.get('rag_uploader_n', 0)}",
            help="Supported formats: PDF and plain text (.txt)",
        )
        st.caption("Supported formats: PDF · TXT")
        if uploaded:
            _ingest(uploaded)
    with right:
        with st.container(key="card_rag_docs"):
            count = ss.handler.get_document_count()
            html(f'<div class="card-title">Your library</div>')
            st.metric("Indexed passages", count, help="Number of text chunks stored in the vector database.")
            if ss.rag_docs:
                rows = "".join(
                    f'<div class="doc-row"><span class="doc-ic">{icon("file", 18)}</span>'
                    f'<div><b>{esc(d["name"])}</b><small>{_size(d["size"])}</small></div>'
                    f'<span class="badge {"ok" if d["status"] == "Indexed" else "err"}">{d["status"]}</span></div>'
                    for d in ss.rag_docs
                )
                html(rows)
            else:
                st.caption("No documents added in this session yet.")
            if count > 0:
                st.button("Clear all documents", on_click=_clear, use_container_width=True)

    st.write("")
    if ss.handler.get_document_count() == 0:
        st.info("Upload a document above to start asking questions.")
        return

    with st.container(key="card_rag_ask"):
        html('<div class="card-title">Ask your documents</div>')
        question = st.text_area(
            "What would you like to know?", key="doc_question", height=100,
            placeholder="e.g., What are the key concepts in unit 2?",
        )
        ask = st.button("Ask documents", type="primary", disabled=not question.strip())
    if ask:
        with st.spinner("Searching your documents…"):
            try:
                answer = ss.handler.query_documents(question)
            except Exception as exc:
                answer = None
                st.error(f"The RAG Tutor could not answer: {exc}")
        if answer:
            ss.rag_answer = answer  # original session key preserved
            ss.rag_history.insert(0, {"q": question, "a": answer})
            bump("n_rag")
            log_activity("Asked a question about your documents")

    if ss.rag_history:
        latest, *older = ss.rag_history
        with st.container(key="card_rag_answer"):
            html(f'<div class="qa-q">{esc(latest["q"])}</div>')
            st.markdown(latest["a"])
        if older:
            with st.expander(f"Earlier questions ({len(older)})"):
                for h in older:
                    html(f'<div class="qa-q">{esc(h["q"])}</div>')
                    st.markdown(h["a"])
                    st.divider()
