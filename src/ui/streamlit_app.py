import os
import tempfile
import streamlit as st
from memory.json_memory import get_profile, upsert_profile
from workflow.langgraph_flow import run_email_workflow
from integrations.llm_client import make_openai_llm
import openai

# Import LangSmith client from old langsmith version
try:
    from langsmith import LangSmith
except ImportError:
    LangSmith = None

def main():
    st.set_page_config(page_title="Email Generator", layout="wide")
    st.title("Email Generator")

    # Sidebar: User Profile
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

    # Main Layout
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
            st.info("Upload an audio file (WAV, MP3, M4A, MP4). Transcribed with Whisper.")
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
                st.write("Transcription:", st.session_state["voice_text"])

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

                # Optional LangSmith tracing (only if old langsmith available)
                tracer = None
                if LangSmith and os.environ.get("LANGSMITH_TRACING", "").lower() == "true":
                    tracer = LangSmith(
                        api_key=os.environ.get("LANGSMITH_API_KEY"),
                        project=os.environ.get("LANGSMITH_PROJECT"),
                        endpoint=os.environ.get("LANGSMITH_ENDPOINT"),
                    )

                # Make LLM
                llm = make_openai_llm()

                # Run workflow
                result = run_email_workflow(full_text, llm=llm, tracer=tracer)
                st.session_state["last_result"] = result

                # Display trace in Streamlit if workflow returns it
                if result and "flow" in result:
                    for step in result["flow"]:
                        agent_name = step.get("agent", "unknown_agent")
                        output = step.get("output", {})
                        trace_placeholder.markdown(f"### {agent_name}")
                        trace_placeholder.json(output)

                spinner_placeholder.empty()

    # Draft & Actions Column
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
            st.info("No email generated yet.\nUse the Compose panel and click Generate email.")

        subject_edit = st.text_input("Subject", subject)
        body_edit = st.text_area("Body", value=body, height=400)

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
            st.success("Saved to profile history.")

        if st.button("Simulate send", disabled=not last):
            prof = get_profile("default")
            prof.setdefault("sent_examples", []).append({"subject": subject_edit, "body": body_edit})
            upsert_profile("default", prof)
            st.success("Email sent (simulation). Saved to profile history.")

    st.markdown("---")
    st.markdown("~ Because writing emails manually is a 2010 problem. 😄")


if __name__ == "__main__":
    main()
