import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
import uuid

st.set_page_config(page_title="AI Survey", page_icon="🤖")

# חיבור לבסיס נתונים פנימי של סטרימליט
conn = st.connection("dicts", type="dict")

st.title("AI survey for virology course by Ilana S. Fratty")

lang = st.radio("Language / שפה", ["English", "עברית"], horizontal=True)
is_he = lang == "עברית"

t = {
    "q1": "האם אתם משתמשים ב-AI?" if is_he else "Do you use AI?",
    "q2": "באילו כלי בינה מלאכותית אתם משתמשים?" if is_he else "Which AI tools do you use?",
    "q3": "האם אתם משלמים על כלי AI?" if is_he else "Do you pay for any AI tools?",
    "submit": "שלח תגובה" if is_he else "Submit Response",
    "thanks": "תודה! התגובה נשמרה" if is_he else "Thank you! Response saved",
    "results": "תוצאות בזמן אמת" if is_he else "Real-time Results"
}

# טופס
with st.form("survey"):
    u_ai = st.radio(t["q1"], ["Yes/כן", "No/לא"])
    p_ai = st.radio(t["q3"], ["Yes/כן", "No/לא"])
    tools = st.text_input(t["q2"])
    if st.form_submit_button(t["submit"]):
        new_id = str(uuid.uuid4())
        # שמירה בבסיס הנתונים המשותף
        conn.set(new_id, {"usesAI": u_ai, "pays": p_ai, "tool": tools})
        st.success(t["thanks"])
        st.balloons()

# שליפת כל הנתונים מכל המשתמשים
all_data = conn.getall()
if all_data:
    st.divider()
    st.subheader(t["results"])
    df = pd.DataFrame(list(all_data.values()))
    
    col1, col2 = st.columns(2)
    with col1:
        fig1 = px.pie(df, names="usesAI", title="Uses AI?")
        st.plotly_chart(fig1, use_container_width=True)
    with col2:
        fig2 = px.pie(df, names="pays", title="Pays for AI?")
        st.plotly_chart(fig2, use_container_width=True)
    
    st.metric("Total Responses", len(df))
