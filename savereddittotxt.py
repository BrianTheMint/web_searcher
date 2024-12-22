import praw
import os
import argparse
import requests
import re
from waybackpy import WaybackMachineCDXServerAPI
from concurrent.futures import ThreadPoolExecutor

def save_text_to_file(text, filename):
    with open(filename, 'a', encoding='utf-8') as file:
        file.write(text + "\n")
        print(text)

def save_media_to_file(url, title, output_dir):
    response = requests.get(url)
    if response.status_code == 200:
        # Sanitize the title to create a valid filename
        sanitized_title = re.sub(r'[\\/*?:"<>|]', "", title)
        extension = url.split('.')[-1]
        filename = os.path.join(output_dir, f"{sanitized_title}.{extension}")
        with open(filename, 'wb') as file:
            file.write(response.content)
        print(f"Saved media: {filename}")

def fetch_from_wayback(url):
    try:
        cdx_api = WaybackMachineCDXServerAPI(url)
        wayback_url = cdx_api.newest().archive_url
        response = requests.get(wayback_url)
        if response.status_code == 200:
            return response.text
    except Exception as e:
        print(f"Error fetching from Wayback Machine: {e}")
    return None

def scrape_reddit(subreddit_name, output_file, output_dir, post_limit):
    reddit = praw.Reddit(
        client_id='JP7jpmyTK5zprsp6wlpiCA',  # Replace with your client ID
        client_secret='W2pfcQ_Q9oXsCBgSjo4g9Lf_391mrg',  # Replace with your client secret
        user_agent='txtfile/1.0'  # Replace with your user agent
    )

    subreddit = reddit.subreddit(subreddit_name)
    after = None
    total_count = 0

    while total_count < post_limit:
        submissions = subreddit.new(limit=100, params={'after': after})
        count = 0
        for submission in submissions:
            user_info = f"User: {submission.author.name}\n"
            save_text_to_file(user_info + submission.title, output_file)
            save_text_to_file(submission.selftext, output_file)
            save_text_to_file("\n================================================================================================================================================\n", output_file)

            if submission.url.endswith(('.jpg', '.jpeg', '.png', '.gif', '.mp4', '.webm')):
                save_media_to_file(submission.url, submission.title, output_dir)

            submission.comments.replace_more(limit=0)
            for comment in submission.comments.list():
                if comment.author:
                    comment_info = f"User: {comment.author.name}\n"
                    save_text_to_file(comment_info + comment.body, output_file)
                else:
                    wayback_content = fetch_from_wayback(f"https://www.reddit.com{comment.permalink}")
                    if wayback_content:
                        save_text_to_file("User: [deleted]\n" + wayback_content, output_file)
                    else:
                        save_text_to_file("User: [deleted]\n[Content not available]", output_file)
                save_text_to_file("\n======\n", output_file)
            count += 1
            total_count += 1

            if total_count >= post_limit:
                break

        if count == 0:
            break
        after = submission.name

def get_subreddits_from_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        return [line.strip() for line in file if line.strip()]

def main(subreddit_file, single_subreddit, output_dir, post_limit):
    reddit = praw.Reddit(
        client_id='JP7jpmyTK5zprsp6wlpiCA',  # Replace with your client ID
        client_secret='W2pfcQ_Q9oXsCBgSjo4g9Lf_391mrg',  # Replace with your client secret
        user_agent='txtfile/1.0'  # Replace with your user agent
    )

    if single_subreddit:
        subreddits = [single_subreddit]
    else:
        subreddits = get_subreddits_from_file(subreddit_file)

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    with ThreadPoolExecutor() as executor:
        futures = []
        for subreddit in subreddits:
            subreddit_output_dir = os.path.join(output_dir, subreddit)
            if not os.path.exists(subreddit_output_dir):
                os.makedirs(subreddit_output_dir)
            output_file = os.path.join(subreddit_output_dir, f"{subreddit}.txt")
            if os.path.exists(output_file):
                os.remove(output_file)
            futures.append(executor.submit(scrape_reddit, subreddit, output_file, subreddit_output_dir, post_limit))

        for future in futures:
            future.result()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Scrape Reddit and save to a file.")
    parser.add_argument('--subreddit-file', type=str, help="Path to the file containing subreddits to scrape.")
    parser.add_argument('--single-subreddit', type=str, help="Specify a single subreddit to scrape.")
    parser.add_argument('output_dir', type=str, help="Directory to save images and text files.")
    parser.add_argument('--post-limit', type=int, default=100, help="Number of posts to download per subreddit.")

    args = parser.parse_args()

    if not args.subreddit_file and not args.single_subreddit:
        parser.error("You must specify either --subreddit-file or --single-subreddit")

    main(args.subreddit_file, args.single_subreddit, args.output_dir, args.post_limit)