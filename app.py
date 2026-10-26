"""
Multi-Agent Study Assistant - StudyMate AI
Department of Computer Science & Engineering | IIMT Engineering College, Meerut

app.py is the application shell: page config, design system, navigation and routing.
All agent logic lives, unchanged, in agent_handler.py / study_agents.py / rag_helper.py / prompts.yaml.
Each screen is a module in views/.
"""
import streamlit as st
from dotenv import load_dotenv

load_dotenv()

st.set_page_config(
    page_title="StudyMate AI · Multi-Agent Study Assistant",
    layout="wide",
    page_icon="📖",
    initial_sidebar_state="expanded",
)

from state import init_state  # noqa: E402
from ui import PAGES, PAGE_NAMES, esc, html, icon, inject_css  # noqa: E402
from views import (about, analyzer, dashboard, home, quiz, rag,  # noqa: E402
                   resources, roadmap, settings, tutor)

ROUTES = {
    "Home": home.render,
    "Dashboard": dashboard.render,
    "Student Analyzer": analyzer.render,
    "Roadmap Creator": roadmap.render,
    "Quiz Generator": quiz.render,
    "AI Tutor": tutor.render,
    "Resource Finder": resources.render,
    "Document Intelligence": rag.render,
    "About": about.render,
    "Settings": settings.render,
}

init_state()
inject_css()


def _sync_nav():
    st.session_state.page = st.session_state.nav_radio


def sidebar():
    ss = st.session_state
    with st.sidebar:
        html(
            f"""<div class="side-brand"><div class="brand"><div class="brand-mark">{icon("book", 16)}</div>
            <div class="brand-name">StudyMate AI<small>Study Assistant</small></div></div></div>
            <div class="side-label">Navigate</div>"""
        )
        labels = dict(PAGES)
        ss.nav_radio = ss.page  # keep the radio in step with programmatic navigation
        st.radio(
            "Navigation", PAGE_NAMES, key="nav_radio", on_change=_sync_nav,
            format_func=lambda p: f"{labels[p]} {p}", label_visibility="collapsed",
        )
        studying = f"<br><span>Studying: {esc(ss.topic)}</span>" if ss.get("topic") else ""
        html(
            f"""<div class="side-foot"><b>Sneha Chaudhary</b>
            <span>B.Tech CSE · IIMT Engineering College, Meerut</span>{studying}</div>"""
        )


if st.session_state.page == "Home":
    # The landing page uses its own horizontal navigation instead of the sidebar.
    st.markdown(
        "<style>[data-testid='stSidebar'],[data-testid='stSidebarCollapsedControl'],"
        "[data-testid='stExpandSidebarButton'],[data-testid='stSidebarCollapseButton'],"
        "[data-testid='collapsedControl']{display:none!important}</style>",
        unsafe_allow_html=True,
    )
sidebar()
ROUTES[st.session_state.page]()
