# github-downloader
This is a tool for downloading 135,293 of the 192,205 GitHub repositories with more than 100 stars.  

To download the repositories using the pre-downloaded repository names in `repo_names.json`, simply run  
`python download_repos.py`  

To replicate the repository-name downloading, run  
`python get_repo_names.py --user {your-github-username} --token {your-github-access-token}`  

GitHub access token can be created by following [this tutorial](https://docs.github.com/en/github/authenticating-to-github/creating-a-personal-access-token).

<br></br>
#### Todo:
- [ ] Extend code to download all repositories.
- [ ] Add extra processing for language modelling (convert all repositories into list(s) of plain text strings)
