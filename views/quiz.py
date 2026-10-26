from collections import OrderedDict

import streamlit as st

from parsers import parse_quiz
from ui import bump, esc, html, log_activity, ornament, page_header, require_profile

LEVELS = ["beginner", "intermediate", "advanced"]


def _generate(difficulty: str, num: int, focus: str):
    ss = st.session_state
    try:
        result = ss.handler.generate_quiz(
            difficulty_level=difficulty,
            focus_areas=focus if focus else "general",
            num_questions=num,
        )
    except Exception as exc:
        st.error(f"The Quiz Generator could not finish: {exc}")
        return False
    ss.current_quiz = result["quiz"]  # original session key preserved
    ss.quiz_questions = parse_quiz(ss.current_quiz)
    ss.quiz_answers, ss.quiz_pos, ss.quiz_submitted = {}, 0, False
    bump("n_quizzes")
    log_activity(f"Generated a {difficulty} quiz ({num} questions)")
    return True


def _save(i: int):
    ss = st.session_state
    val = ss.get(f"qa_{i}")
    if val is None or val == "":
        ss.quiz_answers.pop(i, None)
    else:
        ss.quiz_answers[i] = val


def _move(delta: int):
    ss = st.session_state
    ss.quiz_pos = max(0, min(len(ss.quiz_questions) - 1, ss.quiz_pos + delta))


def _submit():
    ss = st.session_state
    ss.quiz_submitted = True
    bump("n_quizzes_completed")
    g, t = _score()
    log_activity(f"Submitted quiz: {g}/{t} on auto-graded questions" if t else "Submitted quiz")


def _score():
    ss = st.session_state
    graded = [(i, q) for i, q in enumerate(ss.quiz_questions) if q["type"] in ("mcq", "tf")]
    correct = sum(1 for i, q in graded if ss.quiz_answers.get(i) == q["answer"])
    return correct, len(graded)


def _reset_attempt():
    ss = st.session_state
    for i in range(len(ss.quiz_questions)):
        ss.pop(f"qa_{i}", None)
    ss.quiz_answers, ss.quiz_pos, ss.quiz_submitted = {}, 0, False


def _new_quiz():
    ss = st.session_state
    _reset_attempt()
    ss.quiz_questions = []
    ss.current_quiz = None


def _taking():
    ss = st.session_state
    qs, pos = ss.quiz_questions, ss.quiz_pos
    q = qs[pos]
    answered = len(ss.quiz_answers)
    st.progress((pos + 1) / len(qs), text=f"Question {pos + 1} of {len(qs)} · {answered} answered")
    dots = "".join(
        f'<span class="dot{" cur" if i == pos else " on" if i in ss.quiz_answers else ""}"></span>'
        for i in range(len(qs))
    )
    html(f'<div class="dots">{dots}</div>')

    html(
        f"""<div class="q-wrap"><div class="q-num">Question {pos + 1}</div>
        <div class="q-text">{esc(q["text"])}</div><div class="q-type">{esc(q["type_label"])}</div></div>"""
    )
    key = f"qa_{pos}"
    if q["type"] == "mcq":
        letters = list(q["options"].keys())
        cur = ss.quiz_answers.get(pos)
        st.radio(
            "Choose one", letters, index=letters.index(cur) if cur in letters else None,
            format_func=lambda L: f"{L})  {q['options'][L]}", key=key,
            on_change=_save, args=(pos,), label_visibility="collapsed",
        )
    elif q["type"] == "tf":
        cur = ss.quiz_answers.get(pos)
        st.radio(
            "Choose one", ["True", "False"], index=["True", "False"].index(cur) if cur else None,
            key=key, horizontal=True, on_change=_save, args=(pos,), label_visibility="collapsed",
        )
    else:
        st.text_area(
            "Your answer", value=ss.quiz_answers.get(pos, ""), key=key, height=140,
            placeholder="Write your answer. This question type is reviewed by you, not auto-graded.",
            on_change=_save, args=(pos,),
        )

    st.write("")
    b1, b2, _, b3 = st.columns([1, 1, 1.4, 1.5])
    b1.button("← Previous", disabled=pos == 0, on_click=_move, args=(-1,), use_container_width=True)
    if pos < len(qs) - 1:
        b2.button("Next →", on_click=_move, args=(1,), use_container_width=True)
    else:
        b2.empty()
    b3.button("Submit quiz", type="primary", on_click=_submit, use_container_width=True)
    if answered < len(qs):
        st.caption(f"{len(qs) - answered} question(s) still unanswered. You can submit at any time.")


