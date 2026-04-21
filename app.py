import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="AI Survey", page_icon="🤖")

# זה ה"מחסן" המשותף של כל הסטודנטים בשרת
if "database" not in st.session_state:
    @st.cache_resource
    def get_db():
        return [] # רשימה משותפת לכולם
    st.session_state.db = get_db()

st.title("AI survey for virology course by Ilana S. Fratty")

lang = st.radio("Language / שפה", ["English", "עברית"], horizontal=True)
is_he = lang == "עברית"

t = {
    "q1": "האם אתם משתמשים ב-AI?" if is_he else "Do you use AI?",
    "q2": "באילו כלי בינה מלאכותית אתם משתמשים?" if is_he else "Which AI tools do you use?",
    "submit": "שלח תגובה" if is_he else "Submit Response",
    "thanks": "תודה! התגובה נוספה" if is_he else "Thank you! Response added",
    "results": "תוצאות מצטברות בזמן אמת" if is_he else "Live Cumulative Results"
}

with st.form("survey_form"):
    u_ai = st.radio(t["q1"], ["Yes/כן", "No/לא"])
    tools = st.text_input(t["q2"])
    if st.form_submit_button(t["submit"]):
        # הוספה לרשימה המשותפת בשרת
        st.session_state.db.append({"usesAI": u_ai, "tool": tools})
        st.success(t["thanks"])
        st.balloons()

# הצגת התוצאות לכולם
if len(st.session_state.db) > 0:
    st.divider()
    st.subheader(t["results"])
    df = pd.DataFrame(st.session_state.db)
    
    col1, col2 = st.columns([2, 1])
    with col1:
        fig = px.pie(df, names="usesAI", title="AI Adoption", color_discrete_sequence=['#F27D26', '#141414'])
        st.plotly_chart(fig, use_container_width=True)
    with col2:
        st.metric("Total Responses", len(df))
    
    if st.button("Refresh Results 🔄"):
        st.rerun()
