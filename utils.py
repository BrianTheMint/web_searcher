from urllib.parse import urlparse

def save_url(url):
    with open("URLs.txt", "a") as file:
        file.write(url + "\n")
    print(f"Visited URL: {url}")

def save_found_url(url, keyword, context):
    with open("found.txt", "a") as file:
        file.write(f"URL: {url}\nKeyword: {keyword}\nContext: {context}\n\n")
    print(f"Found keyword '{keyword}' in URL: {url}\nContext: {context}")

def get_urls_to_search(filename):
    with open(filename, "r") as file:
        return [line.strip() for line in file.readlines()]

def get_base_domains(urls):
    return {urlparse(url).netloc for url in urls}