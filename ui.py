"""
ui.py
Reusable presentation helpers for the redesigned interface. No agent logic here.
"""
from __future__ import annotations

import html as _html
import os
from datetime import datetime
from pathlib import Path

import streamlit as st

ASSETS = Path(__file__).parent / "assets"

# Navigation ---------------------------------------------------------------
PAGES = [
    ("Home", ":material/home:"),
    ("Dashboard", ":material/dashboard:"),
    ("Student Analyzer", ":material/person_search:"),
    ("Roadmap Creator", ":material/route:"),
    ("Quiz Generator", ":material/quiz:"),
    ("AI Tutor", ":material/school:"),
    ("Resource Finder", ":material/menu_book:"),
    ("Document Intelligence", ":material/description:"),
    ("About", ":material/info:"),
    ("Settings", ":material/tune:"),
]
PAGE_NAMES = [p for p, _ in PAGES]


def goto(page: str) -> None:
    """Callback-safe navigation."""
    st.session_state.page = page
    st.session_state.nav_radio = page


def nav_button(label: str, target: str, key: str, kind: str = "secondary", **kw) -> None:
    st.button(label, key=key, type=kind, on_click=goto, args=(target,), **kw)


# Text helpers -------------------------------------------------------------
def esc(text) -> str:
    return _html.escape(str(text if text is not None else ""))


def html(block: str) -> None:
    """Render raw HTML safely through Markdown (no blank/indented lines)."""
    flat = "\n".join(l.strip() for l in block.splitlines() if l.strip())
    st.markdown(flat, unsafe_allow_html=True)


def inject_css() -> None:
    css = (ASSETS / "style.css").read_text(encoding="utf-8")
    st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)


# Line-art icon set (stroke = currentColor) --------------------------------
_ICONS = {
    "analyze": '<circle cx="12" cy="8" r="3.2"/><path d="M5.5 20c.6-3.6 3.3-5.6 6.5-5.6"/><circle cx="17" cy="16.5" r="2.6"/><path d="m19 18.5 2 2"/>',
    "roadmap": '<circle cx="6" cy="18" r="2"/><circle cx="18" cy="6" r="2"/><path d="M8 18h6a3 3 0 0 0 0-6h-4a3 3 0 0 1 0-6h6"/>',
    "quiz": '<rect x="4.5" y="3.5" width="15" height="17" rx="1.5"/><path d="m8 9 1.4 1.4L12 7.8M8 15l1.4 1.4L12 13.8M14 9.5h3M14 15.5h3"/>',
    "tutor": '<path d="m2.5 9.5 9.5-4.5 9.5 4.5-9.5 4.5z"/><path d="M6.5 11.8v4.2c0 1.3 2.5 2.5 5.5 2.5s5.5-1.2 5.5-2.5v-4.2M21.5 9.5v5"/>',
    "resources": '<path d="M4 4.5h4v15H4zM9.5 4.5h4v15h-4z"/><path d="m15.2 5.6 3.8-.9 3 14.3-3.8.9z"/>',
    "rag": '<path d="M6 3.5h8l4 4v13H6z"/><path d="M14 3.5v4h4M9 12h6M9 15.5h4"/><path d="M19.5 2v3M18 3.5h3" />',
    "book": '<path d="M12 6.5C10 5 7 4.5 3.5 5v13c3.5-.5 6.5 0 8.5 1.5 2-1.5 5-2 8.5-1.5V5C17 4.5 14 5 12 6.5zM12 6.5v13"/>',
    "play": '<circle cx="12" cy="12" r="8.5"/><path d="m10.2 8.8 5 3.2-5 3.2z"/>',
    "code": '<path d="m8 8-4 4 4 4M16 8l4 4-4 4M13.5 6l-3 12"/>',
    "users": '<circle cx="9" cy="8.5" r="3"/><path d="M3 19c.5-3 3-4.8 6-4.8s5.5 1.8 6 4.8"/><path d="M16 5.8a3 3 0 0 1 0 5.4M18 14.6c1.6.6 2.7 2 3 4.4"/>',
    "file": '<path d="M6 3.5h8l4 4v13H6z"/><path d="M14 3.5v4h4M9 12h6M9 15.5h6"/>',
    "course": '<rect x="3" y="5" width="18" height="12" rx="1.5"/><path d="M8 20h8M12 17v3M9 9h6M9 12h4"/>',
    "link": '<path d="M10 14a4 4 0 0 0 5.7 0l3-3a4 4 0 0 0-5.7-5.7l-1 1M14 10a4 4 0 0 0-5.7 0l-3 3A4 4 0 0 0 11 18.7l1-1"/>',
    "check": '<path d="m5 12.5 4.5 4.5L19 7.5"/>',
    "spark": '<path d="M12 3v4M12 17v4M3 12h4M17 12h4M6 6l2.5 2.5M15.5 15.5 18 18M18 6l-2.5 2.5M8.5 15.5 6 18"/>',
    "clock": '<circle cx="12" cy="12" r="8.5"/><path d="M12 7.5V12l3 2"/>',
    "layers": '<path d="m12 3.5 9 4.5-9 4.5L3 8z"/><path d="m3 12.5 9 4.5 9-4.5M3 16.5l9 4.5 9-4.5"/>',
    "target": '<circle cx="12" cy="12" r="8.5"/><circle cx="12" cy="12" r="4.5"/><circle cx="12" cy="12" r=".8"/>',
    "chat": '<path d="M4 5.5h16v10H10l-4.5 4v-4H4z"/><path d="M8 9.5h8M8 12.5h5"/>',
    "upload": '<path d="M12 16V5M7.5 9.5 12 5l4.5 4.5M5 19.5h14"/>',
}


