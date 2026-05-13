import os
import cv2
import uuid
import json
from datetime import datetime
import numpy as np
import streamlit as st

from pages.helper import db_queries
from pages.helper.data_models import PublicSubmissions, RegisteredCases
from pages.helper.utils import extract_face_mesh_landmarks, extract_face_embedding
from pages.helper.match_algo import match_with_embeddings, match

# ── Page Config ──────────────────────────────────────────────────────────────
st.set_page_config(page_title="CCTV Pipeline · TraceAI", page_icon="◎", layout="wide")

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

# ── Header ───────────────────────────────────────────────────────────────────
st.markdown('<div class="page-tag">Automation</div>', unsafe_allow_html=True)
st.markdown('<p class="page-title">CCTV Face Pipeline</p>', unsafe_allow_html=True)
st.markdown('<p class="page-desc">Automate sighting submissions by processing CCTV footage videos.</p>', unsafe_allow_html=True)
st.markdown('<div class="minimal-divider"></div>', unsafe_allow_html=True)

# ── Video Upload ─────────────────────────────────────────────────────────────
st.markdown('<p class="section-label">📹 Upload Footage</p>', unsafe_allow_html=True)

video_file = st.file_uploader("Upload CCTV Video File (MP4, AVI, MOV)", type=["mp4", "avi", "mov"])

c1, c2 = st.columns(2)
location = c1.text_input("Footage Location", placeholder="e.g. Metro Station Camera 3")
fps_rate = c2.number_input("Process Every N Seconds", min_value=1, max_value=30, value=2)

if st.button("▶️ Start Processing", type="primary", use_container_width=True):
    if not video_file:
        st.error("Please upload a video file first.")
    elif not location.strip():
        st.error("Please provide the footage location.")
    else:
        # Streamlit file_uploader streams can sometimes be exhausted
        video_file.seek(0)
        
        # Save video temporarily
        temp_video_path = f"temp_cctv_{uuid.uuid4().hex[:8]}.mp4"
        with open(temp_video_path, "wb") as f:
            f.write(video_file.read())
        
        # Write to disk completely before OpenCV tries to run
        vid_path_abs = os.path.abspath(temp_video_path)
        
        cap = cv2.VideoCapture(vid_path_abs)
        fps = cap.get(cv2.CAP_PROP_FPS)
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        
        if fps == 0:
            fps = 30 # Default if unable to read
            
        frame_skip = int(fps * fps_rate) # Extract 1 frame per fps_rate seconds
        
        st.info(f"Processing video: ~{total_frames // frame_skip} frames to analyze.")
        
        progress_text = st.empty()
        progress_bar = st.progress(0)
        status_area = st.container()
        
        from deepface import DeepFace
        
        count_processed = 0
        faces_saved = 0
        frames_read = 0
        
        with status_area:
            st.markdown("### Processing Logs:")
            log_container = st.empty()
            logs = []
            
            while cap.isOpened():
                ret, frame = cap.read()
                if not ret:
                    break
                    
                if frames_read % frame_skip == 0:
                    count_processed += 1
                    # Convert to RGB
                    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    
                    try:
                        # Find faces in the frame using DeepFace
                        # Customarily DeepFace expects RGB numpy arrays
                        # We use enforce_detection=True to localize faces
                        logs.append(f"🔍 Analyzing frame {frames_read}...")
                        face_objs = DeepFace.extract_faces(
                            img_path=rgb_frame,
                            detector_backend='opencv', # changed to opencv for Streamlit thread safety
                            enforce_detection=True,
                            align=True
                        )
                        
                        for face_obj in face_objs:
                            face_img = face_obj['face'] # This is normalized 0-1, or uint8 depending on deepface version
                            # Typically deepface returns float32 [0, 1]. Convert back to uint8
                            if face_img.dtype == np.float32 or face_img.dtype == np.float64:
                                face_img = (face_img * 255).astype(np.uint8)
                                
                            # MediaPipe requires contiguous array
                            face_img = np.ascontiguousarray(face_img)
                            
                            # Get embedding for this cropped face (skip detector since it's already cropped)
                            embedding = extract_face_embedding(face_img, detector_backend="skip")
                            mesh = extract_face_mesh_landmarks(face_img)
                            
                            if embedding or mesh:
                                unique_id = str(uuid.uuid4())
                                save_path = f"./resources/{unique_id}.jpg"
                                # BGR for saving
                                cv2.imwrite(save_path, cv2.cvtColor(face_img, cv2.COLOR_RGB2BGR))
                                
                                new_sub = PublicSubmissions(
                                    submitted_by="CCTV System",
                                    location=location.strip(),
                                    email="system@traceai.local",
                                    face_mesh=json.dumps(mesh) if mesh else None,
                                    face_embedding=json.dumps(embedding) if embedding else None,
                                    id=unique_id,
                                    mobile="0000000000",
                                    birth_marks="",
                                    status="NF",
                                )
                                db_queries.new_public_case(new_sub)
                                faces_saved += 1
                                logs.append(f"✅ Found face at frame {frames_read} -> Saved as {unique_id[:8]}")
                            else:
                                logs.append(f"⚠️ Frame {frames_read}: Face found, but failed to extract embedding/mesh")
                                
                    except ValueError as ve:
                        # No face detected in this frame (or another ValueError)
                        logs.append(f"⏭️ No face detected at frame {frames_read} | Details: {ve}")
                    except Exception as e:
                        logs.append(f"⚠️ Error at frame {frames_read}: {e}")
                
                frames_read += 1
                # Update progress
                progress = min(1.0, frames_read / float(total_frames)) if total_frames > 0 else 0
                progress_bar.progress(progress)
                progress_text.text(f"Processed frame {frames_read}/{total_frames}...")
                log_container.code("\n".join(logs[-10:])) # Show last 10 logs
                
        cap.release()
        try:
            os.remove(temp_video_path)
        except:
            pass
            
        progress_text.text("Processing Complete!")
        progress_bar.progress(1.0)
        
        st.success(f"🎉 CCTV Processing Finished! Added {faces_saved} faces from the footage to the database. You can now run 'Match Cases' to see if anyone was spotted.")
