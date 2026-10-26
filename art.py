"""art.py - original line-art illustrations (education + AI only)."""

HERO_SVG = """
<svg class="hero-art" viewBox="0 0 520 560" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="An open book with a network of connected agents rising from its pages">
  <defs>
    <linearGradient id="arch" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0" stop-color="#5a2a30"/><stop offset="1" stop-color="#421D22"/>
    </linearGradient>
  </defs>
  <path d="M60 540V250C60 120 150 30 260 30s200 90 200 220v290z" fill="url(#arch)"/>
  <path d="M82 540V252C82 134 162 52 260 52s178 82 178 200v288" fill="none" stroke="#D6B99B" stroke-width="1" opacity=".7"/>
  <g stroke="#D6B99B" stroke-width="1.1" fill="none" opacity=".9">
    <path d="M260 150 190 120M260 150 330 118M260 150 260 92M190 120 140 170M330 118 384 168M190 120 230 200M330 118 292 200M140 170 180 250M384 168 346 250M230 200 292 200M180 250 230 200M346 250 292 200M180 250 346 250"/>
  </g>
  <g fill="#421D22" stroke="#D6B99B" stroke-width="1.3">
    <circle cx="260" cy="150" r="13"/><circle cx="190" cy="120" r="9"/><circle cx="330" cy="118" r="9"/>
    <circle cx="260" cy="92" r="7"/><circle cx="140" cy="170" r="7"/><circle cx="384" cy="168" r="7"/>
    <circle cx="230" cy="200" r="8"/><circle cx="292" cy="200" r="8"/><circle cx="180" cy="250" r="6"/><circle cx="346" cy="250" r="6"/>
  </g>
  <circle cx="260" cy="150" r="4" fill="#D6B99B"/>
  <g fill="none" stroke="#F4E6DA" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round">
    <path d="M260 330C222 300 160 292 104 304V470c56-12 118-4 156 26 38-30 100-38 156-26V304c-56-12-118-4-156 26z" fill="#F4E6DA" fill-opacity=".06"/>
    <path d="M260 330V496"/>
    <path d="M128 330c36-6 78-2 112 18M128 358c36-6 78-2 112 18M128 386c36-6 78-2 112 18" opacity=".6"/>
    <path d="M392 330c-36-6-78-2-112 18M392 358c-36-6-78-2-112 18M392 386c-36-6-78-2-112 18" opacity=".6"/>
  </g>
  <g stroke="#D6B99B" stroke-width="1" opacity=".85" fill="none" stroke-dasharray="2 5">
    <path d="M260 326V215"/><path d="M200 318 184 256"/><path d="M320 318 342 256"/>
  </g>
  <path d="M260 20l5 9-5 9-5-9z" fill="#D6B99B"/>
  <path d="M96 60l3 5-3 5-3-5zM428 96l3 5-3 5-3-5z" fill="#D6B99B" opacity=".7"/>
</svg>
"""

# Agent glyph names map to icons in ui._ICONS
AGENTS = [
    ("01", "Student Analyzer", "analyze",
     "Reads who you are as a learner.",
     "Analyzes student information, learning preferences, current knowledge and requirements.",
     "Student Analyzer", "Open the analyzer"),
    ("02", "Roadmap Creator", "roadmap",
     "Charts the path from here to mastery.",
     "Creates personalized study roadmaps, milestones and learning plans.",
     "Roadmap Creator", "View roadmap"),
    ("03", "Quiz Generator", "quiz",
     "Tests understanding, gently.",
     "Generates subject-specific quizzes with appropriate questions and difficulty levels.",
     "Quiz Generator", "Take a quiz"),
    ("04", "AI Tutor", "tutor",
     "A patient guide for hard ideas.",
     "Provides interactive explanations, answers questions and assists with difficult concepts.",
     "AI Tutor", "Ask the tutor"),
    ("05", "Resource Finder", "resources",
     "Curates what is worth your time.",
     "Finds and recommends useful learning resources.",
     "Resource Finder", "Browse resources"),
    ("06", "RAG Tutor", "rag",
     "Conversations with your own notes.",
     "Lets you interact with uploaded educational documents using retrieval-augmented generation.",
     "Document Intelligence", "Open documents"),
]
