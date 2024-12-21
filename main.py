import sys
from crawler import crawl
from utils import get_urls_to_search, get_base_domains

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python main.py <keyword1> <keyword2> ...")
        sys.exit(1)

    keywords = sys.argv[1:]
    urls = get_urls_to_search("to_search.txt")
    base_domains = get_base_domains(urls)
    for url in urls:
        crawl(url, keywords, base_domains)