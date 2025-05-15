import streamlit as st
from openai import OpenAI
import requests
import time

# Configure OpenAI API
client = OpenAI(
    api_key='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'  # Replace with your OpenAI API key
)
model = "gpt-4"  # You can use "gpt-3.5-turbo" or other models

# Configure Gemini API
GEMINI_API_KEY = "AIzaSyCK0Aq_T5V-Qc4h78EEDsPthTniaqILowk"
GEMINI_API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent"

# Function to call Gemini API
def call_gemini(prompt):
    headers = {
        "Authorization": f"Bearer {GEMINI_API_KEY}",
        "Content-Type": "application/json"
    }
    data = {
        "prompt": {"text": prompt},
        "temperature": 0.7
    }
    response = requests.post(GEMINI_API_URL, headers=headers, json=data)
    response.raise_for_status()
    return response.json()

# Telemetry sidebar on the left
st.sidebar.title("Telemetry")
tokens_metric = st.sidebar.metric("Total Tokens", 0)
latency_metric = st.sidebar.metric("Latency (ms)", 0)
gemini_tokens_metric = st.sidebar.metric("Gemini Tokens", 0)
gemini_latency_metric = st.sidebar.metric("Gemini Latency (ms)", 0)
gemini_remarks_metric = st.sidebar.metric("Gemini Remarks", "")

# Streamlit UI
st.title("Ask the Web 🌐")
st.subheader("Get Answers with Source Citations")

# Input question
question = st.text_input("Enter your question:", placeholder="E.g., What's the latest AI research from Google?")

if st.button("Get Answer"):
    if question:
        start_time = time.time()

        with st.spinner("Searching the web..."):
            try:
                # Create prompt with citation instructions
                prompt = f"""Answer the following question in plain English. Follow these rules:
1. Use numbered citations like [1], [2], etc., in the answer
2. After the answer, add 'Citations:' followed by:
   - Numbered list of sources
   - Include URLs when available
   - Use reliable web sources

Question: {question}"""

                # Get OpenAI response
                openai_start_time = time.time()
                openai_response = client.chat.completions.create(
                    model=model,
                    messages=[
                        {"role": "user", "content": prompt}
                    ]
                )
                openai_latency = (time.time() - openai_start_time) * 1000  # Convert to milliseconds
                openai_tokens = openai_response.usage.total_tokens
                openai_answer = openai_response.choices[0].message.content

                # Get Gemini response
                gemini_start_time = time.time()
                gemini_response = call_gemini(prompt)
                gemini_latency = (time.time() - gemini_start_time) * 1000  # Convert to milliseconds
                gemini_tokens = gemini_response.get("content", {}).get("tokens", 0)
                gemini_answer = gemini_response.get("content", {}).get("text", "")

                # Evaluate OpenAI response using Gemini
                evaluation_prompt = f"""Evaluate the following OpenAI response for accuracy and completeness:
OpenAI Answer: {openai_answer}
Question: {question}
Provide a brief remark on the quality of the OpenAI response."""
                evaluation_response = call_gemini(evaluation_prompt)
                gemini_remarks = evaluation_response.get("content", {}).get("text", "")

                # Display formatted answer
                st.subheader("OpenAI Answer:")
                formatted_openai_answer = openai_answer.replace('[', '<sup>').replace(']', '</sup>')
                st.markdown(formatted_openai_answer, unsafe_allow_html=True)

                st.subheader("Gemini Answer:")
                st.write(gemini_answer)

                st.subheader("Gemini Evaluation of OpenAI Answer:")
                st.write(gemini_remarks)

                # Telemetry updates
                tokens_metric.metric("Total Tokens", openai_tokens)
                latency_metric.metric("Latency (ms)", int(openai_latency))
                gemini_tokens_metric.metric("Gemini Tokens", gemini_tokens)
                gemini_latency_metric.metric("Gemini Latency (ms)", int(gemini_latency))
                gemini_remarks_metric.metric("Gemini Remarks", gemini_remarks)

            except Exception as e:
                st.error(f"Error: {str(e)}")
    else:
        st.warning("Please enter a question")

st.markdown("---")
st.caption("Powered by OpenAI API and Gemini API • Sources may be AI-generated citations")