def icon(name: str, size: int = 22) -> str:
    body = _ICONS.get(name, _ICONS["book"])
    return (
        f'<svg class="ic" width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" '
        f'stroke="currentColor" stroke-width="1.35" stroke-linecap="round" '
        f'stroke-linejoin="round" aria-hidden="true">{body}</svg>'
    )


def resource_icon(category: str) -> str:
    c = (category or "").lower()
    for key, ic in [
        ("video", "play"), ("lecture", "play"), ("youtube", "play"),
        ("book", "book"), ("course", "course"), ("tutorial", "course"),
        ("practice", "code"), ("interactive", "code"), ("coding", "code"),
        ("forum", "users"), ("community", "users"), ("group", "users"),
        ("article", "file"), ("doc", "file"), ("blog", "file"),
    ]:
        if key in c:
            return icon(ic, 20)
    return icon("resources", 20)


# Editorial building blocks -------------------------------------------------
def ornament(label: str = "") -> None:
    mid = f'<span class="orn-label">{esc(label)}</span>' if label else '<span class="orn-diamond"></span>'
    html(f'<div class="ornament"><span class="orn-line"></span>{mid}<span class="orn-line"></span></div>')


def page_header(eyebrow: str, title: str, subtitle: str = "") -> None:
    sub = f'<p class="ph-sub">{esc(subtitle)}</p>' if subtitle else ""
    html(
        f"""<div class="page-header">
        <div class="eyebrow">{esc(eyebrow)}</div>
        <h1 class="ph-title">{title}</h1>
        {sub}
        <div class="ph-rule"><span></span><i></i><span></span></div>
        </div>"""
    )


def section_title(eyebrow: str, title: str, align: str = "left") -> None:
    html(
        f"""<div class="section-title {align}">
        <div class="eyebrow">{esc(eyebrow)}</div>
        <h2>{title}</h2></div>"""
    )


def stat_card(label: str, value, icon_name: str, note: str = "") -> str:
    n = f'<div class="stat-note">{esc(note)}</div>' if note else ""
    return (
        f'<div class="stat-card"><div class="stat-ic">{icon(icon_name, 20)}</div>'
        f'<div class="stat-val">{esc(value)}</div><div class="stat-label">{esc(label)}</div>{n}</div>'
    )


def chips(items) -> str:
    return "".join(f'<span class="chip">{esc(i)}</span>' for i in items if i)


def empty_state(title: str, text: str, cta_label: str, target: str, key: str) -> None:
    html(
        f"""<div class="empty-state">
        <div class="empty-ic">{icon("book", 34)}</div>
        <h3>{esc(title)}</h3><p>{esc(text)}</p></div>"""
    )
    _, mid, _ = st.columns([1, 1, 1])
    with mid:
        nav_button(cta_label, target, key, kind="primary", use_container_width=True)


def has_profile() -> bool:
    return bool(st.session_state.get("handler") and st.session_state.get("student_analysis"))


def require_profile(key: str) -> bool:
    """Show a friendly empty state and return False when no learning profile exists yet."""
    if has_profile():
        return True
    empty_state(
        "Your learning profile comes first",
        "Every agent adapts to who you are. Tell the Student Analyzer about your topic, level and goals "
        "and the rest of the workspace will open up.",
        "Begin with the Student Analyzer",
        "Student Analyzer",
        key,
    )
    return False


# Activity log (real events only) -------------------------------------------
def log_activity(text: str) -> None:
    log = st.session_state.setdefault("activity_log", [])
    log.insert(0, {"t": datetime.now().strftime("%H:%M"), "text": text})
    del log[12:]


def bump(counter: str, by: int = 1) -> None:
    st.session_state[counter] = st.session_state.get(counter, 0) + by


def api_key_status() -> dict:
    return {
        "groq": bool(os.getenv("GROQ_API_KEY")) and "your_" not in os.getenv("GROQ_API_KEY", ""),
        "openai": bool(os.getenv("OPENAI_API_KEY")) and "your_" not in os.getenv("OPENAI_API_KEY", ""),
    }
