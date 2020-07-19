# github-downloader
This is a tool for downloading the ~192K GitHub repositories that are more than 100 stars and smaller than a gigabyte.

To download the repositories to `output/` using the pre-downloaded repository names in `github_repositories.csv`, simply run `python download_repos.py`.


To replicate the repository-name downloading, set

USER = <<your-github-username>>
TOKEN = <<your-github-access-token>>

in `download_repo_info.py` and run `python download_repo_info.py`.

A GitHub access token can be created by following [this tutorial](https://docs.github.com/en/github/authenticating-to-github/creating-a-personal-access-token).

How it works:
We want to download information about all GitHub repositories, but API requests return at most 1000 results. There are much more than 1000 repositories! How can we get all of them?
The answer is to create lots of small queries that return <= 1000 results in such a way that every repository you're interested in will be returned by at least one query.

The way we do that here is by restricting the size of repositories queried in order to return small numbers of results per query, hopefully right underneath 1000. We start by setting our lower bound to size 0 and our upper bound to size 5. This returns (at the time I'm writing this) 965 results. Great! We can process every repository in those first 965 results. Then we set our lower bound to our upper bound + 1 and somehow decide on a new upper bound that should hopefully return less than 1000 results. The way we do that here is we use our last query to estimate how far ahead our upper bound should be. For the range 0..5, we get 965, so there are about 965/(5-0) = 193 results every time we increase the upper bound by one. Then for 1000 results, our upper bound should be (lower_bound + (1000 results/193 results per +1 size). If GitHub tells us that we overshot and our query returned more than 1000 results, we simply use how many repositories our new (lower bound, upper bound) query returned to come up with a new estimate of a good upper bound. One extra hack required is that this sometimes returns the same upper-bound, so you need to manually set the upper bound to be at least one less than it was before.

<br></br>
#### Todo:
- [x] Extend code to download all repositories.
- [ ] Add extra processing for language modelling (convert all repositories into list(s) of plain text strings)