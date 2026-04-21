import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="AI Survey", page_icon="🤖")

# מחסן משותף לכל המשתמשים
if "database" not in st.session_state:
    @st.cache_resource
    def get_db():
        return [] 
    st.session_state.db = get_db()

st.title("AI survey for virology course by Ilana S. Fratty")

lang = st.radio("Language / שפה", ["English", "עברית"], horizontal=True)
is_he = lang == "עברית"

t = {
    "q1": "האם אתם משתמשים ב-AI?" if is_he else "Do you use AI?",
    "q2": "באילו כלי בינה מלאכותית אתם משתמשים?" if is_he else "Which AI tools do you use?",
    "q3": "האם אתם משלמים על כלי AI כלשהו?" if is_he else "Do you pay for any AI tools?",
    "submit": "שלח תגובה" if is_he else "Submit Response",
    "thanks": "תודה! התגובה נוספה" if is_he else "Thank you! Response added",
    "results": "תוצאות מצטברות בזמן אמת" if is_he else "Live Cumulative Results"
}

# טופס הסקר
with st.form("survey_form"):
    u_ai = st.radio(t["q1"], ["Yes/כן", "No/לא"])
    p_ai = st.radio(t["q3"], ["Yes/כן", "No/לא"])
    tools = st.text_input(t["q2"])
    
    if st.form_submit_button(t["submit"]):
        st.session_state.db.append({
            "usesAI": u_ai, 
            "paysForAI": p_ai,
            "tool": tools
        })
        st.success(t["thanks"])
        st.balloons()

# הצגת תוצאות
if len(st.session_state.db) > 0:
    st.divider()
    st.subheader(t["results"])
    df = pd.DataFrame(st.session_state.db)
    
    col1, col2 = st.columns(2)
    
    with col1:
        fig1 = px.pie(df, names="usesAI", title="AI Adoption", color_discrete_sequence=['#F27D26', '#141414'])
        st.plotly_chart(fig1, use_container_width=True)
        
    with col2:
        fig2 = px.pie(df, names="paysForAI", title="Paid Users", color_discrete_sequence=['#00CC96', '#636EFA'])
        st.plotly_chart(fig2, use_container_width=True)

    st.metric("Total Responses", len(df))
    
    # הצגת רשימת הכלים שהם כתבו
    st.write("**Tools mentioned:** " + ", ".join(df['tool'].dropna().unique()))
    
    if st.button("Refresh Results 🔄"):
        st.rerun()
