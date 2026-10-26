"""
parsers.py
Turns the Markdown that the existing agents return into structured data that
the redesigned UI can render (timelines, quiz cards, resource cards).

Nothing here changes a prompt or an agent. Every parser is defensive: when the
model's output does not match the expected shape the function returns None / []
and the UI falls back to rendering the original Markdown untouched.
"""
from __future__ import annotations

import re
from typing import Dict, List, Optional

_URL_RE = re.compile(r"https?://[^\s)\]>\"']+")
_MD_LINK_RE = re.compile(r"\[([^\]]+)\]\((https?://[^)\s]+)\)")
_DURATION_RE = re.compile(
    r"(\d+\s*(?:[-–to]+\s*\d+)?\s*(?:weeks?|days?|hours?|hrs?|months?))", re.I
)


def strip_md(text: str) -> str:
    """Remove light Markdown emphasis so text can be shown in custom cards."""
    text = _MD_LINK_RE.sub(r"\1", text)
    return re.sub(r"[*_`#]+", "", text).strip(" \t:-")


# --------------------------------------------------------------------------
# Generic heading handling
# --------------------------------------------------------------------------
def _heading(line: str):
    """Return (level, text) when the line looks like a heading, else None."""
    m = re.match(r"^\s{0,3}(#{1,6})\s+(.*\S)\s*$", line)
    if m:
        return len(m.group(1)), strip_md(m.group(2))
    m = re.match(r"^\s*\*\*(.{2,120}?)\*\*:?\s*$", line)  # whole-line bold
    if m:
        return 7, strip_md(m.group(1))
    return None


def split_sections(md: str) -> Optional[List[Dict[str, str]]]:
    """Split Markdown into [{'title', 'body'}] on headings. None if < 2 sections."""
    if not md:
        return None
    lines = md.splitlines()
    heads = [(i, h) for i, l in enumerate(lines) if (h := _heading(l))]
    if len(heads) < 2:
        return None
    sections = []
    pre = "\n".join(lines[: heads[0][0]]).strip()
    if pre:
        sections.append({"title": "Overview", "body": pre})
    for k, (i, (_lvl, txt)) in enumerate(heads):
        end = heads[k + 1][0] if k + 1 < len(heads) else len(lines)
        body = "\n".join(lines[i + 1 : end]).strip()
        if body:
            sections.append({"title": txt, "body": body})
    return sections if len(sections) >= 2 else None


# --------------------------------------------------------------------------
# Roadmap
# --------------------------------------------------------------------------
_PHASE_RE = re.compile(r"^(?:\d+[.)]\s*)?(phase|module|stage|unit)\s*\d+", re.I)


def parse_roadmap(md: str) -> Optional[Dict]:
    """
    Returns {'overview': str, 'phases': [{'title','body','duration'}], 'extras': [...]}
    or None when fewer than two phases can be identified.
    """
    if not md:
        return None
    lines = md.splitlines()
    heads = [(i, h) for i, l in enumerate(lines) if (h := _heading(l))]
    phase_heads = [(i, lvl, txt) for i, (lvl, txt) in heads if _PHASE_RE.match(txt)]
    if len(phase_heads) < 2:
        return None

    phase_level = phase_heads[0][1]
    phases = []
    last_end = phase_heads[0][0]
    for n, (i, lvl, txt) in enumerate(phase_heads):
        end = len(lines)
        for j, (jl, _) in [(j, h) for j, h in heads if j > i]:
            is_next_phase = any(j == pi for pi, _, _ in phase_heads)
            if is_next_phase or jl < phase_level:
                end = j
                break
        body = "\n".join(lines[i + 1 : end]).strip()
        dur = _DURATION_RE.search(txt) or _DURATION_RE.search(body[:400])
        phases.append(
            {
                "title": re.sub(r"^\d+[.)]\s*", "", txt),
                "body": body,
                "duration": dur.group(1).strip() if dur else "",
            }
        )
        last_end = end

    overview = "\n".join(lines[: phase_heads[0][0]]).strip()
    extras: List[Dict[str, str]] = []
    tail = "\n".join(lines[last_end:]).strip()
    if tail:
        extras = split_sections(tail) or [{"title": "Additional guidance", "body": tail}]
    return {"overview": overview, "phases": phases, "extras": extras}


