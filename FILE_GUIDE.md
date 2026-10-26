# 📁 File Guide - Multi-Agent Study Assistant

## Quick Navigation

### 🚀 Start Here
- **README.md** - Main documentation
- **QUICKSTART.md** - 5-minute setup guide  
- **setup.sh** - Automated setup script

### 💻 Core Code
- **app.py** - Streamlit web interface
- **study_agents.py** - AI agent definitions
- **agent_handler.py** - Orchestration logic
- **rag_helper.py** - RAG functionality
- **config.py** - Configuration manager
- **prompts.yaml** - Agent prompts & config

### 📚 Documentation
- **ARCHITECTURE.md** - Technical details
- **PROJECT_SUMMARY.md** - Complete overview
- **FILE_GUIDE.md** - This file

### ⚙️ Configuration
- **pyproject.toml** - Dependencies (uv)
- **requirements.txt** - Dependencies (pip)
- **.env.example** - Environment template
- **.gitignore** - Git ignore rules

---

## 🎯 Reading Order by Goal

### Quick Start
1. QUICKSTART.md
2. Run setup.sh
3. Edit .env
4. Run app.py

### Understand Project
1. README.md
2. PROJECT_SUMMARY.md
3. ARCHITECTURE.md

### Customize
1. prompts.yaml (easiest)
2. study_agents.py
3. agent_handler.py

### Deploy
1. README.md
2. requirements.txt
3. setup.sh

## UI redesign (StudyMate AI)
- `app.py` – thin shell: page config, CSS, sidebar navigation, routing
- `views/` – one module per screen (home, dashboard, analyzer, roadmap, quiz, tutor, resources, rag, about, settings)
- `ui.py` – shared components, icons, navigation helpers · `art.py` – SVG illustrations and agent metadata
- `parsers.py` – turns agent Markdown into roadmap/quiz/resource structures (falls back to plain Markdown)
- `state.py` – session-state defaults (original keys preserved)
- `assets/style.css` – design system · `static/fonts/` – self-hosted Cormorant Garamond + DM Sans
- `tests/test_app_flow.py` – end-to-end UI test (`python tests/test_app_flow.py`)
