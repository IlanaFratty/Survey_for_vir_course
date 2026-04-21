import streamlit as st
import pandas as pd
import plotly.express as px
from streamlit_gsheets import GSheetsConnection
from datetime import datetime
import uuid
import os

# --- GOOGLE SHEETS SETUP ---
# You must set GSHEETS_URL in the Secrets panel or .env file.
# The sheet should have these headers: id, userId, usesAI, tools, paysForAI, timestamp
SPREADSHEET_URL = os.getenv("GSHEETS_URL")

# --- UI SETUP ---
st.set_page_config(
    page_title="AI Survey - Virology Course",
    page_icon="🤖",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Custom Styling
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }
    
    .stButton>button {
        width: 100%;
        border-radius: 12px;
        height: 3em;
        background-color: #141414;
        color: white;
        font-weight: 600;
        border: none;
        transition: all 0.2s ease;
    }
    
    .stButton>button:hover {
        background-color: #F27D26;
        color: white;
    }
</style>
""", unsafe_allow_html=True)

def normalize_tool_name(name):
    """Normalizes AI tool names to group similar entries."""
    n = name.strip().lower()
    mappings = {
        'chatgpt': 'ChatGPT',
        'chat gpt': 'ChatGPT',
        'צ\'אט gpt': 'ChatGPT',
        'צ׳אט gpt': 'ChatGPT',
        'gpt': 'ChatGPT',
        'claude': 'Claude',
        'קלאוד': 'Claude',
        'gemini': 'Gemini',
        'ג׳ימיני': 'Gemini',
        'גמיני': 'Gemini',
        'midjourney': 'Midjourney',
        'מידג׳רני': 'Midjourney',
        'dall-e': 'DALL-E',
        'dalle': 'DALL-E',
        'perplexity': 'Perplexity',
        'פרפלקסיטי': 'Perplexity',
        'copilot': 'Copilot',
        'קו-פיילוט': 'Copilot',
        'קופיילוט': 'Copilot',
    }
    
    for key, val in mappings.items():
        if key in n:
            return val
    return name.strip().title()

def process_tools(tools_str):
    """Splits and normalizes tools input."""
    import re
    tools = re.split(r'[,\n;]', tools_str)
    # Join with semicolon for storage in a single cell
    return [normalize_tool_name(t) for t in tools if t.strip()]

# Language Toggle
lang = st.radio("Language / שפה", ["English", "עברית"], horizontal=True)
is_he = lang == "עברית"

t = {
    "app_title": "AI survey for virology course by Ilana S. Fratty",
    "subtitle": "שתפו את החוויה שלכם עם כלי בינה מלאכותית" if is_he else "Share your experience with AI tools",
    "q1": "האם אתם משתמשים ב-AI?" if is_he else "Do you use AI?",
    "q2": "באילו כלי בינה מלאכותית אתם משתמשים? (הפרידו בפסיקים)" if is_he else "Which AI tools do you use? (Divided by commas)",
    "q3": "האם אתם משלמים על כלי AI כלשהו?" if is_he else "Do you pay for any AI tools?",
    "submit": "שלח תגובה" if is_he else "Submit Response",
    "thanks": "תודה על ההשתתפות!" if is_he else "Thank you for participating!",
    "yes": "כן" if is_he else "Yes",
    "no": "לא" if is_he else "No",
    "results": "תוצאות בזמן אמת" if is_he else "Real-time Results",
}

# --- APP LOGIC ---
st.title(t["app_title"])
st.subheader(t["subtitle"])

# Initialize GSheets Connection
try:
    conn = st.connection("gsheets", type=GSheetsConnection)
except Exception as e:
    st.error("GSheets Connection failed. Please check your configuration.")
    st.stop()

# Load data from Google Sheets
# We set ttl=0 or a very low value for real-time lecture feedback
@st.cache_data(ttl=5)
def get_survey_data():
    if not SPREADSHEET_URL:
        return pd.DataFrame(columns=["id", "userId", "usesAI", "tools", "paysForAI", "timestamp"])
    try:
        data = conn.read(spreadsheet=SPREADSHEET_URL)
        return data
    except Exception:
        return pd.DataFrame(columns=["id", "userId", "usesAI", "tools", "paysForAI", "timestamp"])

df_existing = get_survey_data()

# Persistent User ID in session state or local storage simulation
if 'user_id' not in st.session_state:
    st.session_state.user_id = str(uuid.uuid4())

# Check if user already submitted
user_submitted = False
if not df_existing.empty and 'userId' in df_existing.columns:
    user_submitted = any(df_existing['userId'] == st.session_state.user_id)

if not user_submitted:
    with st.form("survey_form"):
        col1, col2 = st.columns(2)
        uses_ai = col1.radio(t["q1"], [t["yes"], t["no"]])
        pays_ai = col2.radio(t["q3"], [t["yes"], t["no"]])
        
        tools_input = st.text_area(t["q2"], placeholder="e.g. ChatGPT, Claude...")
        
        submitted = st.form_submit_button(t["submit"])
        
        if submitted:
            if not SPREADSHEET_URL:
                st.warning("Please configure GSHEETS_URL in the Secrets panel to enable submissions.")
            else:
                new_row = pd.DataFrame([{
                    "id": str(uuid.uuid4()),
                    "userId": st.session_state.user_id,
                    "usesAI": uses_ai == t["yes"],
                    "tools": ";".join(process_tools(tools_input)),
                    "paysForAI": pays_ai == t["yes"],
                    "timestamp": datetime.now().isoformat()
                }])
                
                # Append to the Google Sheet
                try:
                    updated_df = pd.concat([df_existing, new_row], ignore_index=True)
                    conn.update(spreadsheet=SPREADSHEET_URL, data=updated_df)
                    st.success(t["thanks"])
                    st.cache_data.clear()
                    st.rerun()
                except Exception as e:
                    st.error(f"Error saving data: {e}")

# --- DASHBOARD ---
if not df_existing.empty:
    st.divider()
    st.header(t["results"])
    
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Responses", len(df_existing))
    
    # Calculate %
    if 'usesAI' in df_existing.columns:
        ai_responses = df_existing['usesAI'].astype(bool).sum()
        ai_pct = (ai_responses / len(df_existing)) * 100
        col2.metric("AI Adoption", f"{ai_pct:.1f}%")
    
    if 'paysForAI' in df_existing.columns:
        paid_responses = df_existing['paysForAI'].astype(bool).sum()
        paid_pct = (paid_responses / len(df_existing)) * 100
        col3.metric("Paid Users", f"{paid_pct:.1f}%")
    
    # Tool Ranking
    if 'tools' in df_existing.columns:
        all_tools = []
        for tools_list_str in df_existing['tools'].dropna():
            all_tools.extend(str(tools_list_str).split(";"))
        
        # Filter out empties
        all_tools = [t for t in all_tools if t.strip()]
        
        if all_tools:
            tool_counts = pd.Series(all_tools).value_counts().reset_index()
            tool_counts.columns = ['Tool', 'Count']
            
            st.subheader("Top AI Tools")
            fig = px.bar(tool_counts.head(10), x='Count', y='Tool', orientation='h', color='Count',
                         color_continuous_scale='Oranges')
            fig.update_layout(showlegend=False, height=400)
            st.plotly_chart(fig, use_container_width=True)

    # Export & Admin
    with st.expander("Admin Utility"):
        csv = df_existing.to_csv(index=False).encode('utf-8')
        st.download_button("Download Full CSV", csv, "virology_ai_survey.csv", "text/csv")
        
        if st.button("Force Refresh Dashboard"):
            st.cache_data.clear()
            st.rerun()
else:
    if not SPREADSHEET_URL:
        st.info("👋 Setup required: Add your Google Sheet URL to the app's Secrets as GSHEETS_URL.")
    else:
        st.info("No responses yet. Be the first!")
