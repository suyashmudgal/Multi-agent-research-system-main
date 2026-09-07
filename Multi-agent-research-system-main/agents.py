from langgraph.prebuilt import create_react_agent
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from tools import web_search , scrape_url 
from dotenv import load_dotenv

import os

load_dotenv()

# model setup 
GROQ_MODEL = os.getenv("GROQ_MODEL", "openai/gpt-oss-20b")

def get_llm(model=None, max_tokens=None):
    m = model or GROQ_MODEL
    kwargs = {"model": m, "temperature": 0, "max_retries": 5}
    if max_tokens:
        kwargs["max_tokens"] = max_tokens
    return ChatGroq(**kwargs)

llm = get_llm()

# 1st agent: Search Agent
def build_search_agent(model=None):
    prompt_msg = (
        "You are an autonomous research search agent. "
        "Use the web_search tool once with a targeted query to find reliable, up-to-date sources. "
        "Synthesize the key findings clearly and include the source URLs. Stop immediately after searching."
    )
    return create_react_agent(
        get_llm(model),
        tools=[web_search],
        prompt=prompt_msg
    )

# 2nd agent: Reader Agent
def build_reader_agent(model=None):
    prompt_msg = (
        "You are a research reader agent. "
        "Inspect the search findings, choose the single most authoritative URL, "
        "and call the scrape_url tool with the exact parameter url='<full_http_url>'. "
        "CRITICAL: The 'url' parameter must be the complete web page URL string. Do not invent other parameter names like cursor or loc. "
        "After scraping, summarize 3-5 factual insights and stop."
    )
    return create_react_agent(
        get_llm(model),
        tools=[scrape_url],
        prompt=prompt_msg
    )

# writer chain 
writer_prompt = ChatPromptTemplate.from_messages([
    ("system", "You are an expert research writer. Write clear, structured and insightful reports concisely."),
    ("human", """Write a detailed research report on the topic below.

Topic: {topic}

Research Gathered:
{research}

Structure the report as:
- Introduction
- Key Findings (minimum 3 well-explained points)
- Conclusion
- Sources (list all URLs found in the research)

Be detailed, factual and professional."""),
])

def build_writer_chain(model=None):
    return writer_prompt | get_llm(model) | StrOutputParser()

writer_chain = build_writer_chain()

# critic chain 
critic_prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a sharp, constructive research critic. Be concise and direct."),
    ("human", """Review the research report below and evaluate it strictly.

Report:
{report}

Respond in this exact format:

Score: X/10

Strengths:
- ...
- ...

Areas to Improve:
- ...
- ...

One line verdict:
..."""),
])

def build_critic_chain(model=None):
    return critic_prompt | get_llm(model, max_tokens=400) | StrOutputParser()

critic_chain = build_critic_chain()

