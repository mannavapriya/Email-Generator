import streamlit as st
import tempfile
from openai import OpenAI
import os

from memory.json_memory import get_profile, upsert_profile
from workflow.langgraph_flow import run_email_workflow

# ---------------------------
# LangSmith environment
# ---------------------------
os.environ["OPENAI_API_KEY"] = st.secrets["OPENAI_API_KEY"]
os.environ["LANGSMITH_API_KEY"] = st.secrets["LANGSMITH_API_KEY"]
os.environ["LANGSMITH_PROJECT"] = st.secrets["LANGSMITH_PROJECT"]
os.environ["LANGSMITH_TRACING"] = str(st.secrets.get("LANGSMITH_TRACING", "true")).lower()
os.environ["LANGSMITH_ENDPOINT"] = st.secrets.get(
    "LANGSMITH_ENDPOINT", "https://api.smith.langchain.com"
)

from langsmith import Client
client = Client()

def main():
    st.set_page_config(page_title="Email Generator", layout="wide")
    st.title("Email Generator")

    # Initialize OpenAI client (NEW API – REQUIRED)
    openai_client = OpenAI()

    # ---------------------------
    # Sidebar: User Profile
    # ---------------------------
    st.sidebar.header("User Profile")
    profile = get_profile("default")

    name = st.sidebar.text_input(
        "Sender name",
        value=profile.get("name", "Manasa")
    )
    company = st.sidebar.text_input(
        "Company",
        value=profile.get("company", "Stealth Startup")
    )
    signature = st.sidebar.text_area(
        "Signature",
        value=profile.get("signature", "Best,\nManasa")
    )

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

    # ---------------------------
    # Main Layout
    # ---------------------------
    col1, col2 = st.columns([2, 3])

    # ---------------------------
    # Compose Column
    # ---------------------------
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
            st.info(
                "Upload an audio file (WAV, MP3, M4A, MP4) with email intent. "
                "The audio track will be transcribed."
            )

            if "voice_text" not in st.session_state:
                st.session_state["voice_text"] = ""

            audio_file = st.file_uploader(
                "Upload audio",
                type=["wav", "mp3", "m4a", "mp4"],
            )

            if audio_file:
                # Preserve original file extension
                suffix = "." + audio_file.name.split(".")[-1]

                with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
                    tmp.write(audio_file.read())
                    audio_path = tmp.name

                # Transcription using NEW OpenAI API
                with open(audio_path, "rb") as f:
                    transcript = openai_client.audio.transcriptions.create(
                        file=f,
                        model="gpt-4o-transcribe",
                        language="en",
                    )

                st.session_state["voice_text"] = transcript.text
                st.write("Transcription:", transcript.text)

            user_text = st.session_state["voice_text"]

        tone_choice = st.selectbox(
            "Tone (optional)",
            ["(profile)", "formal", "casual", "assertive"],
            index=0,
        )

        if st.button("Generate email"):
            if not user_text:
                st.warning("Enter text or upload voice input.")
            else:
                extra = (
                    f"\n\ntone: {tone_choice}"
                    if tone_choice and tone_choice != "(profile)"
                    else ""
                )
                full_text = user_text + extra

                # Container for showing agent-by-agent outputs
                trace_container = st.empty()

                with st.spinner("Generating draft..."):
                    # Provide a callback to show per-agent outputs
                    def on_step(agent_name, output):
                        trace_container.markdown(f"### {agent_name}")
                        trace_container.json(output)

                    result = run_email_workflow(full_text, on_step=on_step)
                    st.session_state["last_result"] = result

                st.success("Draft generated. Trace should appear in LangSmith dashboard.")

    # ---------------------------
    # Draft & Actions Column
    # ---------------------------
    with col2:
        st.subheader("Draft & Actions")

        last = st.session_state.get("last_result")

        if last:
            draft = last.get("personalized_draft") or last.get("draft") or {}
            subject = draft.get("subject", "")
            body = draft.get("body", "")
            info_text = None
        else:
            subject = ""
            body = ""
            info_text = (
                "No email generated yet.\n\n"
                "Use the **Compose** panel on the left and click **Generate email** "
                "to see your draft here."
            )

        subject_edit = st.text_input("Subject", subject)
        body_edit = st.text_area("Body", value=body, height=400)

        if info_text:
            st.info(info_text)

        st.download_button(
            "Download .txt",
            data=f"Subject: {subject_edit}\n\n{body_edit}",
            file_name="email_draft.txt",
            mime="text/plain",
            disabled=not bool(subject_edit or body_edit),
        )

        if st.button("Save to profile history", disabled=not last):
            prof = get_profile("default")
            prof.setdefault("sent_examples", []).append(
                {"subject": subject_edit, "body": body_edit}
            )
            upsert_profile("default", prof)
            st.success("Saved to profile history.")

        if st.button("Simulate send", disabled=not last):
            prof = get_profile("default")
            prof.setdefault("sent_examples", []).append(
                {"subject": subject_edit, "body": body_edit}
            )
            upsert_profile("default", prof)
            st.success("Email sent (simulation). Saved to profile history.")

    st.markdown("---")
    st.markdown("~ Because writing emails manually is a 2010 problem. 😄")


if __name__ == "__main__":
    main()
