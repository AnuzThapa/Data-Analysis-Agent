# 🧠 Database Query Agent

A powerful and interactive Streamlit-based agent for querying databases and generating insightful visualizations using local LLMs, advanced model APIs, and persistent memory.

---

## 🚀 Features

- 🔍 **Query Natural Language to SQL**: Ask questions like "Show me users who signed up last week" — the agent converts your query into SQL and fetches data.
- 🧠 **Local Language Model (Ollama)**: Uses a lightweight, privacy-friendly LLM for prompt understanding and SQL generation.
- 📊 **Smart Data Visualizations**: Automatically generate charts and graphs using advanced paid models for more accurate and insightful visual summaries.
- 🗃 **Supabase Integration**: Connects to and queries your Supabase-hosted PostgreSQL databases.
- ♻️ **LangGraph + Memory Checkpointing**: Maintains context across sessions and handles complex user interactions via graph-based reasoning and memory.

---

## 🛠 Tech Stack

| Layer              | Technology        |
|-------------------|-------------------|
| Frontend UI        | [Streamlit](https://streamlit.io) |
| LLM (local)        | [Ollama](https://ollama.com) |
| LLM (visualization)| Paid LLMs (e.g., GPT-4, Claude) |
| Backend Logic      | [LangGraph](https://www.langgraph.dev/) |
| Memory             | LangGraph MemoryCheckpoint |
| Database           | [Supabase](https://supabase.com) |

---

## 📦 Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/AnuzThapa/Data-Analysis-Agent.git
   cd your-repo
```
2. uv init
3. uv sync
4. activate environemnt
5. streamlit run frontend/chat_local.py
