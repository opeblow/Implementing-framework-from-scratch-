# WebPull Agent 🕸️🤖

*A powerful, modular AI research agent* that can *search Google, scrape websites, fetch Wikipedia summaries, get live news, and check weather* — all powered by *GPT-4o* and a custom agent framework.

Built with *six core building blocks*: Intelligence, Memory, Tools, Validation, Recovery, and Human Feedback.


---

## Features

- *Google Search* – Get top 5 real-time search results
- *Website Scraper* – Extract clean text from any public URL (up to 2000 chars)
- *Wikipedia Lookup* – Instant summaries with source links
- *Live News Headlines* – Topic-based news from Google News
- *Weather Anywhere* – Current conditions using wttr.in
- *Smart Tool Calling* – Agent decides when and how to use tools
- *Memory & Context* – Remembers conversation history
- *Error Recovery* – Auto-retries failed operations
- *Human-in-the-Loop* – Optional approval before actions
- *CLI Commands* – Quick shortcuts: weather london, wiki Python, search AI tools

---

## Demo

```bash
You: What's the weather in Tokyo?
Assistant: Currently in Tokyo it's 18°C (64°F), partly cloudy with 72% humidity. Feels like 17°C.

You: Latest news on quantum computing
Assistant: Here are the top stories...
1. Google claims quantum supremacy again...
   Link: https://news.google.com/...

You: wiki Neuralink
Assistant: Neuralink is an American neurotechnology company founded by Elon Musk...
   Read more: https://en.wikipedia.org/wiki/Neuralink

git clone https://github.com/opeblow/implementing-framework-from-scratch.git
cd webpull-agent

OPENAI_API_KEY=sk-your-actual-key-here

python agent.py

============================================================
WEB PULL AGENT
============================================================

 Research Agent is ready:
You: Tell me about black holes
Assistant: A black hole is a region of spacetime where gravity is so strong...

You: weather Paris
 Weather in Paris
 Temperature: 15°C (59°F)
 Condition: Light rain
 Humidity: 88%
 Wind Speed: 12 km/h
 Feels like: 14°C (57°F)


 webpull-agent/
├── agent.py              # Main script + all tools
├── agent_framework.py    # Core agent architecture (6 blocks)
├── .env.example          # Template for API key
├── requirements.txt      # (optional) pin versions
└── README.md
Tech StackPython 3.10+
OpenAI GPT-4o
BeautifulSoup4 – Web scraping
Requests – HTTP calls
Pydantic – Structured outputs & validation
python-dotenv – Environment management

EMAIL:opeblow2021@gmail.com

