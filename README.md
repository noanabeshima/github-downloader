# Download all GitHub repositories
This is a tool for downloading the ~192K GitHub repositories that are more than 100 stars and smaller than a gigabyte.

To download the repositories stored in `github_repositories.csv`, simply run `python download_repos.py`.
They will be saved to `./output`

## Filtering
Stored in `github_repositories.csv` are repository names along with how many stars they have and their top language. To download one particular language, or a subset of the repositories by number of stars, you can filter the file and then run `download_repos.py`.

## Replication
To replicate the repository-name downloading, in `download_repo_info.py` set

USER = {your-github-username}<br>
TOKEN = {your-github-access-token}


 and run the command `python download_repo_info.py`.

A GitHub access token can be created by following [this tutorial](https://docs.github.com/en/github/authenticating-to-github/creating-a-personal-access-token).


## How it works
We want to download information about all GitHub repositories, but API requests return at most 1000 results. There are many more repositories than 1000! How can we download information on all of them?
The answer is to create lots of small queries for the GitHub API that each return <= 1000 results in such a way that every repository we're interested in will be returned by at least one of our query.

The way we do that here is by restricting the minimum and maximum size of all the files in each repository queried in order to return a small numbers of results per query, any amount less than 1000. We start by setting our lower bound to size 0 and our upper bound to size 5. This returns (at the time I'm writing this) 965 results. We process every repository in those first 965 results (save the name, number of stars, and language). Then we set our lower bound to our upper bound + 1 and somehow decide on a new upper bound that should hopefully return fewer than 1000 results. The way we do that is we use the results from our last query to estimate what upper bound to choose. For repositories in the size range 0..5, the API returned 965 results, so there are about 965/(5-0) = 193 results every time we increase the upper bound by one. Then if we'd like 1000 results, an estimate of our upper bound is (lower_bound + (1000 results/193 results). If GitHub tells us that we overshot and our query returned more than 1000 results, we simply use how many repositories our new (lower bound, upper bound) query returned in order to make a new upper bound estimate. This tends to not overshoot because GitHub repositories follow a power distribution with respect to size.

<br></br>
## Todo
- [x] Extend code to be able to download all repositories.
- [ ] Add extra processing for language modelling, i.e. add option to convert all repositories into list(s) of plain text strings while downloading. **(One form of this added to branch LibreAI)**
- [ ] Add clean command line interface.
