import streamlit as st
import requests
import base64
from io import BytesIO
from PIL import Image

# --- Configuration ---
# IMPORTANT: In a real app, use st.secrets["GEMINI_API_KEY"] for security!
API_KEY = "AIzaSyDxlzYbOluOFAdt7-2EPM-BlhQ77ysHkQg" # Replace with your actual key or use Streamlit Secrets
API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-preview-09-2025:generateContent"

# --- System Prompt (Unchanged as it contains all required report structure) ---
SYSTEM_PROMPT = (
    "You are a highly skilled, board-certified electrophysiologist (cardiologist specializing in "
    "ECG analysis). Your task is to analyze the provided Electrocardiogram (ECG) scan image. "
    "Provide a detailed, structured report that includes:\n"
    "1. **ECG Metrics**: Estimate Heart Rate (BPM), Rhythm (Regular/Irregular), PR Interval, QRS Duration, and QT Interval.\n"
    "2. **Morphology Analysis**: Describe the P-waves, QRS complex, and T-waves in all visible leads.\n"
    "3. **Interpretation/Diagnosis**: Based on the visual evidence, provide a primary and secondary differential diagnosis of any possible diseases, abnormalities, or conditions.\n"
    "4. **Clear Diagnosis Statement**: State in **one single sentence** whether the patient has a disease or a significant abnormality based on the ECG, or if the ECG is within normal limits.\n"
    "5. **Recommendation**: Suggest next steps (e.g., monitor, stress test, specific medication, follow-up).\n"
    "6. **Lifestyle Recommendations**: Provide general, non-allergic **dietary suggestions** (e.g., Mediterranean diet elements, low sodium) and **light workout recommendations** (e.g., walking, stretching) suitable for general heart health.\n"
    "Format the response using Markdown for clear readability. Start with the Interpretation/Diagnosis section."
)

# --- Helper Functions ---
def image_to_base64(img_bytes):
    """Converts image bytes to base64 string for the API payload."""
    return base64.b64encode(img_bytes).decode('utf-8')

@st.cache_data(show_spinner=False) # Cache the API call based on image hash/data
def analyze_ecg_with_gemini(image_base64_data):
    """Calls the API to analyze the ECG image."""
    
    # ... (API Payload and Request logic remains the same)
    payload = {
        "contents": [
            {
                "role": "user",
                "parts": [
                    {
                        "inlineData": {
                            "mimeType": "image/png",
                            "data": image_base64_data
                        }
                    },
                    {
                        "text": "Analyze this ECG scan and provide a professional, structured electrophysiology report as instructed."
                    }
                ]
            }
        ],
        "systemInstruction": {
            "parts": [{"text": SYSTEM_PROMPT}]
        }
    }

    headers = { "Content-Type": "application/json" }
    api_endpoint = API_URL
    if API_KEY:
        api_endpoint += f"?key={API_KEY}"

    try:
        response = requests.post(api_endpoint, headers=headers, json=payload)
        response.raise_for_status()
        
        result = response.json()
        generated_text = result.get('candidates', [{}])[0].get('content', {}).get('parts', [{}])[0].get('text', 'Analysis failed or no text generated.')
        return generated_text

    except requests.exceptions.RequestException as e:
        return f"🚨 **API Request Error**: Failed to connect to the model API. Details: {e}"
    except Exception as e:
        return f"🚨 **General Error**: An unexpected error occurred during processing. Details: {e}"

# --- Streamlit UI Layout (Cleaned up, single-button flow) ---

st.set_page_config(page_title="Cardiology Scan Analyst", layout="wide")

