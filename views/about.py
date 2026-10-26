import streamlit as st

from ui import esc, html, ornament, page_header, section_title

# Every entry below is imported or configured somewhere in this repository.
TECH = [
    ("Python", "Core language"),
    ("Streamlit", "Application interface"),
    ("Phidata agents", "Multi-agent framework"),
    ("Groq", "Llama / Mixtral inference"),
    ("OpenAI", "GPT models and embeddings"),
    ("LangChain", "Loaders, splitters, vector store"),
    ("ChromaDB", "Vector database for RAG"),
    ("DuckDuckGo Search", "Web search for resources"),
    ("PyYAML", "Prompt and persona configuration"),
    ("Docker", "Container deployment"),
]


def render():
    page_header("About", "Behind the <em>Intelligence</em>", "An academic major project in applied artificial intelligence.")

    left, right = st.columns([1.15, 1], gap="large")
    with left:
        with st.container(key="card_about_project"):
            html(
                """<div class="card-title">Multi-Agent Study Assistant</div>
                <p>A multi-agent learning platform. Specialised agents analyse the student, plan a roadmap,
                generate quizzes, tutor difficult concepts, find resources and answer questions from uploaded
                documents using retrieval-augmented generation (RAG).</p>
                <p>Each agent has its own persona and prompt, defined in <code>prompts.yaml</code>, and is coordinated
                by a single handler so that every step builds on the student's profile.</p>"""
            )
    with right:
        with st.container(key="card_about_credits"):
            html(
                """<div class="card-title">Project details</div><dl class="cred">
                <dt>Developer</dt><dd>Sneha Chaudhary</dd>
                <dt>Degree</dt><dd>B.Tech Computer Science and Engineering</dd>
                <dt>Institution</dt><dd>IIMT Engineering College, Meerut</dd>
                <dt>Affiliation</dt><dd>Dr. A.P.J. Abdul Kalam Technical University, Lucknow</dd>
                <dt>Project guide</dt><dd>Ms. Anjali Dhiman, Assistant Professor</dd>
                <dt>Coordinator</dt><dd>Dr. Rajeev Sharma</dd></dl>"""
            )

    section_title("Technology", "What it is <em>built with</em>")
    cells = "".join(f"<div><b>{esc(n)}</b><span>{esc(d)}</span></div>" for n, d in TECH)
    html(f'<div class="tech">{cells}</div>')

    ornament()
    html(
        """<div style="text-align:center"><div class="eyebrow">Where intelligence meets the art of learning</div>
        <p class="signature" style="margin:.6rem 0 0">Designed &amp; Developed by Sneha Chaudhary.</p></div>"""
    )
