import httpx
from bs4 import BeautifulSoup
from readability import Document
from loguru import logger

async def fetch_and_extract_content(url: str) -> str:
    """Fetch URL and extract main content using Readability and BeautifulSoup."""
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        async with httpx.AsyncClient(timeout=30.0, follow_redirects=True) as client:
            response = await client.get(url, headers=headers)
            response.raise_for_status()
            html = response.text

        # Use readability to extract the main content
        doc = Document(html)
        summary_html = doc.summary()
        
        # Use BeautifulSoup to clean up HTML tags and get pure text
        soup = BeautifulSoup(summary_html, 'lxml')
        text = soup.get_text(separator='\n', strip=True)
        
        # Basic cleanup
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        cleaned_text = '\n'.join(lines)
        
        # Truncate if too long (rough token limit protection)
        max_chars = 20000
        if len(cleaned_text) > max_chars:
            cleaned_text = cleaned_text[:max_chars] + "\n\n[Content truncated due to length...]"
            
        return cleaned_text
        
    except httpx.HTTPStatusError as e:
        logger.error(f"HTTP error fetching {url}: {e}")
        return f"Error: Could not access the webpage (HTTP {e.response.status_code})."
    except Exception as e:
        logger.error(f"Error fetching/extracting {url}: {e}")
        return "Error: Could not extract content from the provided URL."