# Customized CSS (Same attractive style as before)
st.markdown("""
<style>
/* Overall Page Styling with a subtle gradient */
.stApp {
    background: linear-gradient(135deg, #e3f2fd 10%, #ffffff 100%); /* Very light blue/white gradient */
}

/* Customizing the main header */
.main-header-custom {
    font-size: 3.2em;
    font-weight: 900;
    color: #00897b; /* Teal Green - Calm yet professional */
    text-align: center;
    margin-bottom: 20px;
    padding: 15px 0;
    border-bottom: 6px solid #4db6ac; /* Accent underline */
    letter-spacing: 1.5px;
    text-shadow: 1px 1px 3px rgba(0, 0, 0, 0.1);
}

/* Styling the main upload and analysis button (Single button, high contrast) */
.stButton>button {
    background-color: #6a1b9a; /* Deep Purple - High contrast for action */
    color: white;
    border-radius: 15px;
    padding: 15px 30px;
    font-size: 1.3em;
    font-weight: bold;
    border: none;
    width: 100%; 
    box-shadow: 0 8px 15px rgba(0, 0, 0, 0.2);
    transition: background-color 0.3s, transform 0.2s, box-shadow 0.3s;
}
.stButton>button:hover {
    background-color: #4a148c; /* Darker purple on hover */
    transform: translateY(-4px); 
    box-shadow: 0 10px 20px rgba(0, 0, 0, 0.3);
}

/* Info/Awaiting boxes (Clear and helpful feedback) */
.stAlert div[data-testid="stAlert"] {
    background-color: #e0f2f1; /* Light Teal background for info */
    border-left: 6px solid #00897b; /* Teal border */
    color: #004d40; /* Dark Teal text */
    font-size: 1.1em;
    padding: 20px;
    border-radius: 10px;
    box-shadow: 0 2px 5px rgba(0, 0, 0, 0.08);
}

/* Subheaders (Structured and clean) */
h2 {
    color: #00897b; /* Teal Green */
    border-bottom: 3px solid #b2dfdb; 
    padding-bottom: 10px;
    margin-top: 25px;
}

/* Report Section Headings (Visual Hierarchy) */
.stMarkdown h4 {
    color: #d81b60; /* Deep Pink accent for report sections */
    border-left: 5px solid #00897b; /* Teal accent bar */
    padding-left: 10px;
    margin-top: 20px;
    font-weight: 600;
}
</style>
""", unsafe_allow_html=True)

# Main Title
st.markdown('<p class="main-header-custom">🫀 Cardiology Scan Analyst</p>', unsafe_allow_html=True)
st.markdown("<h4 style='text-align: center; color: #6a1b9a;'>**Upload your ECG scan for an immediate, detailed electrophysiology report.**</h4>", unsafe_allow_html=True)

# Initialize Session State
if 'analysis_report' not in st.session_state:
    st.session_state['analysis_report'] = None
if 'uploaded_file_data' not in st.session_state:
    st.session_state['uploaded_file_data'] = None

# --- Main App Logic ---

# 1. File Uploader
uploaded_file = st.file_uploader(
    "1️⃣ Upload your 12-Lead ECG Image (PNG, JPG)", 
    type=["png", "jpg", "jpeg"],
    accept_multiple_files=False,
    # Clear analysis if a new file is uploaded
    on_change=lambda: st.session_state.update(analysis_report=None, uploaded_file_data=None)
)

analysis_col, results_col = st.columns([1, 2])

with analysis_col:
    st.markdown("---")
    st.markdown("### 2️⃣ Image Preview")
    
    if uploaded_file is not None:
        # Read file bytes only once
        file_bytes = uploaded_file.getvalue()
        st.session_state['uploaded_file_data'] = file_bytes
        
        image = Image.open(BytesIO(file_bytes))
        st.image(image, caption="Uploaded ECG", use_container_width=True) 

    else:
        st.info("⬆️ Please upload an image to proceed.")

    st.markdown("---")
    
    # 3. Single Analyze Button (Conditional)
    if uploaded_file is not None:
        # Check if we need to run analysis or if results are already present
        if st.session_state['analysis_report'] is None:
            if st.button("▶️ Generate Detailed Analysis", key="run_analysis_key"):
                with st.spinner('🔬 Performing professional electrophysiology analysis...'):
                    # Call the cached analysis function
                    image_base64 = image_to_base64(st.session_state['uploaded_file_data'])
                    report = analyze_ecg_with_gemini(image_base64)
                    st.session_state['analysis_report'] = report
                    # Rerun to display results without another button click
                    st.experimental_rerun()
        else:
             st.success("✅ Analysis Complete! See the report on the right.")
             if st.button("Clear Results and Start New Analysis", key="clear_results"):
                st.session_state['analysis_report'] = None
                st.session_state['uploaded_file_data'] = None
                analyze_ecg_with_gemini.clear() # Clear cache
                st.experimental_rerun()
    else:
        st.button("Upload Image First", disabled=True)


with results_col:
    st.subheader("📝 Electrophysiology Analysis Report")
    
    # 4. Results Display
    if st.session_state['analysis_report']:
        st.markdown("---")
        # Display the generated report
        st.markdown(st.session_state['analysis_report'])
    else:
        st.info("The professional analysis report, including metrics, diagnosis, and lifestyle recommendations, will appear here after clicking 'Generate Detailed Analysis'.")
