"""
Streamlit app for Email Assistant.
This app is intended to be run where the OPEN AI API KEY is available.
"""

# ===========================
# Streamlit and App imports
# ===========================
import streamlit as st
import tempfile
import openai
from memory.json_memory import get_profile, upsert_profile
from workflow.langgraph_flow import run_email_workflow

def main():
    # ===========================
    # Streamlit Config
    # ===========================
    st.set_page_config(page_title="Email Generator", layout="wide")
    st.title("Email Generator")

    # ===========================
    # Sidebar: Profile
    # ===========================
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
            "preferred_tone": profile.get("preferred_tone","formal"),
            "sent_examples": profile.get("sent_examples", [])
        })
        st.sidebar.success("Saved.")

    # ===========================
    # Main UI: Compose & Draft
    # ===========================
    col1, col2 = st.columns([2,3])

    with col1:
        st.subheader("Compose")
        mode = st.radio("Input mode", ["Text","Voice"], index=0)
        user_text = ""
        if mode == "Text":
            user_text = st.text_area("Describe intent (e.g., 'to: Alice\\nFollow-up on proposal... tone: formal')", height=200)
        else:
            st.info("Upload a voice file (.wav, .mp3, or .m4a). It will be transcribed using Whisper.")

            if "voice_text" not in st.session_state:
                st.session_state["voice_text"] = ""

            audio_file = st.file_uploader("Upload audio", type=["wav", "mp3", "m4a"])
            if audio_file:
                # Save uploaded file to a temp file
                with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp:
                    tmp.write(audio_file.read())
                    audio_path = tmp.name

                # Transcribe using OpenAI Whisper
                with open(audio_path, "rb") as f:
                    response = openai.Audio.transcriptions.create(
                        model="gpt-4o-transcribe",  # or "whisper-1"
                        file=f
                    )

                st.session_state["voice_text"] = response["text"]
                st.write("Transcription:", response["text"])

            user_text = st.session_state["voice_text"]

        tone_choice = st.selectbox("Tone (optional)", ["(profile)","formal","casual","assertive"], index=0)

        if st.button("Generate email"):
            if not user_text:
                st.warning("Enter text or upload a voice file.")
            else:
                extra = f"\n\ntone: {tone_choice}" if tone_choice and tone_choice != "(profile)" else ""
                full_text = user_text + extra
                with st.spinner("Generating draft..."):
                    result = run_email_workflow(full_text)
                    st.session_state["last_result"] = result

    with col2:
        st.subheader("Draft & Actions")
        last = st.session_state.get("last_result")
        if not last:
            st.info("No draft yet. Generate an email to see the preview.")
        else:
            try:
                draft = last.get("personalized_draft") or last.get("draft") or {}
                subj = draft.get("subject","")
                body = draft.get("body","")
            except Exception:
                subj = ""
                body = str(last)
            subj_edit = st.text_input("Subject", subj)
            body_edit = st.text_area("Body", value=body, height=400)
            st.download_button("Download .txt", data=f"Subject: {subj_edit}\n\n{body_edit}", file_name="email_draft.txt", mime="text/plain")

            if st.button("Save to profile history"):
                prof = get_profile("default")
                prof.setdefault("sent_examples", []).append({"subject": subj_edit, "body": body_edit})
                upsert_profile("default", prof)
                st.success("Saved to profile history.")

            if st.button("Simulate send"):
                st.success("Email sent (simulation). Saved to profile history.")
                prof = get_profile("default")
                prof.setdefault("sent_examples", []).append({"subject": subj_edit, "body": body_edit})
                upsert_profile("default", prof)

    # ===========================
    # Footer Notes
    # ===========================
    st.markdown("---")
    st.markdown("~ Because writing emails manually is a 2010 problem. 😄")
