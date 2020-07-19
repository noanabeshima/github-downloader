# Download all GitHub repositories
This is a tool for downloading the ~192K GitHub repositories that are more than 100 stars and smaller than a gigabyte.

To download the repositories stored in `github_repositories.csv`, simply run `python download_repos.py`.
They will be saved to `./output`

## Filtering
Stored in `github_repositories.csv` are repository names along with how many stars they have and their top language. To download one particular language, or a subset of the repositories by number of stars, you can filter the file and then run `download_repos.py`.

## Replication
To replicate downloading `github_repositories.csv`, in `download_repo_info.py` set

USER = {your-github-username}<br>
TOKEN = {your-github-access-token}


 and run the command `python download_repo_info.py`.

A GitHub access token can be created by following [this tutorial](https://docs.github.com/en/github/authenticating-to-github/creating-a-personal-access-token).

## Downloading repositories and extracting text with [lm-dataformat](https://github.com/leogao2/lm_dataformat)
Run `download_repo_text.py`. You might want to edit `n_threads` in the file to adjust the amount of CPU and bandwidth you use.

## How it works
We want to download information about all GitHub repositories, but API requests return at most 1000 results. There are much more than 1000 repositories! How can we get all of them?
The answer is to create lots of small queries that return <= 1000 results in such a way that every repository you're interested in will be returned by at least one query.

The way we do that here is by restricting the size of repositories queried in order to return small numbers of results per query, hopefully with the number of results right underneath 1000. We start by setting our lower bound to size 0 and our upper bound to size 5. This returns (at the time I'm writing this) 965 results. Great! We can process every repository in those first 965 results. Then we set our lower bound to our upper bound + 1 and somehow decide on a new upper bound that should hopefully return less than 1000 results. The way we do that here is we use our last query to estimate how far ahead our upper bound should be. For the range 0..5, we get 965, so there are about 965/(5-0) = 193 results every time we increase the upper bound by one. Then for 1000 results, our upper bound should be (lower_bound + (1000 results/193 results per +1 size). If GitHub tells us that we overshot and our query returned more than 1000 results, we simply use how many repositories our new (lower bound, upper bound) query returned to come up with a new estimate of a good upper bound. Finally, sometimes this new estimate returns the same upper-bound, so you need to manually ensure that the upper bound is at least one less than the previous estimate.

<br></br>
## Todo
- [x] Extend code to be able to download all repositories.
- [x] Add extra processing for language modelling, i.e. add option to convert all repositories into list(s) of plain text strings while downloading.
- [ ] Better command-line interface
