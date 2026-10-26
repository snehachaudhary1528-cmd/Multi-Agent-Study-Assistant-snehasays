import streamlit as st

from parsers import parse_resources
from ui import esc, html, icon, log_activity, page_header, require_profile, resource_icon


def _find_new():
    """Same behaviour as the original 'Find New Resources' button."""
    ss = st.session_state
    ss.learning_resources = None
    try:
        ss.handler.find_resources()
        log_activity("Found a new set of resources")
    except Exception as exc:
        st.error(f"The Resource Finder could not finish: {exc}")


def _card(r: dict) -> str:
    cost = r["cost"]
    cost_cls = "ok" if cost.lower().startswith("free") else "warn" if cost else ""
    cost_badge = f'<span class="badge {cost_cls}">{esc(cost[:24])}</span>' if cost else ""
    desc = r["description"] or r["why"]
    extra = f'<p style="font-size:.8rem"><b>Best for:</b> {esc(r["best_for"])}</p>' if r["best_for"] else ""
    if r["url"]:
        link = f'<a href="{esc(r["url"])}" target="_blank" rel="noopener noreferrer">Open resource ↗</a>'
    else:
        link = f'<span style="color:var(--muted)">{esc(r["location"][:40])}</span>' if r["location"] else ""
    return (
        f'<div class="card res-card"><div class="res-top">{resource_icon(r["category"])}'
        f'<span class="badge">{esc(r["category"][:28])}</span></div>'
        f'<h4>{esc(r["name"])}</h4><p>{esc(desc)}</p>{extra}'
        f'<div class="res-foot">{cost_badge}{link}</div></div>'
    )


def render():
    ss = st.session_state
    page_header(
        "Agent 05 · Resource Finder", "A library, <em>curated for you</em>",
        "Courses, books, videos and practice platforms matched to your topic, goal and learning style.",
    )
    if not require_profile("res_empty"):
        return
    if not ss.learning_resources:
        st.warning("No resources yet.")
        st.button("Find resources", type="primary", on_click=_find_new)
        return

    items = parse_resources(ss.learning_resources)
    c1, c2, c3 = st.columns([2.2, 1.5, 1.2], vertical_alignment="bottom")
    with c1:
        query = st.text_input("Search resources", placeholder="Search by name or description", key="res_query")
    categories = sorted({i["category"] for i in items})
    with c2:
        chosen = st.multiselect("Categories", categories, key="res_cats", placeholder="All categories") if items else []
    with c3:
        st.button("Find new resources", on_click=_find_new, use_container_width=True)

    if not items:  # unexpected format: show the agent's text untouched
        with st.container(key="card_res_raw"):
            st.markdown(ss.learning_resources)
    else:
        q = query.strip().lower()
        shown = [
            r for r in items
            if (not chosen or r["category"] in chosen)
            and (not q or q in (r["name"] + " " + r["description"] + " " + r["category"] + " " + r["why"]).lower())
        ]
        st.caption(f"Showing {len(shown)} of {len(items)} resources")
        if not shown:
            st.info("No resources match your search. Try fewer words or clear the category filter.")
        for row_start in range(0, len(shown), 3):
            cols = st.columns(3)
            for col, r in zip(cols, shown[row_start:row_start + 3]):
                col.markdown(_card(r), unsafe_allow_html=True)
            st.write("")

    with st.expander("Read the full list as written by the agent"):
        st.markdown(ss.learning_resources)
    st.download_button(
        "Download resources", data=f"# Learning Resources: {ss.topic}\n\n{ss.learning_resources}",
        file_name=f"resources_{ss.topic.replace(' ', '_')}.md", mime="text/markdown",
    )
