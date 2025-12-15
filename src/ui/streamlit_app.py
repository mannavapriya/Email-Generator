# -*- coding: utf-8 -*-
"""
Streamlit app for Email Assistant with live agent trace.
Shows only the currently executing agent's output.
"""

import os
import tempfile
import streamlit as st
import openai

from memory.json_memory import get_profile, upsert_profile
from workflow.langgraph_flow import run_email_workflow

def main():
    st.set_page_config(page_title="Email Generator", layout="wide")
    st.title("Email Generator")

    # -------------------------
    # Sidebar: User Profile
    # -------------------------
    st.sidebar.header("User Profile")
    profile = get_profile("default")
    name = st.sidebar.text_input("Sender name", value=profile.get("name", "Manasa"))
    company = st.sidebar.text_input("Company", value=profile.get("company", "Stealth Startup"))
    signature = st.sidebar.text_area("Signature", value=profile.get("signature", "Best,\nManasa"))

    if st.sidebar.button("Save profile"):
        upsert_profile(
            "default",
            {
                "name": name,
                "company": company,
                "signature": signature,
                "preferred_tone": profile.get("preferred_tone", "formal"),
                "sent_examples": profile.get("sent_examples", []),
            },
        )
        st.sidebar.success("Saved.")

    # -------------------------
    # Main layout
    # -------------------------
    col1, col2 = st.columns([2, 3])

    with col1:
        st.subheader("Compose")
        mode = st.radio("Input mode", ["Text", "Voice"], index=0)
        user_text = ""

        if mode == "Text":
            user_text = st.text_area(
                "Describe intent (e.g., 'to: Alice\\nFollow-up on meeting... tone: formal')",
                height=200,
            )
        else:
            st.info("Upload an audio file (WAV, MP3, M4A, MP4).")
            if "voice_text" not in st.session_state:
                st.session_state["voice_text"] = ""

            audio_file = st.file_uploader("Upload audio", type=["wav", "mp3", "m4a", "mp4"])
            if audio_file:
                suffix = "." + audio_file.name.split(".")[-1]
                with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
                    tmp.write(audio_file.read())
                    audio_path = tmp.name

                client = openai.OpenAI()
                with open(audio_path, "rb") as f:
                    transcript = client.audio.transcriptions.create(
                        file=f,
                        model="gpt-4o-transcribe",
                        language="en",
                    )
                st.session_state["voice_text"] = getattr(transcript, "text", "")
                st.write("Transcription:")
                st.write(st.session_state["voice_text"])

            user_text = st.session_state["voice_text"]

        tone_choice = st.selectbox("Tone (optional)", ["(profile)", "formal", "casual", "assertive"], index=0)

        if st.button("Generate email"):
            if not user_text:
                st.warning("Enter text or upload voice input.")
            else:
                extra = f"\n\ntone: {tone_choice}" if tone_choice != "(profile)" else ""
                full_text = user_text + extra

                st.info("Generating draft...")

                # Placeholder for live trace
                trace_placeholder = st.empty()

                # Run workflow manually to show live trace
                state = {"messages": [{"content": full_text}], "flow": []}
                agents = run_email_workflow.__defaults__[0] if hasattr(run_email_workflow, "__defaults__") else None

                # Using the agents defined inside run_email_workflow
                agents = [
                    ("input_parser_agent", lambda s: run_email_workflow.__globals__["input_parser_agent"](s)),
                    ("intent_detection_agent", lambda s: run_email_workflow.__globals__["intent_detection_agent"](s, llm=run_email_workflow.__globals__["make_openai_llm"]())),
                    ("tone_stylist_agent", lambda s: run_email_workflow.__globals__["tone_stylist_agent"](s)),
                    ("draft_writer_agent", lambda s: run_email_workflow.__globals__["draft_writer_agent"](s, llm=run_email_workflow.__globals__["make_openai_llm"]())),
                    ("personalization_agent", lambda s: run_email_workflow.__globals__["personalization_agent"](s)),
                    ("review_agent", lambda s: run_email_workflow.__globals__["review_agent"](s, llm=run_email_workflow.__globals__["make_openai_llm"]())),
                    ("router_agent", lambda s: run_email_workflow.__globals__["router_agent"](s))
                ]

                for name, fn in agents:
                    output = fn(state)
                    state.update(output)
                    state["flow"].append({"agent": name, "output": output})
                    # Update only the current agent
                    trace_placeholder.markdown(f"### {name}")
                    trace_placeholder.json(output)

                st.session_state["last_result"] = state

    # -------------------------
    # Draft & Actions Column
    # -------------------------
    with col2:
        st.subheader("Draft & Actions")
        last = st.session_state.get("last_result")

        if last:
            draft = last.get("personalized_draft") or last.get("draft") or {}
            subject = draft.get("subject", "")
            body = draft.get("body", "")
        else:
            subject = ""
            body = ""
            st.info("No email generated yet.")

        subject_edit = st.text_input("Subject", subject)
        body_edit = st.text_area("Body", body, height=400)

        st.download_button(
            "Download .txt",
            data=f"Subject: {subject_edit}\n\n{body_edit}",
            file_name="email_draft.txt",
            mime="text/plain",
            disabled=not bool(subject_edit or body_edit),
        )

        if st.button("Save to profile history", disabled=not last):
            prof = get_profile("default")
            prof.setdefault("sent_examples", []).append({"subject": subject_edit, "body": body_edit})
            upsert_profile("default", prof)
            st.success("Saved.")

        if st.button("Simulate send", disabled=not last):
            prof = get_profile("default")
            prof.setdefault("sent_examples", []).append({"subject": subject_edit, "body": body_edit})
            upsert_profile("default", prof)
            st.success("Email sent (simulation).")

    st.markdown("---")
    st.markdown("~ Because writing emails manually is a 2010 problem. 😄")

if __name__ == "__main__":
    main()
