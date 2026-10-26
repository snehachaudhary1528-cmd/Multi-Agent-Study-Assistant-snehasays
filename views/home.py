import streamlit as st

from art import AGENTS, HERO_SVG
from ui import goto, html, icon, nav_button, ornament, section_title, esc

BRAND = f"""<div class="brand"><div class="brand-mark">{icon("book", 16)}</div>
<div class="brand-name">StudyMate AI<small>Multi-Agent Study Assistant</small></div></div>"""


def _top_nav():
    with st.container(key="topnav"):
        c = st.columns([2.6, .9, 1.3, 1.5, .9, 1, 1.35], vertical_alignment="center")
        c[0].markdown(BRAND, unsafe_allow_html=True)
        c[1].markdown('<a class="navlink" href="#top">Home</a>', unsafe_allow_html=True)
        c[2].markdown('<a class="navlink" href="#agents">Explore Agents</a>', unsafe_allow_html=True)
        c[3].markdown('<a class="navlink" href="#features">Learning Features</a>', unsafe_allow_html=True)
        with c[4]:
            nav_button("About", "About", "tn_about")
        with c[5]:
            nav_button("Settings", "Settings", "tn_settings")
        with c[6]:
            nav_button("Start Learning", _entry_page(), "tn_start", kind="primary", use_container_width=True)


def _entry_page() -> str:
    return "Dashboard" if st.session_state.get("student_analysis") else "Student Analyzer"


