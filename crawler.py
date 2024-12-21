import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import re
from utils import save_url, save_found_url

visited = set()

def crawl(url, keywords, base_domains):
    if url in visited:
        return
    visited.add(url)
    save_url(url)

    try:
        response = requests.get(url)
        response.raise_for_status()
    except requests.RequestException:
        return

    soup = BeautifulSoup(response.text, 'html.parser')
    page_text = soup.get_text().lower()

    for keyword in keywords:
        for match in re.finditer(re.escape(keyword.lower()), page_text):
            start = max(match.start() - 30, 0)
            end = min(match.end() + 30, len(page_text))
            context = page_text[start:end]
            save_found_url(url, keyword.strip(), context)

    for link in soup.find_all('a', href=True):
        next_url = urljoin(url, link['href'])
        next_domain = urlparse(next_url).netloc
        if next_url.startswith("http") and any(base_domain in next_domain for base_domain in base_domains):
            crawl(next_url, keywords, base_domains)