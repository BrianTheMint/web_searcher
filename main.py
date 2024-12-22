import sys
from crawler import crawl  # Ensure you import the crawl function from crawler.py

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python main.py <regex1> <regex2> ...")
        sys.exit(1)

    keywords = sys.argv[1:]

    try:
        with open('subreddits.txt', 'r') as file:
            subreddits = file.readlines()
    except FileNotFoundError:
        print("Error: 'subreddits.txt' file not found.")
        sys.exit(1)

    crawl(subreddits, keywords)