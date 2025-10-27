import streamlit as st
import requests
import base64
from io import BytesIO
from PIL import Image

# --- Configuration ---
# NOTE: Replace this with your actual Gemini API Key (or use Streamlit Secrets)
# IMPORTANT: In a real app, use st.secrets["GEMINI_API_KEY"]
API_KEY = "AIzaSyDxlzYbOluOFAdt7-2EPM-BlhQ77ysHkQg" # Replace with your actual key or use Streamlit Secrets
API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-preview-09-2025:generateContent"

# Set a helpful system instruction to guide the model's behavior
SYSTEM_PROMPT = (
    "You are a highly skilled, board-certified electrophysiologist (cardiologist specializing in "
    "ECG analysis). Your task is to analyze the provided Electrocardiogram (ECG) scan image. "
    "Provide a detailed, structured report that includes:\n"
    "1. **ECG Metrics**: Estimate Heart Rate (BPM), Rhythm (Regular/Irregular), PR Interval, QRS Duration, and QT Interval.\n"
    "2. **Morphology Analysis**: Describe the P-waves, QRS complex, and T-waves in all visible leads.\n"
    "3. **Interpretation/Diagnosis**: Based on the visual evidence, provide a primary and secondary differential diagnosis of any possible diseases, abnormalities, or conditions.\n"
    "4. **Clear Diagnosis Statement**: State in **one single sentence** whether the patient has a disease or a significant abnormality based on the ECG, or if the ECG is within normal limits.\n"
    "5. **Recommendation**: Suggest next steps (e.g., monitor, stress test, specific medication).\n"
    "6. **Lifestyle Recommendations**: Provide general, non-allergic **dietary suggestions** (e.g., Mediterranean diet elements, low sodium) and **light workout recommendations** (e.g., walking, stretching) suitable for general heart health.\n"
    "Format the response using Markdown for clear readability. Start with the Interpretation/Diagnosis section."
)


def image_to_base64(img_bytes):
    """Converts image bytes to base64 string for the API payload."""
    return base64.b64encode(img_bytes).decode('utf-8')


def analyze_ecg_with_gemini(image_base64_data):
    """Calls the Gemini API to analyze the ECG image."""
    
    # Construct the multimodal payload
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

    headers = {
        "Content-Type": "application/json"
    }

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
        return f"🚨 **API Request Error**: Failed to connect to the model API. Please check your API key and network connection. Details: {e}"
    except Exception as e:
        return f"🚨 **General Error**: An unexpected error occurred during processing. Details: {e}"


# --- Streamlit UI Layout (More Colourful and Attractive) ---
st.set_page_config(page_title="Professional ECG Analyst", layout="wide")

# MODIFIED: Enhanced CSS for a modern, attractive, and medical/professional look
st.markdown("""
<style>
/* Overall Page Styling */
.stApp {
    background-color: #f0f2f6; /* Very light blue/grey background */
}

/* Customizing the main header */
.main-header-custom {
    font-size: 2.8em;
    font-weight: 800;
    color: #004d99; /* Deep Medical Blue */
    text-align: center;
    margin-bottom: 25px;
    padding: 10px 0;
    border-bottom: 5px solid #007bff; /* Bright blue underline */
    letter-spacing: 1.5px;
}

/* Styling the main upload and analysis button (Vibrant) */
.stButton>button {
    background-color: #17a2b8; /* Teal/Cyan - Professional but vibrant */
    color: white;
    border-radius: 10px;
    padding: 12px 25px;
    font-size: 1.2em;
    font-weight: bold;
    border: none;
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    transition: background-color 0.3s, transform 0.2s;
}
.stButton>button:hover {
    background-color: #138496; /* Darker teal on hover */
    transform: translateY(-2px); /* Slight lift effect */
}

/* Info/Awaiting boxes (Clean and Clear) */
.stAlert div[data-testid="stAlert"] {
    background-color: #e6f7ff; /* Very light blue background for info */
    border-left: 6px solid #007bff;
    color: #004d99;
    font-size: 1.05em;
    padding: 15px;
    border-radius: 8px;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
}

/* Subheaders (Professional look for sections) */
h2 {
    color: #004d99; /* Deep Medical Blue */
    border-bottom: 2px solid #a8c0d8; /* Subtle grey-blue separator */
    padding-bottom: 8px;
    margin-top: 20px;
}

/* Customizing the file uploader label */
label[data-testid="stFileUploadDropzone"] {
    color: #004d99 !important;
    font-weight: bold;
    font-size: 1.1em;
}

/* Styling the analysis report section */
.stMarkdown h4 {
    color: #28a745; /* Green for section titles within the report */
    border-left: 5px solid #28a745;
    padding-left: 10px;
}

</style>
""", unsafe_allow_html=True)

# MODIFIED: Changed title and main description
st.markdown('<p class="main-header-custom">🩺 Professional Cardiology Analyst</p>', unsafe_allow_html=True)
st.markdown("<h4 style='text-align: center; color: #495057;'>**Upload a 12-Lead ECG scan for a structured electrophysiology report.**</h4>", unsafe_allow_html=True)

# File Uploader
uploaded_file = st.file_uploader(
    "Upload an ECG Image (PNG, JPG)", 
    type=["png", "jpg", "jpeg"],
    accept_multiple_files=False
)

analysis_col, results_col = st.columns([1, 2])

with analysis_col:
    if uploaded_file is not None:
        # Read the file bytes
        file_bytes = uploaded_file.read()

        # Display the uploaded image
        st.subheader("🖼️ Uploaded ECG Scan")
        image = Image.open(BytesIO(file_bytes))
        st.image(image, caption="Uploaded ECG", use_column_width=True)

        # Analysis Button
        if st.button("▶️ Generate Detailed Analysis"):
            
            # Convert image to base64
            image_base64 = image_to_base64(file_bytes)

            with st.spinner('🔬 Performing professional ECG analysis... This may take a moment.'):
                analysis_report = analyze_ecg_with_gemini(image_base64)
            
            # Store the result in session state
            st.session_state['analysis_report'] = analysis_report
            st.session_state['uploaded_file'] = uploaded_file.name
    
    else:
        st.info("⬆️ Awaiting ECG file upload. Please select an image to begin the analysis.")


with results_col:
    st.subheader("📝 Electrophysiology Analysis Report")
    if 'analysis_report' in st.session_state:
        st.markdown("---")
        # Display the generated report
        st.markdown(st.session_state['analysis_report'])
    else:
        st.info("The professional analysis report, including metrics, diagnosis, and lifestyle recommendations, will appear here after you upload and analyze an ECG scan.")
