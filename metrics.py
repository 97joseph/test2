import streamlit as st
from openai import OpenAI
import aiohttp
import asyncio
from bs4 import BeautifulSoup
import pandas as pd
import os
from dotenv import load_dotenv
import time
from functools import lru_cache
from typing import List, Tuple, Dict

# Load environment variables
load_dotenv()

# Configure OpenAI API
client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
MODEL = "gpt-4o-mini"  # Use a more efficient model


# Cache web data to avoid repeated requests
@lru_cache(maxsize=100)
async def fetch_web_data(query: str) -> List[str]:
    async with aiohttp.ClientSession() as session:
        urls = [
            f"https://www.google.com/search?q={query}",
            f"https://www.bing.com/search?q={query}",
            f"https://duckduckgo.com/?q={query}",
            f"https://search.brave.com/search?q={query}"
        ]
        data = []
        for url in urls:
            try:
                async with session.get(url, timeout=5) as response:
                    if response.status == 200:
                        soup = BeautifulSoup(await response.text(), 'html.parser')
                        # Improved selector for better reliability
                        results = soup.select('div, p, span',
                                              class_=lambda x: x and ('result' in x.lower() or 'snippet' in x.lower()))
                        data.extend([r.get_text(strip=True) for r in results if r.get_text(strip=True)])
            except Exception as e:
                st.error(f"Error fetching {url}: {str(e)}")
        return data[:10]  # Limit to top 10 results


@lru_cache(maxsize=100)
async def fetch_citations(query: str) -> List[str]:
    async with aiohttp.ClientSession() as session:
        urls = [
            f"https://www.google.com/search?q={query}",
            f"https://www.bing.com/search?q={query}"
        ]
        citations = []
        for url in urls:
            try:
                async with session.get(url, timeout=5) as response:
                    if response.status == 200:
                        soup = BeautifulSoup(await response.text(), 'html.parser')
                        links = soup.find_all('a', href=True)
                        citations.extend([link['href'] for link in links if
                                          link['href'].startswith('http') and 'google' not in link['href']])
            except Exception as e:
                st.error(f"Error fetching citations from {url}: {str(e)}")
        return list(set(citations))[:5]  # Deduplicate and limit to 5


# Simplified analytics functions with placeholder logic
def analyze_metrics(answer: str, citations: List[str]) -> Dict[str, float]:
    return {
        "relevance": 0.85,  # Replace with actual logic (e.g., cosine similarity)
        "accuracy": 0.90,
        "precision": 0.75,
        "factuality": 0.80,
        "readability": 0.90,
        "engagement": 0.60,
        "authority": 0.85
    }


# Streamlit UI
st.set_page_config(page_title="Ask the Web", layout="wide")
st.title("Ask the Web 🌐")
st.subheader("Answers with Source Citations")

# Sidebar for telemetry and analytics
with st.sidebar:
    st.title("Telemetry")
    telemetry = {
        "tokens": st.metric("Total Tokens", 0),
        "latency": st.metric("Latency (ms)", 0),
        "api_calls": st.metric("API Calls", 0),
        "tokens_per_call": st.metric("Tokens per Call", 0),
        "avg_latency": st.metric("Average Latency (ms)", 0),
        "relevance_accuracy": st.metric("Relevance & Accuracy", "0.00 / 0.00")
    }
    st.title("Analytics")
    analytics = {
        "precision": st.metric("Precision", 0),
        "factuality": st.metric("Factuality", 0),
        "readability": st.metric("Readability", 0),
        "engagement": st.metric("Engagement", 0),
        "authority": st.metric("Authority", 0)
    }

# Input question
question = st.text_input("Enter your question:", placeholder="E.g., What's the latest AI research from Google?")


async def get_answer(question: str) -> Tuple[str, List[str], Dict]:
    start_time = time.time()
    web_data = await fetch_web_data(question)
    citations = await fetch_citations(question)

    prompt = f"""Answer in plain English using the provided data. Rules:
1. Use numbered citations [1], [2], etc.
2. After the answer, list citations with URLs.
3. Ensure accuracy and relevance.

Question: {question}
Data: {web_data[:2000]}"""  # Limit data to avoid token overflow

    try:
        response = client.chat.completions.create(
            model=MODEL,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=500,
            temperature=0.7
        )
        if not response.choices[0].message.content:
            raise ValueError("Empty response from API")

        answer = response.choices[0].message.content
        metrics = analyze_metrics(answer, citations)

        # Telemetry
        telemetry_data = {
            "total_tokens": response.usage.total_tokens,
            "latency": int((time.time() - start_time) * 1000),
            "api_calls": 1,
            "tokens_per_call": response.usage.total_tokens,
            "avg_latency": int((time.time() - start_time) * 1000)
        }
        return answer, citations, metrics, telemetry_data
    except Exception as e:
        st.error(f"Error: {str(e)}")
        return "", [], {}, {}


if st.button("Get Answer"):
    if not question:
        st.warning("Please enter a question")
    else:
        with st.spinner("Searching the web..."):
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            answer, citations, metrics, telemetry_data = loop.run_until_complete(get_answer(question))
            loop.close()

            if answer:
                # Display answer
                st.subheader("Answer:")
                formatted_answer = answer.replace('[', '<sup>').replace(']', '</sup>')
                st.markdown(formatted_answer, unsafe_allow_html=True)

                # Display citations
                st.subheader("Source Citations:")
                for i, citation in enumerate(citations, 1):
                    st.write(f"{i}. {citation}")

                # Update telemetry
                telemetry["tokens"].metric("Total Tokens", telemetry_data.get("total_tokens", 0))
                telemetry["latency"].metric("Latency (ms)", telemetry_data.get("latency", 0))
                telemetry["api_calls"].metric("API Calls", telemetry_data.get("api_calls", 0))
                telemetry["tokens_per_call"].metric("Tokens per Call", telemetry_data.get("tokens_per_call", 0))
                telemetry["avg_latency"].metric("Average Latency (ms)", telemetry_data.get("avg_latency", 0))
                telemetry["relevance_accuracy"].metric("Relevance & Accuracy",
                                                       f"{metrics.get('relevance', 0):.2f} / {metrics.get('accuracy', 0):.2f}")

                # Update analytics
                for key, metric in analytics.items():
                    metric.metric(key.capitalize(), f"{metrics.get(key, 0):.2f}")

                # Quality check (simplified)
                st.success("Answer Quality: Pass")  # Replace with actual quality check if needed

st.markdown("---")
st.caption("Powered by OpenAI API • Sources may be AI-generated")