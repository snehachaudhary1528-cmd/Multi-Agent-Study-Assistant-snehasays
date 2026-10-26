"""
End-to-end UI test using Streamlit's AppTest.
The REAL handler, prompts, config and parsers run; only the network edges are faked:
  - study_agents.Agent  -> returns canned, realistically formatted agent output
  - agent_handler.RAGHelper -> in-memory stand-in for OpenAI embeddings + ChromaDB
Run:  python -m pytest tests -q      (or)  python tests/test_app_flow.py
"""
import os, sys
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
os.environ.setdefault("GROQ_API_KEY", "test-key"); os.environ.setdefault("OPENAI_API_KEY", "test-key")

from types import SimpleNamespace
import study_agents, agent_handler
from streamlit.testing.v1 import AppTest

ANALYSIS = "## Current Level Assessment\nBeginner.\n## Knowledge Gaps Identified\nProcesses.\n## Prerequisites Needed\nC basics.\n## Recommended Learning Approach\nVisual."
ROADMAP = """## Roadmap Overview
10 weeks.
### Phase 1: Foundations (Weeks 1-3)
- Objectives
### Phase 2: Core Concepts (Weeks 4-6)
- More
### Phase 3: Practice
- Projects
## Key Checkpoints
- Quiz after phase 2"""
RESOURCES = """**Online Courses**
1. CS50 - Harvard
   - Link/Location: https://cs50.harvard.edu
   - Description: Intro course
   - Cost: Free
**Books**
1. Operating System Concepts
   - Link/Location: Library
   - Description: The dinosaur book
   - Cost: Paid"""
QUIZ = """Question 1: What is a deadlock?
Type: Multiple Choice
Options:
A) A crash
B) Circular wait
C) Fast
D) Scheduler

Correct Answer: B) Circular wait

Explanation: Circular wait.

Key Concept: Deadlocks

Question 2: Paging removes external fragmentation.
Type: True/False
Correct Answer: True
Explanation: Yes.
Key Concept: Paging

Question 3: Explain thrashing.
Type: Short Answer
Correct Answer: Excess paging.
Explanation: Too much swapping.
Key Concept: Virtual memory"""

class FakeAgent:
    def __init__(self, **kw): pass
    def run(self, prompt, stream=False):
        p = prompt
        if "comprehensive student" in p or "Analyze the student" in p: c = ANALYSIS
        elif "detailed, personalized learning roadmap" in p: c = ROADMAP
        elif "Find and recommend" in p: c = RESOURCES
        elif "Generate a comprehensive quiz" in p: c = QUIZ
        elif "Answer the student's question using" in p: c = "**Direct Answer:** from your docs"
        else: c = "Here is a clear explanation with `code`."
        return SimpleNamespace(content=c)

class FakeRAG:
    def __init__(self, **kw): self.n = 0
    def load_pdf(self, p): self.n += 3; return True
    def load_text(self, p): self.n += 2; return True
    def query(self, q, k=4): return ["chunk one", "chunk two"] if self.n else []
    def get_document_count(self): return self.n
    def clear_database(self): self.n = 0; return True

study_agents.Agent = FakeAgent
agent_handler.RAGHelper = FakeRAG

def new_app():
    at = AppTest.from_file(os.path.join(ROOT, "app.py"), default_timeout=60)
    at.run(); return at

def click(at, label_sub):
    b = [b for b in at.button if label_sub.lower() in b.label.lower()]
    assert b, f"button containing {label_sub!r} not found; have {[x.label for x in at.button]}"
    b[0].click(); at.run(); return at

