import streamlit as st
import pandas as pd
import plotly.express as px
import uuid

st.set_page_config(page_title="AI Survey", page_icon="🤖")

# חיבור לבסיס נתונים פנימי
# אם זה מבקש הגדרה, נגדיר אותה ב-Secrets
try:
    conn = st.connection("dicts", type="dict")
except Exception:
    st.error("Please connect the 'Dictionaries' data source in Streamlit Settings.")
    st.stop()

st.title("AI survey for virology course by Ilana S. Fratty")

lang = st.radio("Language / שפה", ["English", "עברית"], horizontal=True)
is_he = lang == "עברית"

t = {
    "q1": "האם אתם משתמשים ב-AI?" if is_he else "Do you use AI?",
    "q2": "באילו כלי בינה מלאכותית אתם משתמשים?" if is_he else "Which AI tools do you use?",
    "submit": "שלח תגובה" if is_he else "Submit Response",
    "thanks": "תודה! התגובה נשמרה במערכת" if is_he else "Thank you! Response saved",
    "results": "תוצאות מצטברות (בזמן אמת)" if is_he else "Real-time Results"
}

with st.form("survey"):
    u_ai = st.radio(t["q1"], ["Yes/כן", "No/לא"])
    tools = st.text_input(t["q2"])
    if st.form_submit_button(t["submit"]):
        new_id = str(uuid.uuid4())
        # שמירה בענן של סטרימליט
        conn.set(new_id, {"usesAI": u_ai, "tool": tools})
        st.success(t["thanks"])
        st.balloons()

# שליפת הנתונים מכל המכשירים
all_data = conn.getall()
if all_data:
    st.divider()
    st.subheader(t["results"])
    df = pd.DataFrame(list(all_data.values()))
    
    fig = px.pie(df, names="usesAI", title="AI Adoption", color_discrete_sequence=['#F27D26', '#141414'])
    st.plotly_chart(fig, use_container_width=True)
    st.metric("Total Responses", len(df))
