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

# Streamlit UI
st.title("Ask the Web 🌐")
st.subheader("Get Answers with Source Citations")

# Input question
question = st.text_input("Enter your question:", placeholder="E.g., What's the latest AI research from Google?")

def fetch_data(query):
    # List of URLs to scrape
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
            # Extract relevant data (e.g., search results)
            results = soup.find_all('div', class_='BNeawe iBp4i AP7Wnd')
            for result in results:
                data.append(result.get_text())
    return data

def fetch_citations(query):
    # List of URLs to scrape for citations
    urls = [
        f"https://www.google.com/search?q={query}",
        f"https://www.bing.com/search?q={query}",
        # Add more search engines or specific URLs as needed
    ]
    citations = []
    for url in urls:
        response = requests.get(url)
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            # Extract URLs from search results
            links = soup.find_all('a')
            for link in links:
                href = link.get('href')
                if href and href.startswith('http'):
                    citations.append(href)
    return citations

def analyze_relevance_and_accuracy(answer, citations):
    # Placeholder function to analyze relevance and accuracy
    # This can be replaced with a more sophisticated analysis
    relevance_score = 0.85  # Example relevance score
    accuracy_score = 0.90  # Example accuracy score
    return relevance_score, accuracy_score

if st.button("Get Answer"):
    if question:
        start_time = time.time()

        with st.spinner("Searching the web..."):
            try:
                # Fetch data and citations from web sources
                web_data = fetch_data(question)
                citations = fetch_citations(question)

                # Create prompt with citation instructions and web data
                prompt = f"""Answer the following question in plain English using the provided data. Follow these rules:
1. Use numbered citations like [1], [2], etc., in the answer
2. After the answer, add 'Citations:' followed by:
   - Numbered list of sources
   - Include URLs when available
   - Use reliable web sources

Question: {question}

Data: {web_data}
"""

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

                # Display relevance and accuracy graph
                st.sidebar.subheader("Relevance & Accuracy Analysis")
                data = pd.DataFrame({
                    'Metric': ['Relevance', 'Accuracy'],
                    'Score': [relevance_score, accuracy_score]
                })
                st.sidebar.bar_chart(data.set_index('Metric'))

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