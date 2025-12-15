import os
import tempfile
import streamlit as st
from memory.json_memory import get_profile, upsert_profile
from workflow.langgraph_flow import (
    input_parser_agent,
    intent_detection_agent,
    tone_stylist_agent,
    draft_writer_agent,
    personalization_agent,
    review_agent,
    router_agent
)
from integrations.llm_client import make_openai_llm
from openai import OpenAI

def main():
    st.set_page_config(page_title="Email Generator", layout="wide")
    st.title("Email Generator")

    # Initialize OpenAI client
    client = OpenAI()

    # ─────────────────────────────────────────────
    # Sidebar: User Profile
    # ─────────────────────────────────────────────
    st.sidebar.header("User Profile")
    profile = get_profile("default")

    name = st.sidebar.text_input("Sender name", value=profile.get("name", "Manasa"))
    company = st.sidebar.text_input("Company", value=profile.get("company", "Stealth Startup"))
    signature = st.sidebar.text_area("Signature", value=profile.get("signature", "Best,\nManasa"))

    if st.sidebar.button("Save profile"):
        upsert_profile("default", {
            "name": name,
            "company": company,
            "signature": signature,
            "preferred_tone": profile.get("preferred_tone", "formal"),
            "sent_examples": profile.get("sent_examples", []),
        })
        st.sidebar.success("Saved.")

    # ─────────────────────────────────────────────
    # Main Layout
    # ─────────────────────────────────────────────
    col1, col2 = st.columns([2, 3])

    # ─────────────────────────────────────────────
    # Compose Column
    # ─────────────────────────────────────────────
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
            st.info("Upload an audio file (WAV, MP3, M4A, MP4) with email intent.")
            if "voice_text" not in st.session_state:
                st.session_state["voice_text"] = ""

            audio_file = st.file_uploader("Upload audio", type=["wav", "mp3", "m4a", "mp4"])
            if audio_file:
                suffix = "." + audio_file.name.split(".")[-1]
                with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
                    tmp.write(audio_file.read())
                    audio_path = tmp.name

                with open(audio_path, "rb") as f:
                    transcript = client.audio.transcriptions.create(
                        file=f,
                        model="gpt-4o-transcribe",
                        language="en",
                    )

                text_result = transcript.get("text") if isinstance(transcript, dict) else getattr(transcript, "text", "")
                st.session_state["voice_text"] = text_result
                st.write("Transcription:", text_result)

            user_text = st.session_state["voice_text"]

        tone_choice = st.selectbox("Tone (optional)", ["(profile)", "formal", "casual", "assertive"], index=0)

        if st.button("Generate email"):
            if not user_text:
                st.warning("Enter text or upload voice input.")
            else:
                extra = f"\n\ntone: {tone_choice}" if tone_choice != "(profile)" else ""
                full_text = user_text + extra

                spinner_placeholder = st.empty()
                trace_placeholder = st.empty()
                spinner_placeholder.info("Generating draft...")

                # Initialize state and LLM
                state = {"messages": [{"content": full_text}], "flow": [], "route": None}
                llm = make_openai_llm()

                # Define agents
                agents = [
                    ("input_parser_agent", lambda s: input_parser_agent(s)),
                    ("intent_detection_agent", lambda s: intent_detection_agent(s, llm)),
                    ("tone_stylist_agent", lambda s: tone_stylist_agent(s)),
                    ("draft_writer_agent", lambda s: draft_writer_agent(s, llm)),
                    ("personalization_agent", lambda s: personalization_agent(s)),
                    ("review_agent", lambda s: review_agent(s, llm)),
                    ("router_agent", lambda s: router_agent(s)),
                ]

                # Run agents and display trace
                for name, fn in agents:
                    output = fn(state)
                    state.update(output)
                    state["flow"].append({"agent": name, "output": output})

                    trace_placeholder.markdown(f"### {name}")
                    trace_placeholder.json(output)

                spinner_placeholder.empty()
                st.session_state["last_result"] = state

    # ─────────────────────────────────────────────
    # Draft & Actions Column
    # ─────────────────────────────────────────────
    with col2:
        st.subheader("Draft & Actions")
        last = st.session_state.get("last_result")

        if last:
            draft = last.get("personalized_draft") or last.get("draft") or {}
            subject = draft.get("subject", "")
            body = draft.get("body", "")
            subject_edit = st.text_input("Subject", subject)
            body_edit = st.text_area("Body", value=body, height=400)

            st.download_button(
                "Download .txt",
                data=f"Subject: {subject_edit}\n\n{body_edit}",
                file_name="email_draft.txt",
                mime="text/plain",
            )

            if st.button("Save to profile history"):
                prof = get_profile("default")
                prof.setdefault("sent_examples", []).append({"subject": subject_edit, "body": body_edit})
                upsert_profile("default", prof)
                st.success("Saved to profile history.")

            if st.button("Simulate send"):
                prof = get_profile("default")
                prof.setdefault("sent_examples", []).append({"subject": subject_edit, "body": body_edit})
                upsert_profile("default", prof)
                st.success("Email sent (simulation). Saved to profile history.")
        else:
            st.info("No draft yet. Generate an email to see the preview.")

    st.markdown("---")
    st.markdown("~ Because writing emails manually is a 2010 problem. 😄")


if __name__ == "__main__":
    main()
