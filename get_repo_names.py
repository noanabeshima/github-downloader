'''
get_repo_names.py

Downloads the names of GitHub repositories as a json list, repo_names.json.
EG: ['noanabeshima/github-scraper', 'deepmind/dm-haiku']
'''

import os
import json
import time
import math
import pickle
import requests
from tqdm import tqdm
import fire

def save_ckpt(last_letter_pair, repo_names):
    print(f"Saving checkpoint {last_letter_pair}...")
    with open('repo_ckpt.pkl', 'wb') as f:
        pickle.dump((last_letter_pair, repo_names), f)

def get_letter_pairs():
    alphabet = 'abcdefghijklmnopqrstuvwxyz'
    letter_pairs = []
    for letter in alphabet:
        for other_letter in alphabet:
            letter_pairs.append(letter + other_letter)
    
    return letter_pairs

def scrape_repos(user: str = "your-github-username",
                 token: str = "your-github-authentication-token",
                 min_stars: int = 100,
                 ):
    letter_pairs = get_letter_pairs()

    # To ensure we comply with GitHub's Search API rate limit rules
    # 30 requests per minute maximum
    # https://developer.github.com/v3/#rate-limiting
    remaining_requests = 30

    # If pickled checkpoint exists, load it.
    # Otherwise, intialize repo_names as an empty list
    if 'repo_ckpt.pkl' in os.listdir():
        # Load checkpoint
        with open('repo_ckpt.pkl', 'rb') as f:
            last_pair, repo_names = pickle.load(f)
        print(f"Loading from {last_pair}")
        starting_index = letter_pairs.index(last_pair)
        letter_pairs = letter_pairs[starting_index:]
    else:
        repo_names = []

    # For each combination of letter pair and each page in 1..10, query the GitHub API
    for i, letter_pair in enumerate(letter_pairs):  
        if (i + 1) % 3 == 0:
            save_ckpt(letter_pair, repo_names)
        print("Current letter pair:", letter_pair)

        for page in range(1, 11):
            remaining_requests -= 1

            if remaining_requests != 0:
                pass
            else:
                print("Sleeping 60 seconds to stay under GitHub API rate limit...")
                time.sleep(60)
                remaining_requests = 30
                    
            r = requests.get(
                   f'https://api.github.com/search/repositories?q={letter_pair}+stars:>{min_stars}&per_page=100&page={page}',
                   auth = (user, token)
                   )

            if page == 1:
                n_repos_returned = r.json()['total_count']
                print("Repositories returned:", n_repos_returned)
                n_query_pages = min(math.ceil(n_repos_returned/100), 10) # GitHub API capped at 1000 results

            if r.status_code == 403:
                print("API rate limit exceeded.")
                save_ckpt(letter_pair, repo_names)
                print("Exiting program.")
                exit()
            if r.status_code == 422:
                # No more pages available
                break # Exit letter_pair loop
            try:
                assert r.status_code == 200
            except:
                print(f"Unexpected status code. Status code returned is {r.status_code}")
                print(r.text)
                save_ckpt(letter_pair, repo_names)
                print("Exiting program.")
                exit()
            
            for repository in r.json()['items']:
                repo_names.append(repository['full_name']) # eg noanabeshima/github-scraper

            if page >= n_query_pages:
                # No more pages available
                break

        print(f"{len(set(repo_names))} unique repositories scraped in total.")

    before = len(repo_names)
    repo_names = list(set(repo_names)) # Remove duplicates
    after = len(repo_names)

    print(f"{round((after / (before + .001))/100, 2)}% of repositories remaining after removing duplicates")


    print("Saving repository names to repo_names.json ...")
    with open("repo_names.json", mode="w") as f:
        f.write(json.dumps(repo_names))

if __name__ == '__main__':
    fire.Fire(scrape_repos)