def _results():
    ss = st.session_state
    qs = ss.quiz_questions
    correct, total = _score()
    ornament("Your results")
    left, right = st.columns([1, 2], gap="large")
    with left:
        if total:
            pct = round(100 * correct / total)
            html(f'<div class="score-ring" style="--pct:{pct}"><div><span>{correct}/{total}</span><small>{pct}% correct</small></div></div>')
        else:
            html('<div class="score-ring" style="--pct:0"><div><span>—</span><small>self-review</small></div></div>')
    with right:
        open_n = len(qs) - total
        unanswered = sum(1 for i in range(len(qs)) if i not in ss.quiz_answers)
        if total:
            pct = correct / total
            verdict = ("Excellent command of this material." if pct >= .85 else
                       "A solid foundation with some gaps to close." if pct >= .6 else
                       "This topic needs more attention before moving on.")
            st.markdown(f"**{verdict}**")
        st.write(
            f"{correct} correct and {total - correct} incorrect among {total} auto-graded question(s)."
            + (f" {open_n} written question(s) are for your own review." if open_n else "")
            + (f" {unanswered} question(s) were left unanswered." if unanswered else "")
        )

        concepts = OrderedDict()
        for i, q in enumerate(qs):
            if q["type"] in ("mcq", "tf") and q["concept"]:
                c = concepts.setdefault(q["concept"], [0, 0])
                c[1] += 1
                c[0] += ss.quiz_answers.get(i) == q["answer"]
        if concepts:
            html('<div class="card-title" style="margin-top:.8rem">By concept</div>')
            for name, (ok, n) in concepts.items():
                st.progress(ok / n, text=f"{name} · {ok}/{n}")
            weak = [n for n, (ok, t) in concepts.items() if ok < t]
            if weak:
                st.info("Suggested revision: " + "; ".join(weak) + ".")
            else:
                st.success("You answered every auto-graded concept correctly.")

    ornament("Review")
    for i, q in enumerate(qs):
        mine = ss.quiz_answers.get(i)
        if q["type"] in ("mcq", "tf"):
            ok = mine == q["answer"]
            cls, badge = ("ok", '<span class="badge ok">Correct</span>') if ok else ("bad", '<span class="badge err">Incorrect</span>' if mine else '<span class="badge warn">Unanswered</span>')
            show = lambda v: f"{v}) {q['options'].get(v, '')}" if q["type"] == "mcq" else v
            body = f"<b>Your answer:</b> {esc(show(mine)) if mine else '—'}<br><b>Correct answer:</b> {esc(show(q['answer']))}"
        else:
            cls, badge = "open", '<span class="badge">Self-review</span>'
            body = f"<b>Your answer:</b> {esc(mine) if mine else '—'}<br><b>Model answer:</b> {esc(q['correct_text'])}"
        extra = f"<br><i>{esc(q['explanation'])}</i>" if q["explanation"] else ""
        concept = f'<br><span class="chip" style="margin-top:.4rem">{esc(q["concept"])}</span>' if q["concept"] else ""
        html(
            f"""<div class="rev {cls}"><div style="display:flex;justify-content:space-between;gap:1rem">
            <b style="font-family:var(--serif);font-size:1.15rem;color:var(--burgundy)">{i + 1}. {esc(q['text'])}</b>{badge}</div>
            <div style="font-size:.92rem;margin-top:.3rem">{body}{extra}{concept}</div></div>"""
        )
    st.write("")
    a, b, _ = st.columns([1, 1.2, 2.5])
    a.button("Retake quiz", on_click=_reset_attempt, use_container_width=True)
    b.button("Generate a new quiz", on_click=_new_quiz, type="primary", use_container_width=True)


def render():
    ss = st.session_state
    page_header(
        "Agent 03 · Quiz Generator", "Test what you <em>know</em>",
        "Quizzes are generated for your topic and level, with explanations for every answer.",
    )
    if not require_profile("quiz_empty"):
        return

    if not ss.quiz_questions and not ss.get("current_quiz"):
        with st.container(key="card_quiz_setup"):
            html(f'<div class="card-title">Quiz on {esc(ss.topic)}</div>')
            c1, c2, c3 = st.columns(3)
            difficulty = c1.selectbox("Difficulty", LEVELS, index=1, format_func=str.title)
            num = c2.slider("Number of questions", 5, 20, 10)
            focus = c3.text_input("Focus areas (optional)", placeholder="e.g., deadlocks, memory management")
            go = st.button("Generate quiz", type="primary")
        if go:
            with st.container(key="card_quiz_status"):
                ok = _generate(difficulty, num, focus)
            if ok:
                st.rerun()
        return

    if not ss.quiz_questions:  # the output did not follow the expected format
        st.warning("The quiz could not be turned into an interactive format, so it is shown as written by the agent.")
        with st.container(key="card_quiz_raw"):
            st.markdown(ss.current_quiz)
        st.download_button("Download quiz", data=f"# Quiz: {ss.topic}\n\n{ss.current_quiz}",
                           file_name=f"quiz_{ss.topic.replace(' ', '_')}.md", mime="text/markdown")
        st.button("Generate a new quiz", on_click=_new_quiz, type="primary")
        return

    if ss.quiz_submitted:
        _results()
    else:
        _taking()
    with st.expander("Download this quiz with answers"):
        st.download_button("Download quiz", data=f"# Quiz: {ss.topic}\n\n{ss.current_quiz}",
                           file_name=f"quiz_{ss.topic.replace(' ', '_')}.md", mime="text/markdown")
