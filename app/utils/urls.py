import re
from urllib.parse import urlparse

URL_REGEX = re.compile(
    r'(?:(?:https?|ftp)://)?'
    r'(?:\S+(?::\S*)?@)?'
    r'(?:'
    r'(?!(?:10|127)(?:\.\d{1,3}){3})'
    r'(?!(?:169\.254|192\.168)(?:\.\d{1,3}){2})'
    r'(?!172\.(?:1[6-9]|2\d|3[0-1])(?:\.\d{1,3}){2})'
    r'(?:[1-9]\d?|1\d\d|2[01]\d|22[0-3])'
    r'(?:\.(?:1?\d{1,2}|2[0-4]\d|25[0-5])){2}'
    r'(?:\.(?:[1-9]\d?|1\d\d|2[0-4]\d|25[0-4]))'
    r'|'
    r'(?:(?:[a-z\u00a1-\uffff0-9]-*)*[a-z\u00a1-\uffff0-9]+)'
    r'(?:\.(?:[a-z\u00a1-\uffff0-9]-*)*[a-z\u00a1-\uffff0-9]+)*'
    r'(?:\.(?:[a-z\u00a1-\uffff]{2,}))'
    r'\.?'
    r')'
    r'(?::\d{2,5})?'
    r'(?:[/?#]\S*)?',
    re.IGNORECASE
)

def extract_urls(text: str) -> list[str]:
    """Extracts a list of valid URLs from a text."""
    if not text:
        return []
    
    matches = URL_REGEX.findall(text)
    urls = []
    for match in matches:
        if not match.startswith(('http://', 'https://')):
            match = 'https://' + match
        
        try:
            parsed = urlparse(match)
            if parsed.scheme and parsed.netloc:
                urls.append(match)
        except Exception:
            continue
            
    return urls

def is_valid_url(url: str) -> bool:
    """Checks if a single string is a valid URL."""
    try:
        parsed = urlparse(url)
        return bool(parsed.scheme and parsed.netloc)
    except Exception:
        return False
