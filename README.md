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

## Example Intents

### 1) Professional Follow-Up After a Meeting
Draft a polished and comprehensive follow-up email to a senior stakeholder after a 45-minute product strategy meeting.
The email should:
Thank the recipient for their time and insights
Summarize the key discussion points and decisions made
Clearly outline next steps, owners, and tentative timelines
Be concise but thorough, suitable for an executive audience
Assume the sender is a product or engineering lead and the recipient expects clarity, accountability, and alignment.

### 2) Assertive Tone : Action Required / Deadline Enforcement
Generate a email requesting immediate action on an overdue deliverable.
The email should:
State the issue and expectation in the opening sentence
Reference the original deadline and current impact of the delay
Specify exactly what is required and by when
Reinforce accountability and urgency without being hostile
End with a firm call to action and next steps
Assume the recipient is responsible for the deliverable and resolution is time-sensitive.

### 3) Casual / Friendly: Secret Santa & Christmas Party Invitation
Write a email inviting my friend to participate in a Secret Santa exchange and attend a Christmas party.
The email should:
Open with a warm, informal greeting that reflects a close friendship
Briefly set the festive context and excitement around the holidays
Share key details about the Secret Santa (what it is, how it works, and why it will be fun)
Mention the Christmas party in a relaxed, inviting way, including high-level details (date/time or general plan)
Encourage her to join without pressure, keeping the tone light and inclusive
Invite questions or follow-ups if she needs more details
Close with an upbeat, affectionate, and holiday-spirited sign-off 
Assume the recipient is a friend, and the goal is to make her feel genuinely included and excited to join.

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
