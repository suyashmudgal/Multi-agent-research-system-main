from langgraph.prebuilt import create_react_agent
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from tools import web_search, search, scrape_url, scrape
from dotenv import load_dotenv
import os

load_dotenv()

# Model setup 
DEFAULT_MODEL = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")
FALLBACK_MODEL = "llama-3.1-8b-instant"

def get_groq_api_key(api_key=None):
    key = api_key or os.getenv("GROQ_API_KEY")
    if not key:
        try:
            import streamlit as st
            if hasattr(st, "secrets") and "GROQ_API_KEY" in st.secrets:
                key = st.secrets["GROQ_API_KEY"]
        except Exception:
            pass
    return key or ""

def get_llm(model=None, max_tokens=None, api_key=None):
    key = get_groq_api_key(api_key)
    m = model or DEFAULT_MODEL
    kwargs = {"model": m, "temperature": 0, "max_retries": 3}
    if key:
        kwargs["api_key"] = key
    if max_tokens:
        kwargs["max_tokens"] = max_tokens
    return ChatGroq(**kwargs)

# 1st agent: Search Agent
def build_search_agent(model=None, api_key=None):
    prompt_msg = (
        "You are an autonomous research search agent. "
        "Use the search or web_search tool once with a targeted, keyword-rich query to find recent, reliable sources. "
        "After getting results, synthesize key findings clearly, include the source URLs found, and stop immediately."
    )
    return create_react_agent(
        get_llm(model, api_key=api_key),
        tools=[search, web_search],
        prompt=prompt_msg
    )

# 2nd agent: Reader Agent
def build_reader_agent(model=None, api_key=None):
    prompt_msg = (
        "You are a research reader agent. "
        "Inspect the search findings, identify the most authoritative URL, and call scrape_url with that URL. "
        "Summarize 3-5 factual insights from the scraped content and stop."
    )
    return create_react_agent(
        get_llm(model, api_key=api_key),
        tools=[scrape_url, scrape],
        prompt=prompt_msg
    )

# Writer chain 
writer_prompt = ChatPromptTemplate.from_messages([
    ("system", "You are an expert research writer. Write clear, structured, and insightful reports with proper citations."),
    ("human", """Write a detailed research report on the topic below.

Topic: {topic}

Research Gathered:
{research}

Structure the report with the following clear sections:
- Executive Summary
- Key Findings & In-depth Analysis (minimum 3 well-explained points)
- Future Implications / Outlook
- References & Sources (list all URLs discovered)

Be detailed, factual, and professional."""),
])

def build_writer_chain(model=None, api_key=None):
    return writer_prompt | get_llm(model, api_key=api_key) | StrOutputParser()

# Critic chain 
critic_prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a sharp, constructive research critic. Evaluate objectively and be direct."),
    ("human", """Review the research report below and evaluate it strictly.

Report:
{report}

Provide your evaluation formatted as:
Score: [X/10]

Strengths:
- [Point 1]
- [Point 2]

Weaknesses / Gaps:
- [Point 1]
- [Point 2]

Final Recommendation:
[1-2 sentences on how to improve or finalize]"""),
])

def build_critic_chain(model=None, api_key=None):
    return critic_prompt | get_llm(model, api_key=api_key) | StrOutputParser()

# Lazy wrappers for backward compatibility (prevents import-time crash when API keys are not yet set)
class _LazyRunnable:
    def __init__(self, builder_fn):
        self._builder = builder_fn
    def invoke(self, *args, **kwargs):
        return self._builder().invoke(*args, **kwargs)

class _LazyLLM:
    def invoke(self, *args, **kwargs):
        return get_llm().invoke(*args, **kwargs)
    def __getattr__(self, name):
        return getattr(get_llm(), name)

writer_chain = _LazyRunnable(build_writer_chain)
critic_chain = _LazyRunnable(build_critic_chain)
llm = _LazyLLM()
