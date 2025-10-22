import os
from datetime import datetime
from io import BytesIO

import streamlit as st
from PIL import Image
from docx import Document
from docx.shared import Inches
import google.generativeai as genai
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Configure Google Gemini API
api_key = os.getenv("GEMINI_API_KEY")
if api_key is None:
    raise ValueError("GEMINI_API_KEY is not set in environment variables")
genai.configure(api_key=api_key)

# Model configuration
generation_config = {
    "temperature": 1,
    "top_p": 0.95,
    "top_k": 64,
    "max_output_tokens": 8192,
    "response_mime_type": "text/plain",
}
model = genai.GenerativeModel(
    model_name="gemini-1.5-pro",
    generation_config=generation_config,
)

def analyze_image(image_file, image_type="Medical Scan"):
    """Send image to Gemini and generate analysis."""
    image = Image.open(image_file)
    current_date = datetime.now().strftime('%Y-%m-%d')

    prompt = f"""
You are a highly experienced medical AI assistant.
Analyze this {image_type} image and provide a detailed report including possible diseases,
observations, and recommendations. Make educated guesses if necessary, 
and clearly indicate any uncertainty.

**ANALYSIS REPORT**

1. Patient Information:
- Date of Scan: {current_date}

2. Scan Observations:
- Key Findings:
- Possible Conditions/Diseases:
- Severity:
- Notes:

3. Recommendations:
- Suggested Tests:
- Follow-up Actions:
- Caution: This analysis is AI-generated. Consult a qualified medical professional.

Provide the report in clear, structured text.
"""
    chat_session = model.start_chat(history=[])
    response = chat_session.send_message([prompt, image])
    return response.text

def create_doc(report_text, image_file):
    """Generate a DOCX report with the analysis and uploaded image."""
    doc = Document()
    doc.add_heading('Medical Image Analysis Report', 0)

    for line in report_text.split("\n"):
        if line.strip() == "":
            continue
        if line.startswith("**") and line.endswith("**"):
            doc.add_heading(line.strip("**"), level=1)
        elif line.startswith("-"):
            doc.add_paragraph(line.strip(), style="List Bullet")
        else:
            doc.add_paragraph(line.strip())

    doc.add_heading('Uploaded Image:', level=1)
    image_stream = BytesIO(image_file.getvalue())
    doc.add_picture(image_stream, width=Inches(6))

    file_stream = BytesIO()
    doc.save(file_stream)
    file_stream.seek(0)
    return file_stream

def main():
    st.title("AI Medical Image Analysis")
    st.write("Upload any medical image (ECG, X-ray, MRI, etc.) and get an AI-generated analysis.")

    uploaded_file = st.file_uploader("Upload Medical Image", type=["png", "jpg", "jpeg"])
    if uploaded_file:
        st.image(uploaded_file, caption="Uploaded Image", use_column_width=True)

        if st.button("Analyze Image"):
            with st.spinner("Analyzing image with Google Gemini..."):
                report_text = analyze_image(uploaded_file)
            st.header("Analysis Report")
            st.markdown(report_text)
            st.session_state.report_text = report_text

        if hasattr(st.session_state, "report_text"):
            doc_file = create_doc(st.session_state.report_text, uploaded_file)
            st.download_button(
                label="Download Analysis Report",
                data=doc_file,
                file_name="Medical_Image_Report.docx",
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
            )

if __name__ == "__main__":
    main()
