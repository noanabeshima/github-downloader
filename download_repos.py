import os
import json
from tqdm import tqdm
from joblib import Parallel, delayed

def download_repo(repo):
    file_name = repo.split("/")[-1]
    if file_name not in os.listdir("output/"):
        os.system(f'git clone --depth 1 --single-branch https://github.com/{repo} output/{file_name}')
    else:
        print(f"Already downloaded {repo}")

with open('repo_names.json', 'r') as f:
    repo_names = json.load(f)

if 'output' not in os.listdir():
    os.makedirs('output')

Parallel(n_jobs=40, prefer="threads")(
    delayed(download_repo)(repo) for repo in tqdm(repo_names))