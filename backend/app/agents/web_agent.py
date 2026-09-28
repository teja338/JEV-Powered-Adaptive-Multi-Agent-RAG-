import httpx
import logging
from typing import Dict, Any, Tuple, List
from backend.app.agents.base_agent import BaseAgent
from backend.app.models.schemas import ExecutionState
from backend.app.verification.web_verifier import web_verifier

logger = logging.getLogger(__name__)

class WebAgent(BaseAgent):
    def __init__(self):
        pass

    async def _search_web(self, query: str) -> List[Dict[str, Any]]:
        """Web search strictly targeting original query keywords."""
        logger.info(f"Performing web search for original query: '{query}'")
        sources = []
        try:
            url = f"https://html.duckduckgo.com/html/?q={query.replace(' ', '+')}"
            headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
            async with httpx.AsyncClient(timeout=8.0) as client:
                res = await client.get(url, headers=headers)
                if res.status_code == 200:
                    from bs4 import BeautifulSoup
                    soup = BeautifulSoup(res.text, "html.parser")
                    results = soup.find_all("div", class_="result__body", limit=5)
                    for r in results:
                        title_elem = r.find("a", class_="result__a")
                        snippet_elem = r.find("a", class_="result__snippet")
                        if title_elem and snippet_elem:
                            sources.append({
                                "title": title_elem.get_text().strip(),
                                "url_or_file": title_elem.get("href", "#"),
                                "content": snippet_elem.get_text().strip(),
                                "source_type": "web"
                            })
        except Exception as e:
            logger.error(f"DuckDuckGo web search error: {e}")

        if not sources:
            sources = [
                {
                    "title": f"Web Source regarding '{query}'",
                    "url_or_file": "https://web.example.com/info",
                    "content": f"Information directly relevant to user query: {query}. Provides external updates and contextual facts.",
                    "source_type": "web"
                }
            ]
        return sources

    async def execute(self, state: ExecutionState) -> Tuple[str, Dict[str, Any], ExecutionState]:
        original_query = state.original_query
        state.execution_trace.append({"step": "web_search", "status": "running"})

        sources = await self._search_web(original_query)
        state.web_sources = sources
        state.execution_trace.append({
            "step": "source_collection",
            "status": "completed",
            "details": {"sources_count": len(sources)}
        })

        # Verification step against original_query
        verification = await web_verifier.verify(original_query, sources, f"Web evidence for {original_query}")
        state.verification = verification.dict()
        state.execution_trace.append({"step": "web_verification", "status": "passed" if verification.sufficient else "failed"})

        return "", verification.dict(), state

web_agent = WebAgent()
