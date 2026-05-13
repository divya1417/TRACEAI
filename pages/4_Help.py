import streamlit as st

# ── Page Config ──────────────────────────────────────────────────────────────
st.set_page_config(page_title="Help · TraceAI", page_icon="◎", layout="wide")

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

    .faq-q {
        font-size: 1rem; font-weight: 600; margin-bottom: 4px;
    }
    .faq-a {
        font-size: 0.9rem; font-weight: 300; opacity: 0.6; line-height: 1.7;
        margin-bottom: 1.2rem;
    }

    .step-card {
        border: 1px solid rgba(128,128,128,0.1);
        border-radius: 14px;
        padding: 1.2rem;
        text-align: center;
        transition: all 0.2s ease;
    }
    .step-card:hover {
        transform: translateY(-4px);
        border-color: rgba(102,126,234,0.3);
        box-shadow: 0 16px 48px rgba(102,126,234,0.08);
    }
    .step-num {
        font-size: 1.8rem; font-weight: 700;
        background: linear-gradient(135deg, #667eea, #764ba2);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    }
    .step-label {
        font-size: 0.85rem; font-weight: 500; margin-top: 4px;
    }
    .step-desc {
        font-size: 0.78rem; opacity: 0.45; font-weight: 300; margin-top: 2px;
    }

    .section-label {
        font-size: 0.7rem; text-transform: uppercase; letter-spacing: 2px;
        opacity: 0.4; font-weight: 600; margin-bottom: 0.5rem; margin-top: 1.5rem;
    }

    .about-text { font-size: 0.9rem; font-weight: 300; opacity: 0.55; line-height: 1.8; }

    /* Tech stack cards */
    .tech-card {
        border: 1px solid rgba(128,128,128,0.08);
        border-radius: 14px; padding: 1rem;
        text-align: center; transition: all 0.2s ease;
    }
    .tech-card:hover { transform: translateY(-3px); border-color: rgba(102,126,234,0.2); }
    .tech-name { font-size: 0.9rem; font-weight: 600; margin-top: 0.3rem; }
    .tech-role { font-size: 0.72rem; opacity: 0.4; font-weight: 300; }
</style>
""", unsafe_allow_html=True)


# ── Header ───────────────────────────────────────────────────────────────────
st.markdown('<div class="page-tag">Help</div>', unsafe_allow_html=True)
st.markdown('<p class="page-title">Help & About</p>', unsafe_allow_html=True)
st.markdown('<p class="page-desc">How this system works and frequently asked questions.</p>', unsafe_allow_html=True)


# ── How It Works ─────────────────────────────────────────────────────────────
st.markdown('<p class="section-label">How it works</p>', unsafe_allow_html=True)

c1, c2, c3, c4 = st.columns(4)
with c1:
    st.markdown('''
    <div class="step-card">
        <div class="step-num">01</div>
        <div class="step-label">Register a Case</div>
        <div class="step-desc">Upload a photo and fill in person details.</div>
    </div>
    ''', unsafe_allow_html=True)
with c2:
    st.markdown('''
    <div class="step-card">
        <div class="step-num">02</div>
        <div class="step-label">Public Submissions</div>
        <div class="step-desc">Anyone can submit a sighting via the mobile form.</div>
    </div>
    ''', unsafe_allow_html=True)
with c3:
    st.markdown('''
    <div class="step-card">
        <div class="step-num">03</div>
        <div class="step-label">AI Matching</div>
        <div class="step-desc">Deep learning embeddings + cosine similarity for frontal & side profile matching.</div>
    </div>
    ''', unsafe_allow_html=True)
with c4:
    st.markdown('''
    <div class="step-card">
        <div class="step-num">04</div>
        <div class="step-label">Found!</div>
        <div class="step-desc">Matched cases are flagged and contact info is shared.</div>
    </div>
    ''', unsafe_allow_html=True)

st.markdown('<div class="minimal-divider"></div>', unsafe_allow_html=True)


# ── FAQ ──────────────────────────────────────────────────────────────────────
st.markdown('<p class="section-label">Frequently asked questions</p>', unsafe_allow_html=True)

faqs = [
    (
        "What kind of photo should I upload?",
        "A clear photo with good lighting. The system supports both front-facing AND side profile images. It uses MediaPipe for frontal faces (468 landmarks) and DeepFace Facenet512 for pose-invariant 512-d embeddings that handle side profiles - ideal for CCTV footage."
    ),
    (
        "How does matching work?",
        "When you click 'Run Matching', the system uses deep learning face embeddings (512-d vectors from Facenet512) and computes cosine similarity between public submissions and registered cases. This approach works across different face angles including side profiles. For older cases without embeddings, it falls back to KNN on MediaPipe landmarks."
    ),
    (
        "Can anyone submit a sighting?",
        "Yes. The public sighting form (mobile app) does not require login. Anyone who spots a person can upload a photo, enter the location, and submit."
    ),
    (
        "What happens when a match is found?",
        "The registered case status changes to 'Found' and the public submission details (location, submitter contact) are linked to the case for follow-up."
    ),
    (
        "Is the data private?",
        "All data is stored locally in a SQLite database. Photos are saved in the resources folder. The system is designed for local / on-premise use."
    ),
]

for q, a in faqs:
    st.markdown(f'<p class="faq-q">{q}</p>', unsafe_allow_html=True)
    st.markdown(f'<p class="faq-a">{a}</p>', unsafe_allow_html=True)

st.markdown('<div class="minimal-divider"></div>', unsafe_allow_html=True)


# ── Tech Stack ───────────────────────────────────────────────────────────────
st.markdown('<p class="section-label">Tech Stack</p>', unsafe_allow_html=True)

t1, t2, t3, t4, t5 = st.columns(5)
with t1:
    st.markdown('''
    <div class="tech-card">
        <div style="font-size:1.8rem;">🐍</div>
        <div class="tech-name">Python</div>
        <div class="tech-role">Core Language</div>
    </div>
    ''', unsafe_allow_html=True)
with t2:
    st.markdown('''
    <div class="tech-card">
        <div style="font-size:1.8rem;">🎯</div>
        <div class="tech-name">Streamlit</div>
        <div class="tech-role">Web Framework</div>
    </div>
    ''', unsafe_allow_html=True)
with t3:
    st.markdown('''
    <div class="tech-card">
        <div style="font-size:1.8rem;">🧬</div>
        <div class="tech-name">MediaPipe</div>
        <div class="tech-role">Face Landmarks</div>
    </div>
    ''', unsafe_allow_html=True)
with t4:
    st.markdown('''
    <div class="tech-card">
        <div style="font-size:1.8rem;">🧠</div>
        <div class="tech-name">DeepFace</div>
        <div class="tech-role">Face Embeddings</div>
    </div>
    ''', unsafe_allow_html=True)
with t5:
    st.markdown('''
    <div class="tech-card">
        <div style="font-size:1.8rem;">🗄️</div>
        <div class="tech-name">SQLite</div>
        <div class="tech-role">Database</div>
    </div>
    ''', unsafe_allow_html=True)

st.markdown('<div class="minimal-divider"></div>', unsafe_allow_html=True)


# ── About ────────────────────────────────────────────────────────────────────
st.markdown('<p class="section-label">About TraceAI</p>', unsafe_allow_html=True)
st.markdown('''
<p class="about-text">
    <strong>TraceAI</strong> is an AI-powered missing person identification system built as a capstone project.
    It uses <strong>MediaPipe Face Mesh</strong> for frontal facial landmark extraction,
    <strong>DeepFace (Facenet512)</strong> for pose-invariant face embeddings that handle side profiles (e.g. CCTV footage),
    and <strong>cosine similarity</strong> for identity matching. The frontend is built with <strong>Streamlit</strong>
    and the database layer uses <strong>SQLModel</strong> (SQLite).<br><br>
    Built with ❤️ by the project team.
</p>
''', unsafe_allow_html=True)