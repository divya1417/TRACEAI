import yaml
import streamlit as st
from yaml import SafeLoader
import streamlit_authenticator as stauth

from pages.helper import db_queries

# ── Page Config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="TraceAI - Find Missing People with AI",
    page_icon="◎",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── CSS ── Startup Landing + Dashboard ───────────────────────────────────────
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap');

    .stApp { font-family: 'Inter', sans-serif; }
    #MainMenu, footer, header { visibility: hidden; }
    /* Sidebar always visible, no collapse */
    [data-testid="collapsedControl"] { display: none !important; }
    section[data-testid="stSidebar"] {
        min-width: 260px !important;
        max-width: 260px !important;
        transform: none !important;
        position: relative !important;
    }
    section[data-testid="stSidebar"] > div { padding-top: 1.5rem; }

    /* ── LANDING PAGE ────────────────────────────────────────────────── */

    /* Animated gradient background blob */
    .landing-blob {
        position: fixed; top: -40%; right: -20%;
        width: 600px; height: 600px;
        background: radial-gradient(circle, rgba(102,126,234,0.08) 0%, transparent 70%);
        border-radius: 50%; pointer-events: none;
        animation: blobFloat 8s ease-in-out infinite;
    }
    .landing-blob-2 {
        position: fixed; bottom: -30%; left: -15%;
        width: 500px; height: 500px;
        background: radial-gradient(circle, rgba(118,75,162,0.06) 0%, transparent 70%);
        border-radius: 50%; pointer-events: none;
        animation: blobFloat 10s ease-in-out infinite reverse;
    }
    @keyframes blobFloat {
        0%, 100% { transform: translate(0, 0) scale(1); }
        50% { transform: translate(30px, -20px) scale(1.05); }
    }

    /* Nav bar */
    .landing-nav {
        display: flex; align-items: center; justify-content: space-between;
        padding: 0.5rem 0; margin-bottom: 3rem;
    }
    .nav-logo {
        font-size: 1.4rem; font-weight: 800; letter-spacing: -1px;
    }
    .nav-logo span { opacity: 0.35; }

    /* Hero */
    .landing-hero {
        text-align: center;
        padding: 2rem 0 3rem;
        position: relative; z-index: 1;
    }
    .hero-pill {
        display: inline-block; padding: 6px 20px; border-radius: 24px;
        font-size: 0.78rem; font-weight: 500; letter-spacing: 0.8px;
        text-transform: uppercase;
        background: linear-gradient(135deg, rgba(102,126,234,0.15), rgba(118,75,162,0.15));
        color: #667eea; margin-bottom: 1.5rem;
        animation: fadeInUp 0.6s ease-out;
    }
    .hero-headline {
        font-size: 4rem; font-weight: 900; letter-spacing: -2.5px;
        line-height: 1.05; margin-bottom: 1rem;
        animation: fadeInUp 0.7s ease-out;
    }
    .hero-headline .gradient-text {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 50%, #f093fb 100%);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    }
    .hero-sub {
        font-size: 1.15rem; font-weight: 300; opacity: 0.5;
        max-width: 520px; margin: 0 auto 2.5rem; line-height: 1.6;
        animation: fadeInUp 0.8s ease-out;
    }

    @keyframes fadeInUp {
        from { opacity: 0; transform: translateY(20px); }
        to { opacity: 1; transform: translateY(0); }
    }

    /* Feature cards */
    .feature-card {
        border: 1px solid rgba(128,128,128,0.08);
        border-radius: 20px; padding: 2rem 1.5rem;
        text-align: center; transition: all 0.3s ease;
        backdrop-filter: blur(10px);
        animation: fadeInUp 0.9s ease-out;
    }
    .feature-card:hover {
        transform: translateY(-4px);
        border-color: rgba(102,126,234,0.25);
        box-shadow: 0 20px 60px rgba(102,126,234,0.08);
    }
    .feature-icon {
        font-size: 2.2rem; margin-bottom: 0.8rem;
    }
    .feature-title {
        font-size: 1rem; font-weight: 600; margin-bottom: 0.4rem;
    }
    .feature-desc {
        font-size: 0.82rem; opacity: 0.45; font-weight: 300;
        line-height: 1.5;
    }

    /* Stats bar */
    .stats-bar {
        display: flex; justify-content: center; gap: 4rem;
        padding: 2rem 0; margin: 2rem 0;
        animation: fadeInUp 1s ease-out;
    }
    .stat-item { text-align: center; }
    .stat-number {
        font-size: 2rem; font-weight: 800;
        background: linear-gradient(135deg, #667eea, #764ba2);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    }
    .stat-label {
        font-size: 0.72rem; text-transform: uppercase;
        letter-spacing: 1.5px; opacity: 0.4; font-weight: 500;
    }

    /* How it works section */
    .how-section-title {
        text-align: center; font-size: 0.7rem; text-transform: uppercase;
        letter-spacing: 3px; opacity: 0.3; font-weight: 600;
        margin-top: 2rem; margin-bottom: 1.5rem;
    }
    .how-step {
        border: 1px solid rgba(128,128,128,0.08);
        border-radius: 16px; padding: 1.5rem;
        text-align: center;
        transition: all 0.2s ease;
    }
    .how-step:hover { border-color: rgba(102,126,234,0.2); }
    .how-num {
        font-size: 2rem; font-weight: 800;
        background: linear-gradient(135deg, #667eea, #764ba2);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
        margin-bottom: 0.3rem;
    }
    .how-label { font-size: 0.85rem; font-weight: 600; margin-bottom: 0.2rem; }
    .how-desc { font-size: 0.75rem; opacity: 0.4; font-weight: 300; }

    /* CTA section */
    .cta-section {
        text-align: center; padding: 2rem 0 1rem;
        animation: fadeInUp 1.1s ease-out;
    }
    .cta-text {
        font-size: 1.5rem; font-weight: 700; letter-spacing: -0.5px;
        margin-bottom: 0.5rem;
    }
    .cta-sub {
        font-size: 0.85rem; opacity: 0.4; font-weight: 300; margin-bottom: 1.5rem;
    }

    /* Footer */
    .landing-footer {
        text-align: center; padding: 2rem 0; margin-top: 2rem;
        font-size: 0.75rem; opacity: 0.25; font-weight: 300;
    }

    /* ── DIVIDER ─────────────────────────────────────────────────────── */
    .minimal-divider {
        height: 1px; border: none;
        background: linear-gradient(90deg, transparent, rgba(128,128,128,0.15), transparent);
        margin: 2rem 0;
    }

    /* ── DASHBOARD (post-login) ──────────────────────────────────────── */
    .hero-tag {
        display: inline-block; padding: 4px 14px; border-radius: 20px;
        font-size: 0.75rem; font-weight: 500; letter-spacing: 1px;
        text-transform: uppercase;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white; margin-bottom: 0.5rem;
    }
    .hero-title {
        font-size: 2.5rem; font-weight: 700; letter-spacing: -1.5px;
        margin-bottom: 0; line-height: 1.1;
    }
    .metric-card {
        border-radius: 16px; padding: 1.5rem; text-align: center;
        border: 1px solid rgba(128,128,128,0.12);
        backdrop-filter: blur(10px); transition: all 0.2s ease;
    }
    .metric-card:hover { transform: translateY(-2px); border-color: rgba(102,126,234,0.25); }
    .metric-number {
        font-size: 2.8rem; font-weight: 700; line-height: 1; margin: 0.5rem 0;
    }
    .metric-label {
        font-size: 0.8rem; text-transform: uppercase;
        letter-spacing: 1.5px; opacity: 0.5; font-weight: 500;
    }
    .metric-found .metric-number { color: #10b981; }
    .metric-missing .metric-number { color: #f59e0b; }

    .user-chip {
        display: inline-flex; align-items: center; gap: 8px;
        padding: 6px 16px; border-radius: 24px;
        font-size: 0.85rem; font-weight: 500;
        border: 1px solid rgba(128,128,128,0.15);
        margin-right: 8px; margin-bottom: 8px;
    }
    .quick-actions-title {
        font-size: 0.75rem; text-transform: uppercase;
        letter-spacing: 2px; opacity: 0.4; font-weight: 600; margin-bottom: 1rem;
    }

    /* Action cards (dashboard) */
    .action-card {
        border: 1px solid rgba(128,128,128,0.1);
        border-radius: 16px; padding: 1.2rem;
        text-align: center; transition: all 0.2s ease;
    }
    .action-card:hover {
        transform: translateY(-2px);
        border-color: rgba(102,126,234,0.3);
        box-shadow: 0 8px 30px rgba(102,126,234,0.06);
    }
    .action-icon { font-size: 1.8rem; margin-bottom: 0.3rem; }
    .action-label { font-size: 0.85rem; font-weight: 500; }
    .action-desc { font-size: 0.72rem; opacity: 0.4; font-weight: 300; }
</style>
""", unsafe_allow_html=True)


# ── Session State ────────────────────────────────────────────────────────────
if "login_status" not in st.session_state:
    st.session_state["login_status"] = False
if "show_login" not in st.session_state:
    st.session_state["show_login"] = False

try:
    with open("login_config.yml") as file:
        config = yaml.load(file, Loader=SafeLoader)
except FileNotFoundError:
    st.error("Config file not found")
    st.stop()

authenticator = stauth.Authenticate(
    config["credentials"],
    config["cookie"]["name"],
    config["cookie"]["key"],
    config["cookie"]["expiry_days"],
)


# ══════════════════════════════════════════════════════════════════════════════
#  SIDEBAR - always visible on every state
# ══════════════════════════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown("### ◎ TraceAI")
    st.markdown('<div class="minimal-divider"></div>', unsafe_allow_html=True)

    if st.session_state.get("authentication_status"):
        user_info_sb = config["credentials"]["usernames"][st.session_state["username"]]
        st.markdown(f'<span class="user-chip">👤 {user_info_sb["name"]}</span>', unsafe_allow_html=True)
        st.markdown(f'<span class="user-chip">🏷 {user_info_sb.get("role", "User")}</span>', unsafe_allow_html=True)
        st.markdown('<div class="minimal-divider"></div>', unsafe_allow_html=True)
        
        # Admin Utils
        with st.expander("🛠 System Tools"):
            if st.button("🚨 Reset Database", use_container_width=True, type="secondary"):
                if db_queries.reset_database():
                    st.success("Database has been reset!")
                    st.rerun()
                else:
                    st.error("Failed to reset database.")

    # st.page_link("Home.py", label="🏠 Home", use_container_width=True)
    # st.page_link("pages/1_Register New Case.py", label="📋 Register Case", use_container_width=True)
    # st.page_link("pages/2_All Cases.py", label="🔍 All Cases", use_container_width=True)
    # st.page_link("pages/3_Match Cases.py", label="🧠 Match Cases", use_container_width=True)
    # st.page_link("pages/4_Help.py", label="❓ Help", use_container_width=True)

    if st.session_state.get("authentication_status"):
        st.markdown('<div class="minimal-divider"></div>', unsafe_allow_html=True)
        authenticator.logout("↩ Logout", "sidebar")
    else:
        st.markdown('<div class="minimal-divider"></div>', unsafe_allow_html=True)
        st.markdown('<p style="font-size:0.75rem; opacity:0.4; text-align:center;">Login for full access</p>', unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
#  LANDING PAGE (shown when NOT logged in)
# ══════════════════════════════════════════════════════════════════════════════
if not st.session_state.get("authentication_status"):

    # ── Floating blobs ───────────────────────────────────────────────────
    st.markdown('<div class="landing-blob"></div><div class="landing-blob-2"></div>', unsafe_allow_html=True)

    # ── Nav ──────────────────────────────────────────────────────────────
    st.markdown('''
    <div class="landing-nav">
        <div class="nav-logo">◎ Trace<span>AI</span></div>
    </div>
    ''', unsafe_allow_html=True)

    # ── Hero ─────────────────────────────────────────────────────────────
    st.markdown('''
    <div class="landing-hero">
        <div class="hero-pill">AI-Powered Missing Person Identification</div>
        <div class="hero-headline">
            Find missing people<br>
            <span class="gradient-text">with facial AI.</span>
        </div>
        <div class="hero-sub">
            TraceAI uses facial landmark recognition and machine learning
            to match missing persons with public sightings - in real time.
        </div>
    </div>
    ''', unsafe_allow_html=True)

    # ── CTA buttons ──────────────────────────────────────────────────────
    _, btn_col1, btn_col2, _ = st.columns([2, 1.2, 1.2, 2])
    with btn_col1:
        if st.button("Admin Login  →", type="primary", use_container_width=True):
            st.session_state["show_login"] = True
            st.rerun()
    with btn_col2:
        st.link_button("📸 Report Sighting", "http://localhost:8502", use_container_width=True)

    st.markdown('<div class="minimal-divider"></div>', unsafe_allow_html=True)

    # ── Stats bar ────────────────────────────────────────────────────────
    st.markdown('''
    <div class="stats-bar">
        <div class="stat-item">
            <div class="stat-number">468</div>
            <div class="stat-label">Face Points</div>
        </div>
        <div class="stat-item">
            <div class="stat-number">1,404</div>
            <div class="stat-label">Features</div>
        </div>
        <div class="stat-item">
            <div class="stat-number">&lt;2s</div>
            <div class="stat-label">Match Time</div>
        </div>
        <div class="stat-item">
            <div class="stat-number">24/7</div>
            <div class="stat-label">Availability</div>
        </div>
    </div>
    ''', unsafe_allow_html=True)

    st.markdown('<div class="minimal-divider"></div>', unsafe_allow_html=True)

    # ── Feature cards ────────────────────────────────────────────────────
    f1, f2, f3 = st.columns(3)
    with f1:
        st.markdown('''
        <div class="feature-card">
            <div class="feature-icon">🧬</div>
            <div class="feature-title">Face Mesh Detection</div>
            <div class="feature-desc">
                MediaPipe extracts 468 3D facial landmarks from any photo
                - creating a unique biometric signature.
            </div>
        </div>
        ''', unsafe_allow_html=True)
    with f2:
        st.markdown('''
        <div class="feature-card">
            <div class="feature-icon">🧠</div>
            <div class="feature-title">KNN Matching</div>
            <div class="feature-desc">
                A K-Nearest Neighbors classifier compares face signatures
                to identify potential matches instantly.
            </div>
        </div>
        ''', unsafe_allow_html=True)
    with f3:
        st.markdown('''
        <div class="feature-card">
            <div class="feature-icon">📱</div>
            <div class="feature-title">Public Reporting</div>
            <div class="feature-desc">
                Anyone can submit a sighting via the mobile form
                - no login required. Just snap and submit.
            </div>
        </div>
        ''', unsafe_allow_html=True)

    st.markdown('<div class="minimal-divider"></div>', unsafe_allow_html=True)

    # ── How it works ─────────────────────────────────────────────────────
    st.markdown('<p class="how-section-title">How it works</p>', unsafe_allow_html=True)

    h1, h2, h3, h4 = st.columns(4)
    with h1:
        st.markdown('''
        <div class="how-step">
            <div class="how-num">01</div>
            <div class="how-label">Register</div>
            <div class="how-desc">Upload a photo of the missing person.</div>
        </div>
        ''', unsafe_allow_html=True)
    with h2:
        st.markdown('''
        <div class="how-step">
            <div class="how-num">02</div>
            <div class="how-label">Extract</div>
            <div class="how-desc">AI extracts 468 facial landmarks.</div>
        </div>
        ''', unsafe_allow_html=True)
    with h3:
        st.markdown('''
        <div class="how-step">
            <div class="how-num">03</div>
            <div class="how-label">Match</div>
            <div class="how-desc">KNN model compares with public sightings.</div>
        </div>
        ''', unsafe_allow_html=True)
    with h4:
        st.markdown('''
        <div class="how-step">
            <div class="how-num">04</div>
            <div class="how-label">Found</div>
            <div class="how-desc">Match alert with location and contact info.</div>
        </div>
        ''', unsafe_allow_html=True)

    st.markdown('<div class="minimal-divider"></div>', unsafe_allow_html=True)

    # ── Login section (toggled by button) ────────────────────────────────
    if st.session_state.get("show_login"):
        st.markdown('<div id="login-anchor"></div>', unsafe_allow_html=True)
        st.markdown('''
        <div class="cta-section">
            <div class="cta-text">Admin Login</div>
            <div class="cta-sub">Authorized personnel only.</div>
        </div>
        ''', unsafe_allow_html=True)

        _, login_col, _ = st.columns([1.5, 1, 1.5])
        with login_col:
            authenticator.login(location="main")

        # Auto-scroll to login form
        st.markdown('''
        <script>
            const anchor = document.getElementById('login-anchor');
            if (anchor) { anchor.scrollIntoView({ behavior: 'smooth', block: 'center' }); }
        </script>
        ''', unsafe_allow_html=True)
        # Fallback: Streamlit components approach
        import streamlit.components.v1 as components
        components.html("""
        <script>
            window.parent.document.querySelector('[id="login-anchor"]')
                ?.scrollIntoView({ behavior: 'smooth', block: 'center' });
        </script>
        """, height=0)
    else:
        # Still need to call login() for cookie auth - hide it in collapsed sidebar
        authenticator.login(location="sidebar")

    # ── Footer ───────────────────────────────────────────────────────────
    st.markdown('''
    <div class="landing-footer">
        TraceAI · Built with Streamlit, MediaPipe & scikit-learn<br>
        College Project · 2026
    </div>
    ''', unsafe_allow_html=True)

    if st.session_state.get("authentication_status") is False:
        st.error("Incorrect credentials. Please try again.")

    if st.session_state.get("authentication_status") is None:
        st.session_state["login_status"] = False


# ══════════════════════════════════════════════════════════════════════════════
#  DASHBOARD (shown AFTER login)
# ══════════════════════════════════════════════════════════════════════════════
if st.session_state.get("authentication_status"):
    st.session_state["login_status"] = True
    user_info = config["credentials"]["usernames"][st.session_state["username"]]
    st.session_state["user"] = user_info["name"]

    # ── Header ───────────────────────────────────────────────────────────
    st.markdown('<div class="hero-tag">Dashboard</div>', unsafe_allow_html=True)
    st.markdown(f'<p class="hero-title">Welcome back, <span style="opacity:0.4">{user_info["name"].split()[0]}</span></p>', unsafe_allow_html=True)
    st.markdown('<div class="minimal-divider"></div>', unsafe_allow_html=True)

    # ── Metrics ──────────────────────────────────────────────────────────
    found = db_queries.get_registered_cases_count(user_info["name"], "F")
    not_found = db_queries.get_registered_cases_count(user_info["name"], "NF")

    m1, m2, m3 = st.columns(3)
    with m1:
        st.markdown(f'''
        <div class="metric-card metric-found">
            <div class="metric-label">Found</div>
            <div class="metric-number">{len(found)}</div>
        </div>
        ''', unsafe_allow_html=True)
    with m2:
        st.markdown(f'''
        <div class="metric-card metric-missing">
            <div class="metric-label">Missing</div>
            <div class="metric-number">{len(not_found)}</div>
        </div>
        ''', unsafe_allow_html=True)
    with m3:
        st.markdown(f'''
        <div class="metric-card">
            <div class="metric-label">Total Cases</div>
            <div class="metric-number">{len(found) + len(not_found)}</div>
        </div>
        ''', unsafe_allow_html=True)

    st.markdown('<div class="minimal-divider"></div>', unsafe_allow_html=True)

    # ── Quick Actions ────────────────────────────────────────────────────
    st.markdown('<p class="quick-actions-title">Quick Actions</p>', unsafe_allow_html=True)

    qa1, qa2, qa3, qa4 = st.columns(4)
    with qa1:
        st.markdown('''
        <div class="action-card">
            <div class="action-icon">📋</div>
            <div class="action-label">Register Case</div>
            <div class="action-desc">File a new missing person report</div>
        </div>
        ''', unsafe_allow_html=True)
        st.page_link("pages/1_Register New Case.py", label="Open →", use_container_width=True)
    with qa2:
        st.markdown('''
        <div class="action-card">
            <div class="action-icon">🔍</div>
            <div class="action-label">All Cases</div>
            <div class="action-desc">Browse registered & public cases</div>
        </div>
        ''', unsafe_allow_html=True)
        st.page_link("pages/2_All Cases.py", label="Open →", use_container_width=True)
    with qa3:
        st.markdown('''
        <div class="action-card">
            <div class="action-icon">🧠</div>
            <div class="action-label">Match</div>
            <div class="action-desc">Train model & find matches</div>
        </div>
        ''', unsafe_allow_html=True)
        st.page_link("pages/3_Match Cases.py", label="Open →", use_container_width=True)
    with qa4:
        st.markdown('''
        <div class="action-card">
            <div class="action-icon">📹</div>
            <div class="action-label">CCTV</div>
            <div class="action-desc">Automate video feeds</div>
        </div>
        ''', unsafe_allow_html=True)
        st.page_link("pages/5_CCTV Pipeline.py", label="Open →", use_container_width=True)
