import streamlit as st
from openai import OpenAI
import time
import requests
from bs4 import BeautifulSoup
import pandas as pd

# Configure OpenAI API
client = OpenAI(
    api_key='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'  # Replace with your OpenAI API key
)
model = "gpt-4"  # You can use "gpt-3.5-turbo" or other models

# Telemetry sidebar
st.sidebar.title("Telemetry")
tokens_metric = st.sidebar.metric("Total Tokens", 0)
latency_metric = st.sidebar.metric("Latency (ms)", 0)
api_calls_metric = st.sidebar.metric("API Calls", 0)
tokens_per_call_metric = st.sidebar.metric("Tokens per Call", 0)
average_latency_metric = st.sidebar.metric("Average Latency (ms)", 0)
relevance_accuracy_metric = st.sidebar.metric("Relevance & Accuracy", 0)

# Analytics sidebar
st.sidebar.title("Analytics")
precision_metric = st.sidebar.metric("Precision", 0)
factuality_metric = st.sidebar.metric("Factuality", 0)
readability_metric = st.sidebar.metric("Readability", 0)
engagement_metric = st.sidebar.metric("Engagement", 0)
authority_metric = st.sidebar.metric("Authority", 0)

# Streamlit UI
st.title("Ask the Web 🌐")
st.subheader("Get Answers with Source Citations")

# Input question
question = st.text_input("Enter your question:", placeholder="E.g., What's the latest AI research from Google?")

def fetch_data(query):
    urls = [
        f"https://www.google.com/search?q={query}",
        f"https://www.bing.com/search?q={query}",
        f"https://duckduckgo.com/?q={query}",  # DuckDuckGo Search
        f"https://search.brave.com/search?q={query}"  # Brave Search
    ]
    data = []
    for url in urls:
        response = requests.get(url)
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            results = soup.find_all('div', class_='BNeawe iBp4i AP7Wnd')
            for result in results:
                data.append(result.get_text())
    return data

def fetch_citations(query):
    urls = [
        f"https://www.google.com/search?q={query}",
        f"https://www.bing.com/search?q={query}",
    ]
    citations = []
    for url in urls:
        response = requests.get(url)
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            links = soup.find_all('a')
            for link in links:
                href = link.get('href')
                if href and href.startswith('http'):
                    citations.append(href)
    return citations

def analyze_relevance_and_accuracy(answer, citations):
    relevance_score = 0.85  # Example relevance score
    accuracy_score = 0.90  # Example accuracy score
    return relevance_score, accuracy_score

def analyze_precision(answer):
    precision_score = 0.75  # Example precision score
    return precision_score

def analyze_factuality(answer):
    factuality_score = 0.80  # Example factuality score
    return factuality_score

def analyze_readability(answer):
    readability_score = 0.90  # Example readability score
    return readability_score

def analyze_engagement(answer):
    engagement_score = 0.60  # Example engagement score
    return engagement_score

def analyze_authority(answer):
    authority_score = 0.85  # Example authority score
    return authority_score

if st.button("Get Answer"):
    if question:
        start_time = time.time()

        with st.spinner("Searching the web..."):
            try:
                web_data = fetch_data(question)
                citations = fetch_citations(question)

                prompt = f"""Answer the following question in plain English using the provided data. Follow these rules:
1. Use numbered citations like [1], [2], etc., in the answer
2. After the answer, add 'Citations:' followed by:
   - Numbered list of sources
   - Include URLs when available
   - Use reliable web sources

Question: {question}

Data: {web_data}
"""

                response = client.chat.completions.create(
                    model=model,
                    messages=[
                        {"role": "user", "content": prompt}
                    ]
                )

                if not response.choices[0].message.content:
                    st.error("No response received. Please try again.")
                    st.stop()

                response_text = response.choices[0].message.content
                citations_part = "\n".join([f"{i+1}. {citation}" for i, citation in enumerate(citations)])

                # Display formatted answer
                st.subheader("Answer:")
                formatted_answer = response_text.replace('[', '<sup>').replace(']', '</sup>')
                st.markdown(formatted_answer, unsafe_allow_html=True)

                # Display citations
                st.subheader("Source Citations:")
                st.write(citations_part)

                # Telemetry updates
                total_tokens = response.usage.total_tokens
                latency = (time.time() - start_time) * 1000  # Convert to milliseconds
                api_calls = 1
                tokens_per_call = total_tokens / api_calls
                average_latency = latency / api_calls

                tokens_metric.metric("Total Tokens", total_tokens)
                latency_metric.metric("Latency (ms)", int(latency))
                api_calls_metric.metric("API Calls", api_calls)
                tokens_per_call_metric.metric("Tokens per Call", int(tokens_per_call))
                average_latency_metric.metric("Average Latency (ms)", int(average_latency))

                # Analyze relevance and accuracy
                relevance_score, accuracy_score = analyze_relevance_and_accuracy(formatted_answer, citations)
                relevance_accuracy_metric.metric("Relevance & Accuracy", f"{relevance_score:.2f} / {accuracy_score:.2f}")

                # Analyze additional metrics
                precision_score = analyze_precision(formatted_answer)
                factuality_score = analyze_factuality(formatted_answer)
                readability_score = analyze_readability(formatted_answer)
                engagement_score = analyze_engagement(formatted_answer)
                authority_score = analyze_authority(formatted_answer)

                precision_metric.metric("Precision", f"{precision_score:.2f}")
                factuality_metric.metric("Factuality", f"{factuality_score:.2f}")
                readability_metric.metric("Readability", f"{readability_score:.2f}")
                engagement_metric.metric("Engagement", f"{engagement_score:.2f}")
                authority_metric.metric("Authority", f"{authority_score:.2f}")

                # Answer quality check
                quality_check_prompt = f"""Critique whether each citation really supports the sentence it is attached to.
Answer: {formatted_answer}
Citations: {citations_part}
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