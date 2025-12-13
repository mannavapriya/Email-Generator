import streamlit as st
import tempfile
import openai
from memory.json_memory import get_profile, upsert_profile
from workflow.langgraph_flow import run_email_workflow

def main():
    st.set_page_config(page_title="Email Generator", layout="wide")
    st.title("Email Generator")

    # Sidebar
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

    col1, col2 = st.columns([2,3])
    with col1:
        st.subheader("Compose")
        mode = st.radio("Input mode", ["Text","Voice"], index=0)
        user_text = ""

        if mode == "Text":
            user_text = st.text_area("Describe intent (e.g., 'to: Alice\\nFollow-up on proposal... tone: formal')", height=200)
        else:
            st.info("Upload a WAV file (.wav only). Whisper will transcribe it.")
            if "voice_text" not in st.session_state:
                st.session_state["voice_text"] = ""

            audio_file = st.file_uploader("Upload WAV audio", type=["wav"])
            if audio_file:
                with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp:
                    tmp.write(audio_file.read())
                    audio_path = tmp.name

                # Transcribe using OpenAI Whisper
                with open(audio_path, "rb") as f:
                    response = openai.Audio.transcriptions.create(
                        file=f,
                        model="gpt-4o-transcribe",
                        language="en"
                    )
                st.session_state["voice_text"] = response.text
                st.write("Transcription:", response.text)

            user_text = st.session_state["voice_text"]

        tone_choice = st.selectbox("Tone (optional)", ["(profile)","formal","casual","assertive"], index=0)
        if st.button("Generate email"):
            if not user_text:
                st.warning("Enter text or record voice.")
            else:
                extra = f"\n\ntone: {tone_choice}" if tone_choice and tone_choice != "(profile)" else ""
                full_text = user_text + extra
                with st.spinner("Generating draft..."):
                    result = run_email_workflow(full_text)
                    st.session_state["last_result"] = result

    with col2:
        st.subheader("Draft & Actions")
        last = st.session_state.get("last_result")
        if last:
            draft = last.get("personalized_draft") or last.get("draft") or {}
            subj = draft.get("subject","")
            body = draft.get("body","")
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

    st.markdown("---")
    st.markdown("~ Because writing emails manually is a 2010 problem. 😄")
