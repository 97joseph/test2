import streamlit as st
from openai import OpenAI
import time

# Configure OpenAI API
client = OpenAI(
    api_key='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'  # Replace with your OpenAI API key
)
model = "gpt-4"  # You can use "gpt-3.5-turbo" or other models

# Telemetry sidebar
st.sidebar.title("Telemetry")
tokens_metric = st.sidebar.metric("Total Tokens", 0)
latency_metric = st.sidebar.metric("Latency (ms)", 0)

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
                response = client.chat.completions.create(
                    model=model,
                    messages=[
                        {"role": "user", "content": prompt}
                    ]
                )

                if not response.choices[0].message.content:
                    st.error("No response received. Please try again.")
                    st.stop()

                # Split response into answer and citations
                response_text = response.choices[0].message.content
                citations = []

                if 'Citations:' in response_text:
                    answer_part, citations_part = response_text.split('Citations:', 1)
                    citations = [c.strip() for c in citations_part.split('\n') if
                                 c.strip().startswith(('1', '2', '3', '4', '5', '6', '7', '8', '9'))]
                else:
                    answer_part = response_text

                # Display formatted answer
                st.subheader("Answer:")
                formatted_answer = answer_part.replace('[', '<sup>').replace(']', '</sup>')
                st.markdown(formatted_answer, unsafe_allow_html=True)

                # Display citations
                if citations:
                    st.subheader("Source Citations:")
                    for citation in citations:
                        st.write(f"📚 {citation}")
                else:
                    st.warning("No citations identified in the response")

                # Telemetry updates
                total_tokens = response.usage.total_tokens
                latency = (time.time() - start_time) * 1000  # Convert to milliseconds
                tokens_metric.metric("Total Tokens", total_tokens)
                latency_metric.metric("Latency (ms)", int(latency))

                # Answer quality check
                quality_check_prompt = f"""Critique whether each citation really supports the sentence it is attached to.
Answer: {formatted_answer}
Citations: {citations}
"""
                quality_response = client.chat.completions.create(
                    model=model,
                    messages=[
                        {"role": "user", "content": quality_check_prompt}
                    ]
                )

                quality_feedback = quality_response.choices[0].message.content
                if "pass" in quality_feedback.lower():
                    st.success("Answer Quality: Pass")
                else:
                    st.error("Answer Quality: Fail")

            except Exception as e:
                st.error(f"Error: {str(e)}")
    else:
        st.warning("Please enter a question")

st.markdown("---")
st.caption("Powered by OpenAI API • Sources may be AI-generated citations")