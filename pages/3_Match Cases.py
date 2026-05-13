import streamlit as st
from pages.helper import db_queries, match_algo, train_model

# ── Page Config ──────────────────────────────────────────────────────────────
st.set_page_config(page_title="Match · TraceAI", page_icon="◎", layout="wide")

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
    @keyframes pulseGlow {
        0%, 100% { box-shadow: 0 0 0 0 rgba(16,185,129,0.15); }
        50% { box-shadow: 0 0 20px 4px rgba(16,185,129,0.1); }
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

    /* Match card */
    .match-card {
        border: 1px solid rgba(16,185,129,0.2);
        border-radius: 16px;
        padding: 1.2rem;
        margin-bottom: 1rem;
        background: rgba(16,185,129,0.03);
        transition: all 0.2s ease;
    }
    .match-card:hover {
        transform: translateY(-3px);
        border-color: rgba(16,185,129,0.4);
        box-shadow: 0 12px 40px rgba(16,185,129,0.08);
    }
    .match-card { animation: pulseGlow 3s ease-in-out infinite; }
    .match-name { font-size: 1.1rem; font-weight: 600; margin-bottom: 2px; }
    .match-meta { font-size: 0.8rem; opacity: 0.5; line-height: 1.6; }

    .match-badge {
        display: inline-block; padding: 3px 12px; border-radius: 12px;
        font-size: 0.7rem; font-weight: 600; letter-spacing: 0.5px;
        text-transform: uppercase;
        background: rgba(16,185,129,0.15); color: #10b981;
    }

    .empty-state {
        text-align: center; padding: 4rem 2rem; opacity: 0.3;
    }

    .run-info {
        font-size: 0.8rem; opacity: 0.4; font-weight: 500;
        letter-spacing: 1px; text-transform: uppercase;
    }

    .step-item {
        padding: 0.5rem 0;
        font-size: 0.85rem;
        opacity: 0.5;
    }
    .step-done { opacity: 0.9; }
    .step-done::before { content: "✓ "; color: #10b981; font-weight: 700; }
    .step-active::before { content: "◌ "; color: #667eea; font-weight: 700; }
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


# ── Match result viewer ──────────────────────────────────────────────────────
def render_match(registered_case_id, public_case_id):
    try:
        case_details = db_queries.get_registered_case_detail(registered_case_id)[0]
        # Registered case details
        name, mobile, age, last_seen, birth_marks = case_details

        # Public submission details (NEW)
        pub_details = db_queries.get_public_case_detail(public_case_id)[0]
        pub_location, pub_submitted_by, pub_mobile, pub_birth_marks = pub_details

        db_queries.update_found_status(registered_case_id, public_case_id)

        col_img, col_info = st.columns([1, 3])

        with col_img:
            try:
                st.image(f"./resources/{registered_case_id}.jpg", use_container_width=True)
            except:
                st.markdown('<div style="height:100px; border-radius:12px; background:rgba(128,128,128,0.08); display:flex; align-items:center; justify-content:center; font-size:1.5rem; opacity:0.3;">📷</div>', unsafe_allow_html=True)

        with col_info:
            st.markdown(f'''
            <div class="match-card">
                <span class="match-badge">Match Found</span>
                <div class="match-name">{name}</div>
                <div class="match-meta">
                    Age: {age} &nbsp;·&nbsp; Last seen: {last_seen}<br>
                    📱 Contact: {mobile} &nbsp;·&nbsp; Marks: {birth_marks}
                </div>
                <div style="margin-top:1rem; padding-top:1rem; border-top:1px solid rgba(16,185,129,0.2); font-size:0.85rem;">
                    <strong style="color:#10b981; font-size:0.75rem; text-transform:uppercase; letter-spacing:1px;">Sighting Details</strong><br>
                    <div style="opacity:0.8; margin-top:0.3rem;">
                        📍 <strong>Location:</strong> {pub_location}<br>
                        👤 <strong>Submitted by:</strong> {pub_submitted_by}<br>
                        📞 <strong>Reporter Mobile:</strong> {pub_mobile}
                    </div>
                </div>
            </div>
            ''', unsafe_allow_html=True)

    except Exception as e:
        st.error(f"Could not display match: {str(e)}")


# ── Header ───────────────────────────────────────────────────────────────────
st.markdown('<div class="page-tag">Match</div>', unsafe_allow_html=True)
st.markdown('<p class="page-title">Match Cases</p>', unsafe_allow_html=True)
st.markdown('<p class="page-desc">Train the model and find matches between registered and public cases.</p>', unsafe_allow_html=True)

# ── Controls ─────────────────────────────────────────────────────────────────
col_btn, col_info, _ = st.columns([1, 2, 2])
run_match = col_btn.button("⟳ Run Matching", type="primary", use_container_width=True)

st.markdown('<div class="minimal-divider"></div>', unsafe_allow_html=True)

# ── Run matching pipeline ────────────────────────────────────────────────────
if run_match:
    progress = st.empty()
    results_area = st.container()

    # Step 1 - Train
    progress.markdown('<div class="step-item step-active">Training model on registered cases…</div>', unsafe_allow_html=True)
    with st.spinner(""):
        result = train_model.train(user)
    progress.markdown('<div class="step-item step-done">Model trained</div>', unsafe_allow_html=True)

    # Step 2 - Match
    progress2 = st.empty()
    progress2.markdown('<div class="step-item step-active">Running match algorithm…</div>', unsafe_allow_html=True)
    with st.spinner(""):
        matched_ids = match_algo.match()
    progress2.markdown('<div class="step-item step-done">Matching complete</div>', unsafe_allow_html=True)

    st.markdown('<div class="minimal-divider"></div>', unsafe_allow_html=True)

    # Step 3 - Display results
    if matched_ids.get("status") and matched_ids.get("result"):
        count = len(matched_ids["result"])
        st.markdown(f'<p class="run-info">{count} match{"es" if count != 1 else ""} found</p>', unsafe_allow_html=True)
        for matched_id, submitted_case_id in matched_ids["result"].items():
            render_match(matched_id, submitted_case_id[0])
    else:
        st.markdown("""
        <div class="empty-state">
            <p style="font-size:2rem;">🔍</p>
            <p style="font-weight:300; font-size:0.95rem;">No matches found this round.<br>
            <span style="font-size:0.8rem;">Try again after new public submissions come in.</span></p>
        </div>
        """, unsafe_allow_html=True)
else:
    st.markdown("""
    <div class="empty-state">
        <p style="font-size:2.5rem;">◎</p>
        <p style="font-weight:300; font-size:0.95rem;">Hit <strong>Run Matching</strong> to train the model<br>and scan for potential matches.</p>
    </div>
    """, unsafe_allow_html=True)
