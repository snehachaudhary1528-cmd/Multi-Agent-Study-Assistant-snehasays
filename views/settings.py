import streamlit as st

from state import reset_plan
from ui import api_key_status, html, page_header

GROQ_MODELS = ["llama-3.3-70b-versatile", "llama-3.1-70b-versatile", "mixtral-8x7b-32768"]
OPENAI_MODELS = ["gpt-4o", "gpt-4-turbo", "gpt-4o-mini", "gpt-3.5-turbo"]


def render():
    ss = st.session_state
    page_header("Settings", "Configure your <em>agents</em>", "Choose the AI provider and model that power every agent.")

    with st.container(key="card_settings_model"):
        html('<div class="card-title">AI provider and model</div>')
        providers = ["groq", "openai"]
        provider = st.selectbox(
            "AI provider", providers, index=providers.index(ss.provider),
            help="Groq is free and fast. OpenAI requires a paid API key.",
        )
        models = GROQ_MODELS if provider == "groq" else OPENAI_MODELS
        cur = ss.selected_model if ss.selected_model in models else models[0]
        model = st.selectbox("Model", models, index=models.index(cur))
        ss.provider, ss.selected_model = provider, model
        if ss.handler and (ss.handler.provider != provider or ss.handler.model_name != model):
            st.warning(
                "Your current plan was created with "
                f"{ss.handler.provider} / {ss.handler.model_name}. The new choice applies "
                "to the next plan you create."
            )

    st.write("")
    with st.container(key="card_settings_keys"):
        html('<div class="card-title">API keys</div>')
        status = api_key_status()
        for name, label in (("groq", "Groq (GROQ_API_KEY)"), ("openai", "OpenAI (OPENAI_API_KEY)")):
            ok = status[name]
            st.markdown(
                f'{label} &nbsp; <span class="badge {"ok" if ok else "warn"}">{"Found" if ok else "Not set"}</span>',
                unsafe_allow_html=True,
            )
        st.caption(
            "Keys are read from your environment or .env file and are never displayed. "
            "Note: document search (RAG) creates embeddings with OpenAI, so it needs OPENAI_API_KEY even when Groq is the chat provider."
        )

    st.write("")
    with st.container(key="card_settings_reset"):
        html('<div class="card-title">Start over</div>')
        st.caption("Clears your profile, plan, quiz, chat and session activity. Indexed documents stay in the vector database until cleared on the Documents page.")
        st.button("Start a new learning plan", on_click=reset_plan)