# --------------------------------------------------------------------------
# Quiz
# --------------------------------------------------------------------------
def parse_quiz(md: str) -> List[Dict]:
    """
    Parse the quiz format mandated by prompts.yaml:
        Question N: ... / Type: ... / Options: A) B) C) D) / Correct Answer: ...
        Explanation: ... / Key Concept: ...
    Returns a list of question dicts. Empty list when nothing usable is found.
    """
    if not md:
        return []
    text = re.sub(r"[*#]+", "", md)
    parts = re.split(r"(?im)^\s*Question\s*\[?(\d+)\]?\s*[:.)\-]\s*", text)
    questions: List[Dict] = []
    for k in range(1, len(parts) - 1, 2):
        body = parts[k + 1]

        def field(name: str, stop: str) -> str:
            m = re.search(
                rf"(?ims)^\s*{name}\s*:\s*(.+?)(?=^\s*(?:{stop})\s*:|\Z)", body
            )
            return m.group(1).strip() if m else ""

        qtype_raw = field("Type", "Options|Correct Answer|Explanation|Key Concept|[A-D]\\)")
        correct = field("Correct Answer", "Explanation|Key Concept")
        explanation = field("Explanation", "Key Concept|Question")
        concept = field("Key Concept", "Question")
        opts = re.findall(r"(?m)^\s*\(?([A-D])[\).]\s+(.+?)\s*$", body)
        options = {letter: strip_md_keep(t) for letter, t in opts}

        stem_end = re.search(
            r"(?im)^\s*(Type|Options|Correct Answer)\s*:|^\s*\(?[A-D][\).]\s", body
        )
        stem = body[: stem_end.start()] if stem_end else body
        stem = stem.strip()
        if not stem:
            continue

        qtype, answer = "open", None
        if len(options) >= 2:
            m = re.match(r"\(?([A-D])\b", correct.strip())
            if m and m.group(1) in options:
                qtype, answer = "mcq", m.group(1)
            else:  # try matching the answer text against option text
                for letter, t in options.items():
                    if correct and correct.strip().lower().startswith(t.lower()[:30]):
                        qtype, answer = "mcq", letter
                        break
        elif re.search(r"true\s*[/-]?\s*false", qtype_raw, re.I) or re.match(
            r"(?i)^(true|false)\b", correct.strip()
        ):
            m = re.match(r"(?i)^(true|false)\b", correct.strip())
            if m:
                qtype, answer = "tf", m.group(1).capitalize()
                options = {"True": "True", "False": "False"}

        questions.append(
            {
                "number": len(questions) + 1,
                "text": stem,
                "type": qtype,
                "type_label": strip_md(qtype_raw) or {"mcq": "Multiple Choice", "tf": "True / False"}.get(qtype, "Written answer"),
                "options": options if qtype in ("mcq", "tf") else {},
                "answer": answer,
                "correct_text": correct,
                "explanation": explanation,
                "concept": strip_md(concept),
            }
        )
    return questions


def strip_md_keep(text: str) -> str:
    return text.replace("**", "").strip()


# --------------------------------------------------------------------------
# Resources
# --------------------------------------------------------------------------
_FIELD_RE = re.compile(
    r"^\s*[-*•]?\s*\**\s*(Link/Location|Link|URL|Location|Description|Best For|Cost|Why Recommended)\s*\**\s*:\s*\**\s*(.*)$",
    re.I,
)
_ITEM_RE = re.compile(r"^\s*(?:#{1,6}\s*)?\**\s*(\d+)[.)]\s+(.+?)\s*$")


def parse_resources(md: str) -> List[Dict]:
    """Return a flat list of resource dicts, each tagged with its category."""
    if not md:
        return []
    items: List[Dict] = []
    category, cur = "Recommended", None
    for raw in md.splitlines():
        line = raw.rstrip()
        if not line.strip():
            continue
        fm = _FIELD_RE.match(line)
        if fm and cur is not None:
            key = fm.group(1).lower()
            val = fm.group(2).strip().strip("*").strip()
            if key in ("link/location", "link", "url", "location"):
                cur["location"] = strip_md(val)
                url = _MD_LINK_RE.search(val) or _URL_RE.search(val)
                if url:
                    cur["url"] = url.group(2) if _MD_LINK_RE.search(val) else url.group(0).rstrip(".,;")
            elif key == "description":
                cur["description"] = strip_md(val)
            elif key == "best for":
                cur["best_for"] = strip_md(val)
            elif key == "cost":
                cur["cost"] = strip_md(val)
            elif key == "why recommended":
                cur["why"] = strip_md(val)
            continue
        im = _ITEM_RE.match(line)
        if im:
            name_raw = im.group(2)
            cur = {
                "category": category,
                "name": strip_md(name_raw.split(" - ")[0]) or strip_md(name_raw),
                "location": "",
                "url": "",
                "description": "",
                "best_for": "",
                "cost": "",
                "why": "",
            }
            ml, ul = _MD_LINK_RE.search(name_raw), _URL_RE.search(name_raw)
            if ml:
                cur["url"] = ml.group(2)
            elif ul:
                cur["url"] = ul.group(0).rstrip(".,;")
            items.append(cur)
            continue
        h = _heading(line)
        br = re.match(r"^\s*\[([^\]]{3,60})\]\s*$", line)
        if h or br:
            category = strip_md(br.group(1) if br else h[1]) or category
            cur = None
            continue
        # Loose continuation text: attach to the description when empty
        if cur is not None and not cur["description"] and not line.lstrip().startswith(("-", "*")):
            cur["description"] = strip_md(line)
    return [i for i in items if i["name"]]