def render():
    html('<div id="top"></div>')
    _top_nav()

    # ---- Hero ----
    html(
        f"""<section class="hero"><div>
        <div class="eyebrow">Your personal AI learning companion</div>
        <h1 class="hero-title">Learning,<em>reimagined.</em></h1>
        <p class="hero-sub">Where personalized education meets the power of intelligent multi-agent systems.
        Learn at your own pace, discover your strengths and build a smarter learning journey.</p>
        </div><div>{HERO_SVG}</div></section>"""
    )
    b1, b2, _ = st.columns([1.1, 1.3, 3])
    with b1:
        nav_button("Start Learning", _entry_page(), "hero_start", kind="primary", use_container_width=True)
    with b2:
        st.markdown('<a class="navlink" href="#agents" style="border:1px solid var(--burgundy);border-radius:3px;padding:.5rem 1rem">Explore AI Agents</a>', unsafe_allow_html=True)
    html('<div class="hero-meta"><span>Six specialised agents</span><span>Retrieval-augmented</span><span>Built for students</span></div>')
    html('<p class="tagline">Where intelligence meets the art of learning.</p>')
    ornament()

    # ---- Introduction ----
    html(
        """<div class="intro"><div><div class="eyebrow">The platform</div>
        <h2>A study companion that <em style="color:var(--rose)">knows you</em> before it teaches you.</h2></div>
        <p class="dropcap">An intelligent learning companion designed to make education more personalized,
        interactive and meaningful through the power of multi-agent artificial intelligence. Instead of one
        general-purpose chatbot, six specialised agents each take responsibility for a single part of your
        learning: understanding you, planning your path, testing your knowledge, explaining difficult ideas,
        finding materials and reading your own documents.</p></div>"""
    )

    # ---- Six agents ----
    html('<div id="agents"></div>')
    section_title("Explore the agents", "Six minds, <em>one</em> classroom")
    for row in (AGENTS[:3], AGENTS[3:]):
        cols = st.columns(3)
        for col, (num, name, ic, tag, purpose, target, cta) in zip(cols, row):
            with col:
                with st.container(key=f"card_agent_{num}"):
                    html(
                        f"""<div class="agent-top"><span class="agent-num">{num}</span>
                        <span class="agent-ic">{icon(ic, 22)}</span></div>
                        <h3 style="font-size:1.55rem!important;margin:0!important">{esc(name)}</h3>
                        <div class="agent-tag">{esc(tag)}</div>
                        <p style="font-size:.9rem;color:var(--muted);margin:0 0 .8rem">{esc(purpose)}</p>"""
                    )
                    nav_button(cta, target, f"agent_cta_{num}", use_container_width=True)
        st.write("")

    # ---- How it works ----
    html(
        """<section class="band"><div class="section-title"><div class="eyebrow">How it works</div>
        <h2>From a single question to a <em style="color:var(--gold)">complete plan</em></h2></div>
        <div class="steps">
        <div class="step"><div class="step-n">i</div><h4>Understand</h4><p>The Student Analyzer reads your topic, level, goal, time and learning style.</p></div>
        <div class="step"><div class="step-n">ii</div><h4>Plan</h4><p>The Roadmap Creator turns that analysis into phases, milestones and a schedule.</p></div>
        <div class="step"><div class="step-n">iii</div><h4>Gather</h4><p>The Resource Finder searches the web for materials that match how you learn.</p></div>
        <div class="step"><div class="step-n">iv</div><h4>Practise</h4><p>Quizzes, the AI Tutor and the document-grounded RAG Tutor keep you moving.</p></div>
        </div></section>"""
    )

    # ---- Learning features / benefits ----
    html('<div id="features"></div>')
    section_title("Learning features", "Designed around <em>how you learn</em>")
    feats = [
        ("target", "Personalised from the first step", "Every plan starts from your own level, goal, available time and preferred learning style."),
        ("layers", "Structured, phase-by-phase paths", "Roadmaps break a large goal into milestones you can tick off as you go."),
        ("quiz", "Practice that explains itself", "Generated quizzes include answers, explanations and the key concept behind each question."),
        ("rag", "Grounded in your own notes", "Upload PDFs or text files and ask questions answered from their content."),
    ]
    cols = st.columns(2)
    for i, (ic, t, d) in enumerate(feats):
        with cols[i % 2]:
            html(f'<div class="feature" style="margin-bottom:1.6rem"><span class="agent-ic">{icon(ic, 20)}</span><div><h4>{t}</h4><p>{d}</p></div></div>')

    # ---- Dashboard preview ----
    section_title("A glimpse inside", "Your <em>learning space</em>")
    html(
        """<div class="preview"><div class="pv-bar"><i></i><i></i><i></i></div>
        <div class="pv-body"><div class="pv-side"><b></b><b></b><b></b><b></b><b></b><b></b></div>
        <div class="pv-main"><h5>Welcome to your learning space.</h5>
        <div class="pv-row"><div></div><div></div><div></div><div></div></div>
        <div class="pv-bars"><span></span><span></span><span></span></div></div></div></div>
        <p style="text-align:center;color:var(--muted);font-size:.8rem;margin-top:.6rem;font-style:italic">
        An illustrative layout. Your dashboard shows only your own real activity.</p>"""
    )

    # ---- Final CTA ----
    html(
        """<section class="cta-band"><div class="eyebrow">Begin</div>
        <h2>Every great achievement begins with a <em>curious mind.</em></h2>
        <p>Tell the Student Analyzer what you want to learn and let the agents do the planning.</p></section>"""
    )
    _, mid, _ = st.columns([1.4, 1, 1.4])
    with mid:
        nav_button("Start Learning", _entry_page(), "cta_start", kind="primary", use_container_width=True)

    # ---- Footer ----
    html(
        f"""<footer class="footer"><div class="footer-grid">
        <div>{BRAND}<p style="margin-top:1rem;max-width:340px">Where intelligence meets the art of learning.</p></div>
        <div><h5>Explore</h5><ul><li>Student Analyzer</li><li>Roadmap Creator</li><li>Quiz Generator</li><li>AI Tutor</li></ul></div>
        <div><h5>Project</h5><ul><li>B.Tech Computer Science and Engineering</li><li>IIMT Engineering College, Meerut</li></ul></div></div>
        <div class="footer-credit"><span>© Multi-Agent Study Assistant</span><em>Designed &amp; Developed by Sneha Chaudhary.</em></div></footer>"""
    )
