# 🌐 Ask the Web – AI-Powered Web Q\&A App

**Ask the Web** is a Streamlit-based application that allows users to ask natural language questions and get accurate, readable, and cited answers powered by OpenAI's GPT API and real-time web data.

> 🔍 Ask a question → 🌍 Search the web → 🤖 Get a GPT answer → 📎 View citations and analytics

---

## 🚀 Features

* 🔗 **Real-time web search** from Google, Bing, DuckDuckGo, and Brave
* 🤖 **OpenAI GPT-4o-mini** for generating natural language answers
* 🧠 **Citations** and sources for every answer
* 📊 **Answer quality metrics**: accuracy, relevance, precision, readability, etc.
* 📈 **Telemetry dashboard**: token usage, latency, API calls
* ⚡️ **Asynchronous fetching** and response caching for performance

---

## 📸 Demo

![Ask the Web Screenshot](screenshot.png) <sub>(Add your own screenshot here)</sub>

---

## 🧰 Tech Stack

* [Streamlit](https://streamlit.io/) – UI
* [OpenAI API](https://openai.com/) – LLM response generation
* [aiohttp](https://docs.aiohttp.org/) – Async HTTP requests
* [BeautifulSoup](https://www.crummy.com/software/BeautifulSoup/) – HTML parsing
* [dotenv](https://pypi.org/project/python-dotenv/) – Environment variable management
* [Python asyncio](https://docs.python.org/3/library/asyncio.html) – Asynchronous event loop

---

## 📦 Setup

### 1. Clone the Repository

```bash
git clone https://github.com/your-username/ask-the-web.git
cd ask-the-web
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure Environment Variables

Create a `.env` file in the project root:

```env
OPENAI_API_KEY=your_openai_api_key
```

### 4. Run the App

```bash
streamlit run app.py
```

---

## ✨ How It Works

1. User enters a question in the UI.
2. The app fetches real-time search results from multiple search engines using asynchronous HTTP requests.
3. Extracted snippets are passed to OpenAI's GPT model to generate a coherent answer.
4. Answer and its citations are displayed with quality metrics and performance telemetry.

---

## 📈 Metrics & Analytics

The app includes two dashboards:

* **Telemetry**: Token usage, latency, and API stats
* **Analytics**: Answer quality breakdown (relevance, factuality, precision, etc.)

> Metrics are currently placeholder values and can be enhanced with NLP techniques or similarity scoring.

---

## ✅ TODO

* [ ] Enhance web scraping with robust selectors or an API-based approach
* [ ] Use semantic search or embedding models for better web data relevance
* [ ] Implement actual metrics analysis (e.g., cosine similarity with trusted content)
* [ ] Add feedback mechanism to rate answers

---

## 🛡 Disclaimers

* This app uses AI-generated content and may contain inaccuracies.
* Web scraping is subject to the terms of service of the target websites.
* Intended for educational and experimental use.

---

## 📄 License

MIT License

---

## 🙌 Acknowledgements

* OpenAI for GPT models
* Streamlit for interactive Python UI
* Python community for async tools and web scraping libraries

---

## 📬 Contact

Created by [Joseph Kibira](https://github.com/your-username) – feel free to reach out or contribute!


