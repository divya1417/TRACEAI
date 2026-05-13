# TraceAI - Finding Missing Person Using AI

> An AI-powered platform designed to assist law enforcement and organizations in locating missing persons through facial recognition and advanced matching algorithms.

![Python](https://img.shields.io/badge/Python-3.8+-3776ab?style=for-the-badge&logo=python)
![Streamlit](https://img.shields.io/badge/Streamlit-1.0+-FF4B4B?style=for-the-badge&logo=streamlit)
![MediaPipe](https://img.shields.io/badge/MediaPipe-0.8+-FF6F00?style=for-the-badge)
![SQLite](https://img.shields.io/badge/SQLite-3.0+-003B57?style=for-the-badge&logo=sqlite)

---

## Problem Statement

Thousands of people, especially children, go missing every day. Traditional investigative methods, while effective, are time-consuming and resource-intensive. Law enforcement agencies often struggle to quickly scan through massive volumes of CCTV footage and public submissions.

This project provides an **AI-assisted solution** to accelerate the process of locating missing individuals by leveraging facial recognition technology and intelligent matching algorithms.

---

## Project Overview

A comprehensive web-based platform that enables:
- **Case Registration**: Quick registration of missing person cases with facial feature extraction
- **Image Matching**: Fast facial recognition matching against registered cases
- **Multi-User Management**: Role-based dashboards for administrators and users
- **Public Submissions**: Web and mobile interfaces for sighting reports
- **Offline-First Architecture**: SQLite database for portability and minimal setup

---

## Key Features

### 🎭 Facial Recognition
- Uses **MediaPipe Face Mesh** for robust facial feature extraction
- 468-point facial landmarks for accurate matching
- Works with diverse lighting and angles

### 📋 Case Management
- Easy case registration with automatic feature extraction
- Database storage of facial embeddings
- Update and manage case status

### 🔍 Intelligent Matching
- Cosine similarity-based facial matching algorithm
- Fast retrieval from database
- Confidence scoring for matches

### 👥 Multi-Interface System
- **Admin Dashboard**: Full case management and analytics
- **User Portal**: Case registration and matching
- **Mobile/Public App**: Crowdsourced sighting submissions

### 💾 Lightweight & Portable
- SQLite for local data storage
- No cloud dependencies
- Minimal system requirements

---

## Tech Stack

| Category | Technology |
|----------|-----------|
| **Frontend** | Streamlit |
| **Backend** | Python |
| **ML/AI** | MediaPipe, scikit-learn |
| **Database** | SQLite, SQLModel ORM |
| **Data Processing** | NumPy, Pandas, PIL |
| **Authentication** | Streamlit Authenticator |

---

## Installation

### Prerequisites
- Python 3.8 or higher
- pip package manager

### Setup Instructions

1. **Clone the repository**
   ```bash
   git clone https://github.com/your-username/Finding-missing-person-using-AI.git
   cd Finding-missing-person-using-AI
   ```

2. **Create a virtual environment** (optional but recommended)
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure authentication** (optional)
   - Copy `login_config.example.yml` to `login_config.yml`
   - Update credentials with your own secure passwords

5. **Run the application**
   ```bash
   streamlit run Home.py
   ```

   The app will open at `http://localhost:8501`

---

## Usage

### Admin Dashboard
Navigate to the main app to access the admin panel where you can:
- View all registered missing person cases
- Manage case status and information
- Review matching results

### Register New Case (Pages → Register New Case)
- Upload a photo of the missing person
- Enter personal details
- System automatically extracts facial features

### Match Cases (Pages → Match Cases)
- Upload a CCTV or submitted image
- System matches against registered cases
- View confidence scores and potential matches

### CCTV Pipeline (Pages → CCTV Pipeline)
- Process batch CCTV footage
- Extract frames and perform matching
- Generate match reports

### Help Section
- User guide and FAQs
- Contact and support information

---

## Project Structure

```
Finding-missing-person-using-AI/
│
├── Home.py                          # Main application entry point
├── requirements.txt                 # Python dependencies
├── face_landmarker.task            # MediaPipe pre-trained model
│
├── pages/                           # Streamlit multi-page structure
│   ├── 1_Register New Case.py      # Case registration interface
│   ├── 2_All Cases.py              # Case management dashboard
│   ├── 3_Match Cases.py            # Image matching interface
│   ├── 4_Help.py                   # Help & documentation
│   ├── 5_CCTV Pipeline.py          # Batch processing for CCTV
│   │
│   └── helper/                      # Core utility modules
│       ├── data_models.py          # SQLModel data structures
│       ├── db_queries.py           # Database operations
│       ├── match_algo.py           # Facial matching algorithm
│       ├── model_cache.py          # Model caching utilities
│       ├── streamlit_helpers.py    # Streamlit UI helpers
│       ├── train_model.py          # Model training utilities
│       └── utils.py                # General utilities
│
├── resources/                       # Project assets
│   ├── images/                     # Documentation images
│   └── screenshots/                # Application screenshots
│
├── login_config.example.yml        # Authentication config template
├── .gitignore                      # Git ignore rules
└── .github/                        # GitHub configurations

```

---

## How It Works

### 1. **Case Registration**
   - User uploads a photo of the missing person
   - MediaPipe extracts 468 facial landmarks
   - Features stored as embeddings in the database

### 2. **Image Submission**
   - CCTV footage frame or public submission
   - Facial features extracted using same model
   - Queried against registered cases

### 3. **Matching Algorithm**
   - Cosine similarity computed between embeddings
   - Sorted by confidence score
   - Top matches displayed to authorities

### 4. **Result Review**
   - Law enforcement reviews potential matches
   - Confidence scores aid decision-making
   - Case status updated accordingly

---

## Configuration

### Login Credentials
By default, the application includes sample credentials. To set up custom credentials:

1. Create `login_config.yml` from `login_config.example.yml`
2. Update with secure credentials
3. The file is ignored by Git for security

Example structure:
```yaml
credentials:
  usernames:
    admin:
      email: admin@example.com
      name: Administrator
      password: [hashed_password]
```

---

## Database

The application uses SQLite for lightweight, file-based storage:
- **Database file**: `sqlite_database.db` (auto-created on first run)
- **Tables**: 
  - `registered_cases` - Missing person records
  - `public_submissions` - Public submissions
  - `face_embeddings` - Stored facial features

The database file is ignored by Git and created locally on each installation.

---

## Performance Considerations

- **Embedding Extraction**: ~100-200ms per image
- **Single Match Query**: ~10-50ms for typical database sizes
- **Batch Processing**: Scales linearly with image count

---

## Limitations & Future Scope

### Current Limitations
- Requires good quality images for optimal matching
- Single-face detection per image
- Local database suitable for up to 10,000 cases

### Future Enhancements
- Multi-face detection and tracking
- Cloud database integration for scalability
- Real-time CCTV streaming integration
- Mobile app with push notifications
- Integration with national police databases
- Advanced filtering (age, location, time)

---

## Contributing

We welcome contributions from the community! Areas for improvement:
- Algorithm optimization
- UI/UX enhancements
- Mobile app development
- Database scaling solutions
- Documentation improvements

---

## Acknowledgments

This project was developed as an academic initiative at **DIT University**. We acknowledge:

- **MediaPipe Team** for the exceptional open-source face mesh solution
- **Streamlit** for the rapid application development framework
- **scikit-learn** for machine learning utilities
- The missing persons organizations and law enforcement agencies whose work inspired this project

---

## License

This project is provided as-is for educational and humanitarian purposes. For production use, ensure compliance with local regulations and data protection laws.

---

## Contact & Support

For questions, suggestions, or collaboration:
- **Institution**: DIT University
- **Project Type**: Academic Initiative

---

**Disclaimer**: This tool is designed to assist authorities in legitimate missing person investigations. Ensure all usage complies with local laws and regulations regarding facial recognition and privacy.
