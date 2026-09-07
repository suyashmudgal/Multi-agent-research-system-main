from langchain.tools import tool 
import requests
from bs4 import BeautifulSoup
from tavily import TavilyClient
import os 
from dotenv import load_dotenv
from typing import Optional

load_dotenv()

tavily = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))

_DISCOVERED_URLS = []

@tool
def search(query: str, top_n: Optional[int] = 5, source: Optional[str] = None) -> str:
    """Search the web for recent and reliable information on a topic. Returns Titles, URLs and snippets.
    
    Args:
        query: The search query string or keywords.
        top_n: Number of results to return (default 5).
        source: Optional source filter (default None).
    """
    global _DISCOVERED_URLS
    max_results = top_n if (isinstance(top_n, int) and 1 <= top_n <= 10) else 5
    try:
        results = tavily.search(query=query, max_results=max_results)
    except Exception as e:
        return f"Search error: {e}"

    out = []
    for r in results.get('results', []):
        u = r.get('url')
        if u and u.startswith('http') and u not in _DISCOVERED_URLS:
            _DISCOVERED_URLS.insert(0, u)
        out.append(
            f"Title: {r.get('title')}\nURL: {u}\nSnippet: {r.get('content', '')[:250]}\n"
        )
    return "\n----\n".join(out)

@tool
def web_search(query: str, top_n: Optional[int] = 5, source: Optional[str] = None) -> str:
    """Search the web for recent and reliable information on a topic. Returns Titles, URLs and snippets.
    
    Args:
        query: The search query string or keywords.
        top_n: Number of results to return (default 5).
        source: Optional source filter (default None).
    """
    return search.invoke({"query": query, "top_n": top_n, "source": source})

@tool
def scrape_url(url: Optional[str] = None, cursor: Optional[int] = 0, loc: Optional[int] = 0) -> str:
    """Scrape and extract clean textual content from a web page URL.
    
    Args:
        url: The complete HTTP or HTTPS URL to fetch.
        cursor: Optional character offset (default 0).
        loc: Optional length or location limit (default 1800).
    """
    global _DISCOVERED_URLS
    target = url
    if not target or not target.startswith("http"):
        if _DISCOVERED_URLS:
            target = _DISCOVERED_URLS[0]
        else:
            return "No valid HTTP URL was provided or found to scrape."

    raw_text = ""
    # Fast path: try Tavily extract (handles dynamic JS, anti-bot protection, cleanly formats text)
    try:
        res = tavily.extract(urls=[target])
        if res and res.get("results") and res["results"][0].get("raw_content"):
            raw_text = res["results"][0]["raw_content"]
    except Exception:
        pass

    # Fallback: direct HTTP request with 4s timeout
    if not raw_text:
        try:
            resp = requests.get(
                target,
                timeout=4,
                headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
            )
            soup = BeautifulSoup(resp.text, "html.parser")
            for tag in soup(["script", "style", "nav", "footer", "header"]):
                tag.decompose()
            raw_text = soup.get_text(separator=" ", strip=True)
        except Exception as e:
            return f"Could not scrape URL {target}: {str(e)}"

    start = cursor or 0
    limit = loc if (loc and loc > 0) else 1800
    return raw_text[start:start + limit]

@tool
def scrape(url: Optional[str] = None, cursor: Optional[int] = 0, loc: Optional[int] = 0) -> str:
    """Scrape and extract clean textual content from a web page URL.
    
    Args:
        url: The complete HTTP or HTTPS URL to fetch.
        cursor: Optional character offset (default 0).
        loc: Optional length or location limit (default 1800).
    """
    return scrape_url.invoke({"url": url, "cursor": cursor, "loc": loc})
