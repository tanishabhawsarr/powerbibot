import streamlit as st
from PyPDF2 import PdfReader
from openai import AzureOpenAI
import os

# -------------------------------
# Azure OpenAI Configuration
# -------------------------------
client = AzureOpenAI(
    api_key=os.getenv("AZURE_OPENAI_API_KEY"),
    api_version="2024-02-15-preview",
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT")
)

DEPLOYMENT_NAME = os.getenv("AZURE_OPENAI_DEPLOYMENT")

# -------------------------------
# Streamlit UI
# -------------------------------
st.set_page_config(page_title="PowerBI Insights Bot", page_icon="🤖")
st.title("📄 PowerBI Insights Bot")

pdf_text = ""

pdf_file = st.file_uploader("Upload a PDF", type="pdf")

if pdf_file:
    try:
        reader = PdfReader(pdf_file, strict=False)
        for page in reader.pages:
            text = page.extract_text()
            if text:
                pdf_text += text + "\n"

        st.success(f"PDF uploaded successfully: {pdf_file.name}")

    except Exception as e:
        st.error(f"Error reading PDF: {e}")

# -------------------------------
# PDF Insights
# -------------------------------
if pdf_text:
    st.subheader("📊 PDF Insights")

    summary_prompt = f"""
    You are an expert analyst.
    Summarize the following PDF content into key insights, important numbers, and main points.
    Keep it concise and dashboard friendly.

    PDF Content:
    {pdf_text}
    """

    try:
        response = client.chat.completions.create(
            model=DEPLOYMENT_NAME,
            messages=[{"role": "user", "content": summary_prompt}],
            temperature=0.3
        )
        st.write(response.choices[0].message.content)

    except Exception as e:
        st.error(f"Error generating insights: {e}")

    # -------------------------------
    # Q&A Section
    # -------------------------------
    st.subheader("💬 Ask questions about the PDF")
    question = st.chat_input("Ask your question")

    if question:
        qa_prompt = f"""
        Answer using ONLY the information from the PDF.

        PDF Content:
        {pdf_text}

        Question:
        {question}
        """

        try:
            response = client.chat.completions.create(
                model=DEPLOYMENT_NAME,
                messages=[{"role": "user", "content": qa_prompt}],
                temperature=0.2
            )
            st.write("**Answer:**")
            st.write(response.choices[0].message.content)

        except Exception as e:
            st.error(f"Error generating answer: {e}")
