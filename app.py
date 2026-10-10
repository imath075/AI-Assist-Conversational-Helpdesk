
import streamlit as st
from src.triage import analyse_issue
from src.conversation import next_reply, reset_case

st.set_page_config(page_title="AI-Assist", page_icon="🛠️", layout="wide")

st.markdown("""
<style>
.block-container {max-width: 1050px; padding-top: 1.2rem;}
#MainMenu, footer {visibility:hidden;}
</style>
""", unsafe_allow_html=True)

if "case" not in st.session_state:
    reset_case(st.session_state)

with st.sidebar:
    st.title("AI-Assist")
    st.caption("Teacher IT Support")
    if st.button("New support request", use_container_width=True):
        reset_case(st.session_state)
        st.rerun()

    case = st.session_state.case
    if case.get("triage"):
        st.divider()
        st.subheader("Case Summary")
        t = case["triage"]
        st.write(f"**Category:** {t['category']}")
        st.write(f"**Priority:** {t['priority']}")
        st.write(f"**Issue Type:** {t['issue_type']}")

st.title("IT Support")
st.caption("Describe the problem in your own words.")

for m in st.session_state.messages:
    avatar = "👩‍🏫" if m["role"] == "user" else "🛠️"
    with st.chat_message(m["role"], avatar=avatar):
        st.markdown(m["content"])


# Quick response buttons appear only while troubleshooting.
if st.session_state.case.get("status") == "troubleshooting":
    st.caption("Quick response")
    b1, b2, b3 = st.columns(3)
    clicked = None
    if b1.button("✅ Solved", use_container_width=True):
        clicked = "Solved"
    if b2.button("❌ Not solved", use_container_width=True):
        clicked = "Not solved"
    if b3.button("⬆️ Escalate to IT", use_container_width=True):
        clicked = "Escalate to IT"

    if clicked:
        st.session_state.messages.append({"role": "user", "content": clicked})
        reply = next_reply(clicked, st.session_state.case)
        st.session_state.messages.append({"role": "assistant", "content": reply})
        st.rerun()

prompt = st.chat_input("Type your IT problem or reply here...")

if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user", avatar="👩‍🏫"):
        st.markdown(prompt)

    reply = next_reply(prompt, st.session_state.case)
    st.session_state.messages.append({"role": "assistant", "content": reply})

    with st.chat_message("assistant", avatar="🛠️"):
        st.markdown(reply)
