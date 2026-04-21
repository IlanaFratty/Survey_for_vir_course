import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
import uuid

# --- UI SETUP ---
st.set_page_config(page_title="AI Survey", page_icon="🤖")

# כותרת האפליקציה
st.title("AI survey for virology course by Ilana S. Fratty")

# שפת ממשק
lang = st.radio("Language / שפה", ["English", "עברית"], horizontal=True)
is_he = lang == "עברית"

t = {
    "q1": "האם אתם משתמשים ב-AI?" if is_he else "Do you use AI?",
    "q2": "באילו כלי בינה מלאכותית אתם משתמשים?" if is_he else "Which AI tools do you use?",
    "q3": "האם אתם משלמים על כלי AI?" if is_he else "Do you pay for any AI tools?",
    "submit": "שלח תגובה" if is_he else "Submit Response",
    "thanks": "תודה! התגובה נשמרה (סימולציה להרצאה)" if is_he else "Thank you! Response saved",
    "results": "תוצאות בזמן אמת (מדגם)" if is_he else "Real-time Results"
}

# שימוש ב-Session State לשמירת תוצאות זמניות (עובד מעולה להדגמה חיה!)
if 'responses' not in st.session_state:
    st.session_state.responses = []

# טופס הסקר
with st.form("survey"):
    u_ai = st.radio(t["q1"], ["Yes/כן", "No/לא"])
    p_ai = st.radio(t["q3"], ["Yes/כן", "No/לא"])
    tools = st.text_input(t["q2"])
    
    if st.form_submit_button(t["submit"]):
        st.session_state.responses.append({
            "usesAI": u_ai,
            "pays": p_ai,
            "tool": tools if tools else "None"
        })
        st.success(t["thanks"])

# הצגת תוצאות במידה ויש תגובות
if st.session_state.responses:
    st.divider()
    st.subheader(t["results"])
    df = pd.DataFrame(st.session_state.responses)
    
    col1, col2 = st.columns(2)
    with col1:
        fig1 = px.pie(df, names="usesAI", title="Uses AI?", color_discrete_sequence=['#F27D26', '#141414'])
        st.plotly_chart(fig1, use_container_width=True)
    with col2:
        fig2 = px.pie(df, names="pays", title="Pays for AI?", color_discrete_sequence=['#F27D26', '#141414'])
        st.plotly_chart(fig2, use_container_width=True)
