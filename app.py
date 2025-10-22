import os
from datetime import datetime
from io import BytesIO

import streamlit as st
from PIL import Image
from docx import Document
from docx.shared import Inches
from dotenv import load_dotenv
import google.generativeai as genai

# Load environment variables
load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")
if api_key is None:
    st.error("GEMINI_API_KEY not set in environment variables.")
    st.stop()

# Configure Google Gemini
genai.configure(api_key=api_key)

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


def generate_report(image_file):
    image = Image.open(image_file)
    current_date = datetime.now().strftime("%Y-%m-%d")
    
    prompt = f"""
Analyze this medical scan image and provide a detailed report.
- Mention any abnormalities or possible diseases.
- Give clear, structured analysis.
- If unsure, mention 'Unable to determine from the image'.
- Include recommendations and caution about consulting a medical professional.
Date: {current_date}
"""

    chat_session = model.start_chat(history=[])
    response = chat_session.send_message([prompt, image])
    return response.text


def create_doc(report_text, image_file):
    doc = Document()
    doc.add_heading("Medical Scan Analysis Report", 0)

    for line in report_text.split("\n"):
        if line.strip() == "":
            continue
        if line.startswith("-"):
            doc.add_paragraph(line.strip(), style="List Bullet")
        else:
            doc.add_paragraph(line.strip())

    doc.add_heading("Uploaded Image:", level=1)
    image_stream = BytesIO(image_file.getvalue())
    doc.add_picture(image_stream, width=Inches(6))

    file_stream = BytesIO()
    doc.save(file_stream)
    file_stream.seek(0)
    return file_stream


def main():
    st.title("Medical Scan Analysis with AI (Google Gemini)")

    uploaded_file = st.file_uploader(
        "Upload medical scan (ECG/X-ray/etc.)", type=["png", "jpg", "jpeg"]
    )

    if uploaded_file:
        st.image(uploaded_file, caption="Uploaded Image", use_column_width=True)

        if st.button("Generate Report"):
            with st.spinner("Analyzing image..."):
                report_text = generate_report(uploaded_file)
            st.subheader("AI-Generated Report")
            st.markdown(report_text)

            # Enable download
            doc_stream = create_doc(report_text, uploaded_file)
            st.download_button(
                label="Download Report",
                data=doc_stream,
                file_name="Medical_Report.docx",
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            )


if __name__ == "__main__":
    main()
