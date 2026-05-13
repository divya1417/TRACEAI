import uuid
import numpy as np
import streamlit as st
import json

from pages.helper.data_models import RegisteredCases
from pages.helper import db_queries
from pages.helper.utils import image_obj_to_numpy, extract_face_mesh_landmarks, extract_face_embedding

# ── Page Config ──────────────────────────────────────────────────────────────
st.set_page_config(page_title="Register Case · TraceAI", page_icon="◎", layout="centered")

# ── Shared CSS ───────────────────────────────────────────────────────────────
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

    /* Animations */
    @keyframes fadeInUp {
        from { opacity: 0; transform: translateY(16px); }
        to { opacity: 1; transform: translateY(0); }
    }
    .stApp > div { animation: fadeInUp 0.5s ease-out; }

    .page-tag {
        display: inline-block;
        padding: 4px 14px;
        border-radius: 20px;
        font-size: 0.75rem;
        font-weight: 500;
        letter-spacing: 1px;
        text-transform: uppercase;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        margin-bottom: 0.5rem;
    }
    .page-title {
        font-size: 2rem;
        font-weight: 700;
        letter-spacing: -1px;
        margin-bottom: 0.2rem;
    }
    .page-desc {
        font-size: 0.95rem;
        font-weight: 300;
        opacity: 0.5;
        margin-bottom: 1.5rem;
    }
    .minimal-divider {
        height: 1px;
        background: linear-gradient(90deg, transparent, rgba(128,128,128,0.2), transparent);
        margin: 1.5rem 0;
        border: none;
    }

    /* Upload area */
    .upload-zone {
        border: 2px dashed rgba(128,128,128,0.2);
        border-radius: 16px;
        padding: 2rem;
        text-align: center;
        transition: border-color 0.3s;
    }
    .upload-zone:hover { border-color: rgba(102,126,234,0.5); }

    .face-status {
        padding: 8px 16px;
        border-radius: 12px;
        font-size: 0.85rem;
        font-weight: 500;
        text-align: center;
        margin-top: 0.5rem;
    }
    .face-ok { background: rgba(16,185,129,0.1); color: #10b981; }
    .face-fail { background: rgba(239,68,68,0.1); color: #ef4444; }

    .section-label {
        font-size: 0.7rem;
        text-transform: uppercase;
        letter-spacing: 2px;
        opacity: 0.4;
        font-weight: 600;
        margin-bottom: 0.5rem;
        margin-top: 1rem;
    }
</style>
""", unsafe_allow_html=True)


# ── Auth Guard ───────────────────────────────────────────────────────────────
if "login_status" not in st.session_state or not st.session_state.get("login_status"):
    st.markdown("""
    <div style="text-align:center; padding:4rem 2rem;">
        <p style="font-size:2rem; font-weight:300; opacity:0.4;">🔒</p>
        <p style="font-weight:300; opacity:0.5;">Please login from the Home page to continue.</p>
    </div>
    """, unsafe_allow_html=True)
    st.stop()

user = st.session_state.user

# ── Header ───────────────────────────────────────────────────────────────────
st.markdown('<div class="page-tag">New Case</div>', unsafe_allow_html=True)
st.markdown('<p class="page-title">Register Missing Person</p>', unsafe_allow_html=True)
st.markdown('<p class="page-desc">Upload a clear photo and fill in the details below.</p>', unsafe_allow_html=True)
st.markdown('<div class="minimal-divider"></div>', unsafe_allow_html=True)

# ── Image Upload ─────────────────────────────────────────────────────────────
image_obj = None
face_mesh = None
face_embedding = None
unique_id = None

st.markdown('<p class="section-label">📸 Photo Upload</p>', unsafe_allow_html=True)

image_obj = st.file_uploader(
    "Upload a clear front-facing photo",
    type=["jpg", "jpeg", "png"],
    key="new_case",
    help="Ensure the face is clearly visible, well-lit, and front-facing.",
)

if image_obj:
    unique_id = str(uuid.uuid4())
    uploaded_file_path = "./resources/" + unique_id + ".jpg"
    with open(uploaded_file_path, "wb") as f:
        f.write(image_obj.read())

    col_img, col_status = st.columns([1, 1])
    with col_img:
        st.image(image_obj, caption="Uploaded Photo", use_container_width=True)

    with col_status:
        with st.spinner("Analyzing face..."):
            image_numpy = image_obj_to_numpy(image_obj)
            face_mesh = extract_face_mesh_landmarks(image_numpy)
            face_embedding = extract_face_embedding(image_numpy)

        if face_mesh and face_embedding:
            st.markdown('<div class="face-status face-ok">✓ Frontal face detected - full landmarks + embedding extracted</div>', unsafe_allow_html=True)
            st.markdown(f"""
            <div style="margin-top:1rem; font-size:0.8rem; opacity:0.5;">
                <div>Landmarks: <strong>468</strong></div>
                <div>Embedding: <strong>512-d</strong></div>
                <div>Profile: <strong>Frontal</strong></div>
            </div>
            """, unsafe_allow_html=True)
        elif face_mesh:
            st.markdown('<div class="face-status face-ok">✓ Frontal face detected - landmarks extracted</div>', unsafe_allow_html=True)
            st.markdown(f"""
            <div style="margin-top:1rem; font-size:0.8rem; opacity:0.5;">
                <div>Landmarks: <strong>468</strong></div>
                <div>Embedding: <strong>Failed</strong></div>
                <div>Profile: <strong>Frontal</strong></div>
            </div>
            """, unsafe_allow_html=True)
        elif face_embedding:
            st.markdown('<div class="face-status face-ok">✓ Side profile detected - embedding extracted</div>', unsafe_allow_html=True)
            st.markdown(f"""
            <div style="margin-top:1rem; font-size:0.8rem; opacity:0.5;">
                <div>Embedding: <strong>512-d</strong></div>
                <div>Profile: <strong>Side / Angled</strong></div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown('<div class="face-status face-fail">✗ No face detected - try another photo</div>', unsafe_allow_html=True)

st.markdown('<div class="minimal-divider"></div>', unsafe_allow_html=True)

# ── Form ─────────────────────────────────────────────────────────────────────
if image_obj and (face_mesh or face_embedding):
    with st.form(key="register_case_form"):
        st.markdown('<p class="section-label">👤 Person Details</p>', unsafe_allow_html=True)
        c1, c2 = st.columns(2)
        name = c1.text_input("Full Name *", placeholder="e.g. Ravi Kumar")
        fathers_name = c2.text_input("Father's Name", placeholder="e.g. Suresh Kumar")

        c3, c4, c5 = st.columns(3)
        age = c3.number_input("Age *", min_value=1, max_value=100, value=10, step=1)
        adhaar_card = c4.text_input("Aadhaar No.", placeholder="12 digits", max_chars=12)
        last_seen = c5.text_input("Last Seen *", placeholder="e.g. City Mall, Jan 15")

        c6, c7 = st.columns(2)
        address = c6.text_input("Address", placeholder="Last known address")
        birthmarks = c7.text_input("Birth Marks", placeholder="Identifying marks")

        description = st.text_area("Description (optional)", placeholder="Any additional details...", height=80)

        st.markdown('<p class="section-label">📞 Complainant Info</p>', unsafe_allow_html=True)
        cc1, cc2 = st.columns(2)
        complainant_name = cc1.text_input("Complainant Name *", placeholder="Who is filing?")
        complainant_phone = cc2.text_input("Phone Number *", placeholder="10-digit number", max_chars=10)

        st.markdown("")
        submit_bt = st.form_submit_button("Register Case  →", use_container_width=True)

        if submit_bt:
            # Validation
            if not name.strip():
                st.error("Name is required.")
            elif not complainant_name.strip():
                st.error("Complainant name is required.")
            elif not complainant_phone.strip() or not complainant_phone.isdigit() or len(complainant_phone) != 10:
                st.error("Please enter a valid 10-digit phone number.")
            else:
                new_case = RegisteredCases(
                    id=unique_id,
                    submitted_by=user,
                    name=name,
                    father_name=fathers_name,
                    age=str(age),
                    complainant_mobile=complainant_phone,
                    complainant_name=complainant_name,
                    face_mesh=json.dumps(face_mesh) if face_mesh else None,
                    face_embedding=json.dumps(face_embedding) if face_embedding else None,
                    adhaar_card=adhaar_card,
                    birth_marks=birthmarks,
                    address=address,
                    last_seen=last_seen,
                    status="NF",
                    matched_with="",
                )
                db_queries.register_new_case(new_case)
                st.success("✓ Case registered successfully!")
                st.balloons()

elif image_obj and not face_mesh and not face_embedding:
    st.info("↑ Please upload a photo with a clearly visible face to proceed.")
else:
    st.markdown("""
    <div style="text-align:center; padding:2rem; opacity:0.3;">
        <p style="font-size:2rem;">📷</p>
        <p>Upload a photo to get started</p>
    </div>
    """, unsafe_allow_html=True)
