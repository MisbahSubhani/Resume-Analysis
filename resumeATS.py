import streamlit as st
import os
from dotenv import load_dotenv
import google.generativeai as genai
from PyPDF2 import PdfReader
import re

# Load environment variables and configure API
load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
model = genai.GenerativeModel("gemini-1.5-flash")

# Function to get Gemini output
def get_gemini_output(pdf_text, prompt):
    response = model.generate_content([pdf_text, prompt])
    return response.text

# Function to read PDF
def read_pdf(uploaded_file):
    if uploaded_file is not None:
        pdf_reader = PdfReader(uploaded_file)
        pdf_text = ""
        for page in pdf_reader.pages:
            pdf_text += page.extract_text()
        return pdf_text
    else:
        raise FileNotFoundError("No file uploaded")

# Function to extract score from response
def extract_score(response_text):
    match = re.search(r'(?:ATS|overall|compatibility)?(?:score|rating)?\s*:\s*(\d{1,3})\s*(?:out of 100|/100)?', response_text, re.IGNORECASE)
    if match:
        return int(match.group(1))
    return None

# Streamlit UI with black background
st.set_page_config(page_title="NextStep Resume Analysis", layout="centered")

# Dark theme CSS with black background
st.markdown("""
    <style>
    .main {
        background-color: #000000;
        color: #ffffff;
    }
    .block-container {
        max-width: 900px;
        padding: 2rem;
        background-color: #1a1a1a;
        border-radius: 15px;
        box-shadow: 0 4px 20px rgba(255, 255, 255, 0.1);
        margin-top: 2rem;
        margin-bottom: 2rem;
        border: 1px solid #333333;
    }
    .stButton>button {
        background-color: #4a6fa5;
        color: white;
        border-radius: 12px;
        padding: 10px 24px;
        font-weight: 600;
        border: none;
        width: 100%;
        transition: all 0.3s ease;
    }
    .stButton>button:hover {
        background-color: #3a5a80;
        transform: scale(1.02);
    }
    .stTextInput>div>div>input, .stTextArea>textarea {
        background-color: #2d2d2d;
        color: white;
        border-radius: 12px;
        padding: 12px;
        border: 1px solid #444444;
    }
    .stRadio>div {
        display: flex;
        gap: 20px;
    }
    .stRadio>div>div {
        flex: 1;
    }
    .stRadio>div>div>label>div:first-child {
        padding: 15px;
        border-radius: 12px;
        border: 1px solid #444444;
        transition: all 0.3s ease;
        background-color: #2d2d2d;
        color: white;
    }
    .stRadio>div>div>label>div:first-child:hover {
        border-color: #4a6fa5;
        box-shadow: 0 2px 8px rgba(74, 111, 165, 0.5);
    }
    h1, h2, h3, h4, h5, h6 {
        color: #ffffff;
    }
    h1 {
        font-size: 2.5rem;
        margin-bottom: 1rem;
        text-align: center;
    }
    h2 {
        font-size: 1.8rem;
        margin-bottom: 1rem;
        text-align: center;
    }
    h3 {
        font-size: 1.4rem;
        margin-bottom: 1rem;
    }
    .stExpander {
        background-color: #2d2d2d;
        border-radius: 12px;
        border: 1px solid #444444;
    }
    .stMarkdown {
        color: #ffffff;
        line-height: 1.6;
    }
    .css-1v3fvcr {
        gap: 20px;
    }
    .score-display {
        font-size: 2rem;
        font-weight: bold;
        color: #4CAF50;
        text-align: center;
        margin: 1rem 0;
        padding: 1rem;
        background-color: #1e3b1e;
        border-radius: 12px;
        border: 2px solid #4CAF50;
    }
    .fileUploader {
        background-color: #2d2d2d;
        border-radius: 12px;
        padding: 20px;
        border: 2px dashed #444444;
    }
    .stFileUploader > div > div {
        color: white !important;
    }
    .st-bb {
        background-color: transparent;
    }
    .st-c0 {
        color: white !important;
    }
    </style>
    """, unsafe_allow_html=True)

