# Agentic AI Email Generator

**Email Generator** is an AI-powered assistant that helps professionals quickly create, personalize, and validate emails. Using multi-agent workflows and large language models (LLMs), it generates high-quality drafts in seconds, tailored to the recipient and the desired tone.

---

## Features

- **Fast Email Drafting:** Reduce time spent composing emails from 15–20 minutes to under 2 minutes.  
- **Context-Aware:** Adapts tone and content based on recipient and situation.  
- **Tone Options:** Formal, casual, or assertive email styles.  
- **Multi-Purpose:** Supports outreach, follow-ups, internal updates, and more.  
- **Personalization & Memory:** Remembers user preferences and prior drafts.  

---

## How It Works

The app uses a **multi-agent system** to process user input and generate polished emails:

1. **Input Parsing Agent:** Extracts intent, recipient, tone, and constraints from your prompt.  
2. **Intent Detection Agent:** Determines if your email is an outreach, follow-up, apology, or other.  
3. **Tone Stylist Agent:** Adjusts language style to formal, casual, or assertive.  
4. **Draft Writer Agent:** Generates the main email body.  
5. **Personalization Agent:** Inserts your name, signature, and prior context.  
6. **Review & Validator Agent:** Checks grammar, tone alignment, and coherence.  
7. **Routing & Memory Agent:** Handles fallback logic and stores user preferences.  

---

## Usage

1. Open the app (Cloud).  
2. Select the **email tone**: formal, casual, or assertive.  
3. Enter or speak your **email intent**.  
4. Preview, edit, and export your **personalized email draft**.

---

## Deployment

**Streamlit Cloud:** https://email-generator-agentic-ai.streamlit.app/

---

## Project Structure

```text
email_assistant/
├── streamlit_app.py        # Streamlit Cloud entrypoint
├── requirements.txt        # Python dependencies
├── runtime.txt 
├── src/
│   ├── ui/                 # Streamlit UI
│   ├── agents/             # Modular agent code
│   ├── workflow/           # LangGraph workflow
│   └── integrations/       # API clients
├── memory/                 # User profile JSON
├── data/                   # Tone samples
└── config/                 # MCP routing config
