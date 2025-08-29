from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import PromptTemplate
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader
from langchain_core.output_parsers import StrOutputParser
from dotenv import load_dotenv 
import streamlit as st
import tempfile
import os

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")
model = ChatGoogleGenerativeAI(
    model= "gemini-1.5-flash",
    temperature=0.3,
    google_api_key=api_key
)

parser = StrOutputParser()

def load_document(file_path):
    # Save the uploaded file to a temp location
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
        tmp_file.write(uploaded_file.getbuffer())
        tmp_path = tmp_file.name


    loader = PyPDFLoader(tmp_path)
    docs = loader.load() 

    return docs[0].page_content

prompt1 = PromptTemplate(
    template="""
    Review the candidate's resume: {resume}.
    
    Provide the output in the following **sections**:

    ### Candidate Overview
    (3–4 lines covering name, total experience, and a quick highlight of projects/achievements)

    ### Work Experience
    (Short summary of roles/companies/years — max 3 lines)

    ### Projects & Achievements
    (Brief list of notable projects/achievements — concise points)

    ### Technical Skills
    (List all technical tools, programming languages, frameworks, libraries, cloud platforms, databases, etc.)

    ### Soft Skills
    (Extract any soft skills such as leadership, communication, teamwork, problem-solving, etc.)

    Keep it concise and structured. Do not copy sentences directly from the resume.  
    """,
    input_variables=['resume']
)

prompt2 = PromptTemplate(
    template="You are a highly skilled ATS (Applicant Tracking System) scanner with expertise in Data Science, Full Stack Web Development, "
             "Machine Learning, DevOps, Data Analysis, and Big Data Engineering. Your task is to critically evaluate the provided resume {resume} "
             "against the given job description {descr}. Follow this structure strictly:\n\n"
             "1. **Match Percentage**: Provide a single percentage number with a % sign, reflecting a brutally honest and critical evaluation of how well the resume matches the job description.\n"
             "2. **Missing Keywords**: Output only the missing skills, tools, or keywords as plain bullet points, no explanations or extra text regarding the keywords.\n"
             "3. **Final Thoughts**: Give a concise, VERY slightly elaborative, and brutally honest judgment on the candidate’s overall suitability, "
             "avoiding bluff or sugar-coating.",
    input_variables=['resume', 'descr']
)

prompt3 = PromptTemplate(
    template="You are an experienced HR professional with " \
    "technical expertise in Data Science, Full Stack Web Development, DevOPs,Machine Learning, Data Analyst"
    " and Big Data Engineering.Your task is to evaluate the provided " \
    "resume {resume} against the given job description {descr} and job roles. Provide a" \
    " detailed assessment of whether the candidate's profile aligns with " \
    "the requirements, highlighting key strengths weaknesses of the applicant.Be objective and very concise in your analysi",
    input_variables= ['resume', 'descr']
)


# Streamlit Page Config 
st.set_page_config(page_title="ATS Resume Expert", page_icon="📄", layout="wide")


# Custom CSS styling
st.markdown("""
<style>
.main-header {
    text-align: center;
    color: #2E86AB;
    font-size: 2.5rem;
    font-weight: bold;
    margin-bottom: 0.5rem;
}
.sub-header {
    text-align: center;
    color: #666;
    font-size: 1.1rem;
    margin-bottom: 2rem;
}
.upload-section {
    background-color: #f8f9fa;
    padding: 1.5rem;
    border-radius: 10px;
    border: 2px dashed #dee2e6;
    margin: 1rem 0;
}
.stButton > button {
    width: 100%;
    background-color: #2E86AB;
    color: white;
    border: none;
    border-radius: 5px;
    padding: 0.75rem 1rem;
    font-weight: 500;
    transition: background-color 0.3s;
}
.stButton > button:hover {
    background-color: #1e5f7a;
}
.result-container {
    background-color: #f8f9fa;
    padding: 1.5rem;
    border-radius: 10px;
    border-left: 4px solid #2E86AB;
    margin: 1rem 0;
}
</style>
""", unsafe_allow_html=True)

st.markdown('<h1 class="main-header">ATS Resume Expert</h1>', unsafe_allow_html=True)
st.markdown('<p class="sub-header">Optimize your resume for Applicant Tracking Systems</p>', unsafe_allow_html=True)

# Input Sections
col1, col2 = st.columns(2)

with col1:
    st.subheader("📋 Job Description")
    input_text = st.text_area(
        "Paste the job description here:", 
        key="input",
        height=200,
        placeholder="Enter the job description to match your resume against..."
    )

with col2:
    st.subheader("📄 Resume Upload")
    uploaded_file = st.file_uploader(
        "Upload your resume (PDF format)", 
        type=["pdf"],
        help="Please upload a PDF file of your resume for analysis"
    )

# Analysis Buttons
st.markdown("---")
st.subheader("Analysis Options")

btn_col1, btn_col2, btn_col3 = st.columns(3)

with btn_col1:
    submit1 = st.button("📊 Analyze Resume", help="Get detailed analysis of your resume")
with btn_col2:
    submit2 = st.button("🎯 Match Percentage", help="Calculate compatibility with job description")
with btn_col3:
    submit3 = st.button("💡 Improvement Tips", help="Get suggestions to enhance your resume")

# Results Section
if submit1 or submit2 or submit3:
    if uploaded_file is not None:
        pdf_content = load_document(uploaded_file)

        if submit1:
            response = prompt1 | model | parser
            st.subheader("Resume Analysis Results")
            # st.markdown('<div class="result-container">', unsafe_allow_html=True)
            st.write(response.invoke({'resume': pdf_content}))
            # st.markdown('</div>', unsafe_allow_html=True)

        elif submit2:
            if input_text.strip():
                response = prompt2 | model | parser
                st.subheader(" Compatibility Score")
                # st.markdown('<div class="result-container">', unsafe_allow_html=True)
                st.write(response.invoke({'resume': pdf_content, 'descr': input_text}))
                # st.markdown('</div>', unsafe_allow_html=True)
            else:
                st.warning("⚠️ Please provide a job description for percentage matching.")

        elif submit3:
            if input_text.strip():
                response = prompt3 | model | parser
                st.subheader("Resume Improvement Suggestions")
                st.write(response.invoke({'resume': pdf_content, 'descr': input_text}))
            else: st.warning("⚠️ Please provide a job description for improvement suggestions.")

        else: st.error("❌ Please upload your resume to proceed with the analysis.")

# Sidebar
st.sidebar.markdown("## ℹ️ About ATS Resume Expert")
st.sidebar.markdown("""
This tool helps you optimize your resume for Applicant Tracking Systems (ATS) by:

- **Analyzing** your resume structure and content
- **Calculating** compatibility percentage with job descriptions
- **Providing** actionable improvement suggestions

### 📝 Tips for best results:
- Use a clean, simple PDF format
- Include relevant keywords from the job description
- Ensure proper formatting and sections
- Keep your resume ATS-friendly
""")


st.markdown("---")