# Main content container
with st.container():
    st.title("NextStep Resume Analysis")
    st.subheader("AI-powered resume optimization for your career advancement")

    # File upload with dark theme styling
    st.markdown("### Upload Your Resume")
    st.markdown('<div class="fileUploader">', unsafe_allow_html=True)
    upload_file = st.file_uploader("Upload PDF resume", type=["pdf"], label_visibility="collapsed")
    st.markdown('</div>', unsafe_allow_html=True)

    # Job description input with dark theme styling
    st.markdown("### Job Description (Optional)")
    job_description = st.text_area("Enter job description", height=150, label_visibility="collapsed", 
                                 placeholder="Paste the job description you're applying for to get tailored recommendations")

    # Analysis options with dark theme styling
    st.markdown("### Select Analysis Type")
    analysis_option = st.radio("Analysis type selection", 
                             ["Quick Scan", "Detailed Analysis", "ATS Optimization"],
                             horizontal=True,
                             label_visibility="collapsed")

    # Analyze button with dark theme styling
    if st.button("Analyze Resume", type="primary"):
        if upload_file is not None:
            with st.spinner("Analyzing your resume..."):
                pdf_text = read_pdf(upload_file)
                
                if analysis_option == "Quick Scan":
                    prompt = f"""
                    You are ResumeChecker, an expert in resume analysis. Provide a quick scan of the following resume:
                    
                    1. Start with the overall ATS score out of 100 (display as "ATS Score: XX/100").
                    2. Identify the most suitable profession for this resume.
                    3. List 3 key strengths of the resume.
                    4. Suggest 2 quick improvements.
                    
                    Resume text: {pdf_text}
                    Job description (if provided): {job_description}
                    """
                elif analysis_option == "Detailed Analysis":
                    prompt = f"""
                    You are ResumeChecker, an expert in resume analysis. Provide a detailed analysis of the following resume:
                    
                    1. Start with the overall ATS score out of 100 (display as "ATS Score: XX/100").
                    2. Identify the most suitable profession for this resume.
                    3. List 5 strengths of the resume.
                    4. Suggest 3-5 areas for improvement with specific recommendations.
                    5. Rate the following aspects out of 10: Impact, Brevity, Style, Structure, Skills.
                    6. Provide a brief review of each major section (e.g., Summary, Experience, Education).
                    
                    Resume text: {pdf_text}
                    Job description (if provided): {job_description}
                    """
                else:  # ATS Optimization
                    prompt = f"""
                    You are ResumeChecker, an expert in ATS optimization. Analyze the following resume and provide optimization suggestions:
                    
                    1. Start with the ATS compatibility score out of 100 (display as "ATS Compatibility Score: XX/100").
                    2. Identify keywords from the job description that should be included in the resume.
                    3. Suggest reformatting or restructuring to improve ATS readability.
                    4. Recommend changes to improve keyword density without keyword stuffing.
                    5. Provide 3-5 bullet points on how to tailor this resume for the specific job description.
                    6. Explain how to improve the score.
                    
                    Resume text: {pdf_text}
                    Job description: {job_description}
                    """
                
                response = get_gemini_output(pdf_text, prompt)
                
                # Extract and display score prominently
                score = extract_score(response)
                if score:
                    st.markdown(f'<div class="score-display">ATS Score: {score}/100</div>', unsafe_allow_html=True)
                
                # Display results
                with st.expander("Analysis Results", expanded=True):
                    st.markdown(response)
                
                # Chat feature
                st.divider()
                st.markdown("### Resume Q&A")
                user_question = st.text_input("Ask any follow-up questions about your resume analysis:", 
                                            placeholder="How can I improve my work experience section?")
                if user_question:
                    with st.spinner("Generating response..."):
                        chat_prompt = f"""
                        Based on the resume and analysis above, answer the following question:
                        {user_question}
                        
                        Resume text: {pdf_text}
                        Previous analysis: {response}
                        """
                        chat_response = get_gemini_output(pdf_text, chat_prompt)
                        st.markdown(chat_response)
        else:
            st.error("Please upload a resume to analyze.")