def test_full_flow():
    at = new_app(); assert not at.exception
    assert at.session_state.page == "Home"
    # Landing page -> Student Analyzer
    click(at, "Start Learning")
    assert at.session_state.page == "Student Analyzer", at.session_state.page
    # Buttons on empty pages show friendly empty states, no errors
    for page in ["Dashboard", "Roadmap Creator", "Quiz Generator", "AI Tutor", "Resource Finder", "Document Intelligence"]:
        at.session_state.page = page; at.run(); assert not at.exception, (page, at.exception)
    at.session_state.page = "Student Analyzer"; at.run()
    # Fill the profile and run the real pipeline
    [t for t in at.text_input if t.label == "Specific topic"][0].set_value("Operating Systems")
    [t for t in at.text_area if "achieve" in t.label][0].set_value("Pass AKTU exams")
    at.run(); click(at, "Analyze & build")
    assert not at.exception, at.exception
    ss = at.session_state
    assert ss.step == 4 and ss.student_analysis == ANALYSIS and ss.learning_roadmap == ROADMAP and ss.learning_resources == RESOURCES
    assert ss.topic == "Operating Systems" and ss.handler is not None
    # Every page renders with a real profile
    for page in ["Dashboard", "Student Analyzer", "Roadmap Creator", "Resource Finder", "Quiz Generator", "AI Tutor", "Document Intelligence", "About", "Settings", "Home"]:
        ss.page = page; at.run(); assert not at.exception, (page, [e.value for e in at.exception])
    # Roadmap: tick a phase
    ss.page = "Roadmap Creator"; at.run()
    cbs = [c for c in at.checkbox if "phase complete" in c.label]; assert len(cbs) == 3
    cbs[0].check(); at.run(); assert at.session_state.phase_done[0] is True
    # Quiz: generate, answer, submit
    ss.page = "Quiz Generator"; at.run(); click(at, "Generate quiz")
    assert len(at.session_state.quiz_questions) == 3, at.session_state.quiz_questions
    q=at.radio(key="qa_0"); q.set_value(q.options[1]); at.run()   # Q1 option B
    assert at.session_state.quiz_answers.get(0) == "B", at.session_state.quiz_answers
    click(at, "Next"); at.radio(key="qa_1").set_value("True"); at.run()
    click(at, "Next"); [t for t in at.text_area if t.label == "Your answer"][0].set_value("swapping"); at.run()
    click(at, "Submit quiz")
    assert at.session_state.quiz_submitted and not at.exception
    assert any("2/2" in str(m.value) for m in at.markdown), "score ring should show 2/2"
    # Tutor chat
    ss.page = "AI Tutor"; at.run()
    at.chat_input[0].set_value("Explain paging").run()
    assert not at.exception and len(at.session_state.tutor_messages) == 2
    assert at.session_state.n_tutor == 1
    # RAG: seed documents through the real handler path, then ask
    ss.handler.add_document_to_rag("x.pdf", "pdf"); ss.page = "Document Intelligence"; at.run()
    [t for t in at.text_area if "know" in t.label][0].set_value("What is unit 2?"); at.run()
    click(at, "Ask documents"); assert not at.exception and len(at.session_state.rag_history) == 1
    # Dashboard reflects only real counters
    ss.page = "Dashboard"; at.run(); assert not at.exception
    # Reset
    click(at, "Start a new learning plan")
    assert at.session_state.handler is None and at.session_state.page == "Student Analyzer"

def _login_and_build(at):
    click(at, "Start Learning")
    [t for t in at.text_input if t.label == "Specific topic"][0].set_value("Networks")
    [t for t in at.text_area if "achieve" in t.label][0].set_value("Learn"); at.run()
    return click(at, "Analyze & build")

def test_unstructured_output_falls_back_to_markdown():
    """If the model ignores the requested format the UI must still show the text, never crash."""
    orig = FakeAgent.run
    FakeAgent.run = lambda self, prompt, stream=False: SimpleNamespace(content="Just some plain prose with no headings.")
    try:
        at = _login_and_build(new_app()); assert not at.exception, at.exception
        for page in ["Roadmap Creator", "Resource Finder", "Quiz Generator"]:
            at.session_state.page = page; at.run(); assert not at.exception, (page, at.exception)
        click(at, "Generate quiz"); assert not at.exception
        assert at.session_state.quiz_questions == [] and at.session_state.current_quiz
        at.session_state.page = "Quiz Generator"; at.run(); assert not at.exception
    finally:
        FakeAgent.run = orig

def test_agent_failure_is_reported_not_raised():
    orig = FakeAgent.run
    def boom(self, prompt, stream=False): raise RuntimeError("401 invalid api key")
    FakeAgent.run = boom
    try:
        at = _login_and_build(new_app())
        assert not at.exception, at.exception
        assert any("could not finish" in e.value for e in at.error), [e.value for e in at.error]
        assert at.session_state.step != 4
    finally:
        FakeAgent.run = orig

if __name__ == "__main__":
    test_full_flow(); test_unstructured_output_falls_back_to_markdown(); test_agent_failure_is_reported_not_raised(); print("ALL FLOW TESTS PASSED")
