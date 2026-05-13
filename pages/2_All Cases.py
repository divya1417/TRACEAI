import streamlit as st
from pages.helper import db_queries

# ── Page Config ──────────────────────────────────────────────────────────────
st.set_page_config(page_title="All Cases · TraceAI", page_icon="◎", layout="wide")

# ── CSS ──────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    .stApp { font-family: 'Inter', sans-serif; }
    #MainMenu, footer, header { visibility: hidden; }
    [data-testid="collapsedControl"] { display: none !important; }
    section[data-testid="stSidebar"] {
        min-width: 260px !important; max-width: 260px !important;
        transform: none !important; position: relative !important;
    }

    @keyframes fadeInUp {
        from { opacity: 0; transform: translateY(16px); }
        to { opacity: 1; transform: translateY(0); }
    }
    .stApp > div { animation: fadeInUp 0.5s ease-out; }

    .page-tag {
        display: inline-block; padding: 4px 14px; border-radius: 20px;
        font-size: 0.75rem; font-weight: 500; letter-spacing: 1px;
        text-transform: uppercase;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white;
        margin-bottom: 0.5rem;
    }
    .page-title { font-size: 2rem; font-weight: 700; letter-spacing: -1px; margin-bottom: 0.2rem; }
    .page-desc { font-size: 0.95rem; font-weight: 300; opacity: 0.5; margin-bottom: 1.5rem; }
    .minimal-divider {
        height: 1px;
        background: linear-gradient(90deg, transparent, rgba(128,128,128,0.2), transparent);
        margin: 1.5rem 0; border: none;
    }

    /* Case card */
    .case-card {
        border: 1px solid rgba(128,128,128,0.12);
        border-radius: 16px;
        padding: 1.2rem;
        margin-bottom: 1rem;
        transition: all 0.2s ease;
        backdrop-filter: blur(10px);
    }
    .case-card:hover {
        transform: translateY(-3px);
        border-color: rgba(102,126,234,0.3);
        box-shadow: 0 12px 40px rgba(102,126,234,0.06);
    }

    .case-name { font-size: 1.1rem; font-weight: 600; margin-bottom: 2px; }
    .case-meta { font-size: 0.8rem; opacity: 0.5; line-height: 1.6; }

    .status-chip {
        display: inline-block; padding: 3px 12px; border-radius: 12px;
        font-size: 0.7rem; font-weight: 600; letter-spacing: 0.5px;
        text-transform: uppercase;
    }
    .status-found { background: rgba(16,185,129,0.12); color: #10b981; }
    .status-missing { background: rgba(245,158,11,0.12); color: #f59e0b; }

    .case-count {
        font-size: 0.8rem; opacity: 0.4; font-weight: 500;
        letter-spacing: 1px; text-transform: uppercase;
    }

    .empty-state {
        text-align: center; padding: 3rem; opacity: 0.3;
    }
    .empty-state p { font-size: 1.5rem; }

    .section-label {
        font-size: 0.7rem; text-transform: uppercase; letter-spacing: 2px;
        opacity: 0.4; font-weight: 600; margin-bottom: 0.5rem; margin-top: 1rem;
    }
</style>
""", unsafe_allow_html=True)


# ── Auth Guard ───────────────────────────────────────────────────────────────
if "login_status" not in st.session_state or not st.session_state.get("login_status"):
    st.markdown("""
    <div style="text-align:center; padding:4rem 2rem;">
        <p style="font-size:2rem; font-weight:300; opacity:0.4;">🔒</p>
        <p style="font-weight:300; opacity:0.5;">Please login from the Home page.</p>
    </div>
    """, unsafe_allow_html=True)
    st.stop()

user = st.session_state.user


# ── Card renderers ───────────────────────────────────────────────────────────
def render_registered_case(case):
    case = list(case)
    case_id = case[0]
    name = case[1]
    age = case[2]
    status = case[3]
    last_seen = case[4]
    matched_with_id = case[5]

    status_class = "status-found" if status == "F" else "status-missing"
    status_text = "Found" if status == "F" else "Missing"

    col_img, col_info = st.columns([1, 3])

    with col_img:
        try:
            st.image(f"./resources/{case_id}.jpg", use_container_width=True)
        except:
            st.markdown('<div style="height:100px; border-radius:12px; background:rgba(128,128,128,0.08); display:flex; align-items:center; justify-content:center; font-size:1.5rem; opacity:0.3;">📷</div>', unsafe_allow_html=True)

    with col_info:
        st.markdown(f'''
        <div class="case-card">
            <span class="status-chip {status_class}">{status_text}</span>
            <div class="case-name">{name}</div>
            <div class="case-meta">
                Age: {age} &nbsp;·&nbsp; Last seen: {last_seen}
            </div>
        </div>
        ''', unsafe_allow_html=True)

        # Show match details if found
        if matched_with_id and status == "F":
            try:
                matched_with_id = matched_with_id.replace("{", "").replace("}", "")
                details = db_queries.get_public_case_detail(matched_with_id)
                if details:
                    d = details[0]
                    st.markdown(f'''
                    <div style="font-size:0.8rem; opacity:0.6; padding-left:0.5rem; border-left:2px solid #10b981;">
                        <strong>Match Info</strong><br>
                        📍 {d[0]} &nbsp;·&nbsp; 👤 {d[1]} &nbsp;·&nbsp; 📱 {d[2]}
                    </div>
                    ''', unsafe_allow_html=True)
            except:
                pass


def render_public_case(case):
    case = list(case)
    case_id = str(case[0])
    status = case[1]
    location = case[2]
    mobile = case[3]
    birth_marks = case[4]
    submitted_on = case[5]
    submitted_by = case[6]

    status_class = "status-found" if status == "F" else "status-missing"
    status_text = "Found" if status == "F" else "Not Found"

    col_img, col_info = st.columns([1, 3])

    with col_img:
        try:
            st.image(f"./resources/{case_id}.jpg", use_container_width=True)
        except:
            st.markdown('<div style="height:100px; border-radius:12px; background:rgba(128,128,128,0.08); display:flex; align-items:center; justify-content:center; font-size:1.5rem; opacity:0.3;">📷</div>', unsafe_allow_html=True)

    with col_info:
        st.markdown(f'''
        <div class="case-card">
            <span class="status-chip {status_class}">{status_text}</span>
            <div class="case-name">Public Submission</div>
            <div class="case-meta">
                📍 {location} &nbsp;·&nbsp; 📱 {mobile}<br>
                By: {submitted_by} &nbsp;·&nbsp; {submitted_on}
            </div>
        </div>
        ''', unsafe_allow_html=True)


# ── Header ───────────────────────────────────────────────────────────────────
st.markdown('<div class="page-tag">Cases</div>', unsafe_allow_html=True)
st.markdown('<p class="page-title">All Cases</p>', unsafe_allow_html=True)
st.markdown('<p class="page-desc">Browse and filter registered and public cases.</p>', unsafe_allow_html=True)

# ── Filters ──────────────────────────────────────────────────────────────────
col_filter, col_date, _ = st.columns([1.5, 1.5, 2])
status = col_filter.selectbox(
    "Filter by",
    options=["All", "Not Found", "Found", "Public Cases"],
    label_visibility="collapsed",
)
date = col_date.date_input("Date", label_visibility="collapsed")

st.markdown('<div class="minimal-divider"></div>', unsafe_allow_html=True)

# ── Cases List ───────────────────────────────────────────────────────────────
if status == "Public Cases":
    cases = db_queries.fetch_public_cases(False, status)
    st.markdown(f'<p class="case-count">{len(cases)} public submissions</p>', unsafe_allow_html=True)
    if not cases:
        st.markdown('<div class="empty-state"><p>📭</p>No public submissions yet.</div>', unsafe_allow_html=True)
    for case in cases:
        render_public_case(case)
else:
    cases = db_queries.fetch_registered_cases(user, status)
    st.markdown(f'<p class="case-count">{len(cases)} registered cases</p>', unsafe_allow_html=True)
    if not cases:
        st.markdown('<div class="empty-state"><p>📭</p>No cases found.</div>', unsafe_allow_html=True)
    for case in cases:
        render_registered_case(case)
