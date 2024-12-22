import sys
import praw
import re

visited = set()

# Initialize the Reddit API client
reddit = praw.Reddit(
    client_id='3rguFN9z-UXs1SxOVdZ9jA',
    client_secret='bX2iTxQKF5JeLs-1I20l1vHDIljWvQ',
    user_agent='search-bot'
)

def save_url(url):
    # Implement the logic to save the URL
    print(f"URL saved: {url}")

def save_found_url(url, keyword, context):
    # Implement the logic to save the found URL with context
    print(f"Found URL: {url}, Keyword: {keyword}, Context: {context}")

def crawl(subreddits, keywords):
    for subreddit_name in subreddits:
        try:
            subreddit = reddit.subreddit(subreddit_name.strip())
        except Exception as e:
            print(f"Error accessing subreddit '{subreddit_name}': {e}")
            continue

        for submission in subreddit.hot(limit=10):  # Adjust the limit as needed
            print(f"Visiting submission: {submission.url}")
            submission_text = submission.title.lower() + " " + submission.selftext.lower()

            for keyword in keywords:
                for match in re.finditer(keyword, submission_text):
                    start = max(match.start() - 30, 0)
                    end = min(match.end() + 30, len(submission_text))
                    context = submission_text[start:end]
                    save_found_url(submission.url, keyword.strip(), context)

            for comment in submission.comments.list():
                if isinstance(comment, praw.models.MoreComments):
                    continue
                print(f"Visiting comment: {comment.permalink}")
                comment_text = comment.body.lower()
                for keyword in keywords:
                    for match in re.finditer(keyword, comment_text):
                        start = max(match.start() - 30, 0)
                        end = min(match.end() + 30, len(comment_text))
                        context = comment_text[start:end]
                        save_found_url(comment.permalink, keyword.strip(), context)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python crawler.py <regex1> <regex2> ...")
        sys.exit(1)

    keywords = sys.argv[1:]

    try:
        with open('subreddits.txt', 'r') as file:
            subreddits = file.readlines()
    except FileNotFoundError:
        print("Error: 'subreddits.txt' file not found.")
        sys.exit(1)

    crawl(subreddits, keywords)