import os
import PIL
import numpy as np
import streamlit as st
import mediapipe as mp


def image_obj_to_numpy(image: PIL.Image.Image) -> np.ndarray:
    """Convert a Streamlit-uploaded image object to a numpy array (RGB)."""
    img = PIL.Image.open(image).convert("RGB")
    return np.array(img)


# ── Locate model path (works from any cwd) ──────────────────────────────────
_MODEL_PATH = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),  # pages/helper/
    "..", "..",                                   # project root
    "face_landmarker.task",
)


@st.cache_resource
def _get_landmarker():
    """Create and cache the FaceLandmarker (heavy object, load once)."""
    opts = mp.tasks.vision.FaceLandmarkerOptions(
        base_options=mp.tasks.BaseOptions(model_asset_path=_MODEL_PATH),
        running_mode=mp.tasks.vision.RunningMode.IMAGE,
        num_faces=1,
        output_face_blendshapes=False,
        output_facial_transformation_matrixes=False,
    )
    return mp.tasks.vision.FaceLandmarker.create_from_options(opts)


def extract_face_mesh_landmarks(image: np.ndarray):
    """
    Extract face landmarks from an image using MediaPipe FaceLandmarker.
    Returns a flattened list of all (x, y, z) landmarks if a face is found, else None.
    """
    landmarker = _get_landmarker()
    mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=image)
    result = landmarker.detect(mp_image)

    if result.face_landmarks:
        landmarks = result.face_landmarks[0]
        # Flatten: [x1, y1, z1, x2, y2, z2, ...]
        return [coord for lm in landmarks for coord in (lm.x, lm.y, lm.z)]
    return None


def extract_face_embedding(image: np.ndarray, detector_backend: str = "opencv"):
    """
    Extract 512-d face embedding using DeepFace Facenet512 model.
    Handles both frontal and side profile faces via enforce_detection=False.
    Returns a list of 512 floats if successful, else None.
    """
    try:
        from deepface import DeepFace
        import cv2
        bgr_image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
        results = DeepFace.represent(
            img_path=bgr_image,
            model_name="Facenet512",
            enforce_detection=False,
            detector_backend=detector_backend
        )
        if results and len(results) > 0:
            return results[0]["embedding"]
        return None
    except Exception as e:
        print(f"Face embedding extraction failed: {e}")
        return None
