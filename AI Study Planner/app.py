import streamlit as st
import google.generativeai as genai
import fitz  # PyMuPDF for PDF extraction
import os
from dotenv import load_dotenv  # Import dotenv to load environment variables

# Load environment variables from the .env file
load_dotenv()

# Retrieve the Gemini API key from the environment
API_KEY = os.getenv("GEMINI_API_KEY")

# Configure API Key
if API_KEY:
    genai.configure(api_key=API_KEY)
else:
    st.error("API Key is missing. Please ensure that the GEMINI_API_KEY is set in the .env file.")

# Initialize models for different tasks
study_plan_model = genai.GenerativeModel(model_name="gemini-study-plan-model")  # Study plan generation
material_analysis_model = genai.GenerativeModel(model_name="gemini-material-analysis-model")  # Use a different model for text analysis

# Streamlit UI
st.set_page_config(page_title="AI Study Planner", layout="centered")
st.title("AI Personalized Study Planner")
st.write("Get a customized study plan based on your study topics or uploaded materials.")

# User input
user_input = st.text_area("✏️ Enter your study topic or question:")

# 📌 Customization Options
st.subheader("🎯 Customize Your Study Plan")
duration = st.selectbox("Study Duration", ["1 Week", "1 Month", "3 Months"])
pace = st.selectbox("🚀 Learning Pace", ["Slow", "Medium", "Fast"])
style = st.selectbox("🎓 Preferred Study Style", ["Text-based", "Video-based", "Practice-heavy"])

# File upload option
uploaded_file = st.file_uploader("Upload a study material (PDF)", type=["pdf"])
extracted_text = ""

if uploaded_file:
    st.info("📄 Extracting text from uploaded PDF...")
    try:
        # Read the uploaded file
        file_bytes = uploaded_file.read()
        
        # Open the PDF using PyMuPDF
        doc = fitz.open(stream=file_bytes, filetype="pdf")
        
        # Extract text from each page
        extracted_text = ""
        for page in doc:
            extracted_text += page.get_text()
        
        # Display a preview of the extracted text (limit to 500 characters)
        st.text_area("📜 Extracted Text", extracted_text[:500], height=200)
    except Exception as e:
        st.error(f"Failed to extract text from PDF: {e}")

# Generate study plan button
if st.button("🎯 Generate Study Plan"):
    if user_input.strip():
        with st.spinner("📝 Creating your study plan..."):
            try:
                prompt = f"Create a {duration} study plan with a {pace} learning pace focusing on {style} learning. Topic: {user_input}"
                response = study_plan_model.generate_content(prompt)
                if response.text:
                    st.subheader("📖 Your  Study Plan:")
                    st.write(response.text)
                else:
                    st.error("No response generated. Please try again.")
            except Exception as e:
                st.error(f"Failed to generate study plan: {e}")
    else:
        st.warning("⚠️ Please enter a study topic.")

# Analyze uploaded material button
if uploaded_file and st.button("📘 Analyze Uploaded Study Material"):
    if extracted_text.strip():
        with st.spinner("🔍 Analyzing your study material..."):
            try:
                response = material_analysis_model.generate_content(extracted_text)
                st.subheader("📚 Insights from Uploaded Material:")
                st.write(response.text)
            except Exception as e:
                st.error(f"Failed to analyze study material: {e}")
    else:
        st.warning("⚠️ No text extracted from the uploaded PDF.")
