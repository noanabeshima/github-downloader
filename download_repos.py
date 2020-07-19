'''
download_repos.py
Downloads all the repositories listed in repo_names.csv
'''

import os
import csv
from tqdm import tqdm
from joblib import Parallel, delayed

def download_repo(repo):
    file_name = repo.split("/")[-1]
    if file_name not in os.listdir("output/"):
        os.system(f'git clone --depth 1 --single-branch https://github.com/{repo} output/{file_name}')
    else:
        print(f"Already downloaded {repo}")

with open('github_repositories.csv', 'r') as f:
    csv_reader = csv.reader(f)
    repositories = list(map(tuple, csv_reader))

if 'output' not in os.listdir():
    os.makedirs('output')


repo_names = [repo[0] for repo in repositories]
Parallel(n_jobs=40, prefer="threads")(
    delayed(download_repo)(name) for name in tqdm(repo_names))