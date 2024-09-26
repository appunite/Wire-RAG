import aiohttp
import asyncio


async def fetch_repositories(session: aiohttp.ClientSession, org_name: str,
                             api_key: str, repo_limit=None) -> list[dict]:
    """
    Returns a list of repositories in the given organization.
    Each repository is represented as a dictionary with repository metadata.
    If repo_limit is provided, only that number of repositories is fetched.
    """
    all_repos = []
    page = 1

    while True:
        url = f"https://api.github.com/orgs/{org_name}/repos"
        headers = {
            "Authorization": f"token {api_key}",
            "Accept": "application/vnd.github.v3+json"
        }

        if repo_limit is not None and 0 < repo_limit <= 100:
            # Maximum of 100 items per page
            params = {"per_page": repo_limit, "page": page}
        else:
            params = {"per_page": 100, "page": page}

        async with session.get(url, headers=headers, params=params) as response:
            if response.status == 200:
                repos = await response.json()
                if not repos:
                    break  # Stop when no more repositories are found
                all_repos.extend(repos)

                # Respect the repo_limit if it is set
                if repo_limit and len(all_repos) >= repo_limit:
                    return all_repos[:repo_limit]  # Return only up to the repo_limit

                page += 1  # Move to the next page for pagination
            else:
                print(f"Error fetching repositories for {org_name}: {response.status}")
                break

    return all_repos


async def fetch_repo_contents(session: aiohttp.ClientSession, repo_full_name: str,
                              api_key: str, path="") -> list[dict]:
    """
    Returns the contents of a given repository, which can include files and directories.
    The contents are represented as a list of dictionaries.
    """
    url = f"https://api.github.com/repos/{repo_full_name}/contents/{path}"
    headers = {
        "Authorization": f"token {api_key}",
        "Accept": "application/vnd.github.v3+json"
    }
    async with session.get(url, headers=headers) as response:
        if response.status == 200:
            return await response.json()
        else:
            print(f"Error fetching contents for {repo_full_name}/{path}: {response.status}")
            return []


async def fetch_md_files(session: aiohttp.ClientSession, repo_full_name: str,
                         api_key: str, path="") -> list[dict]:
    """
    Recursively fetches all Markdown (.md) files from the repository and directories.
    Returns a list of dictionaries with the file name, download URL, and other metadata.
    """
    contents = await fetch_repo_contents(session, repo_full_name, api_key, path)
    md_files = []

    for item in contents:
        if item['type'] == 'file' and item['name'].endswith('.md'):
            # Fetch .md file along with its download URL and other metadata
            md_files.append({
                'repo_full_name': repo_full_name,
                'path': item['path'],
                'self_url': item['url'],
                'html_url': item['html_url'],
                'git_url': item['git_url'],
                'download_url': item['download_url'],
                'last_modified': ''  # Placeholder for last modified date
            })
        elif item['type'] == 'dir':  # If it's a directory, recursively fetch contents
            md_files += await fetch_md_files(session, repo_full_name, api_key, item['path'])

    return md_files


async def fetch_last_modified_date(session: aiohttp.ClientSession, repo_full_name: str,
                                   file_path: str, api_key: str) -> str:
    """
    Fetches the last commit date for a given file in the repository by checking its commit history.
    Returns the date in ISO 8601 format (e.g., "2023-09-26T12:34:56Z").
    """
    url = f"https://api.github.com/repos/{repo_full_name}/commits"
    headers = {
        "Authorization": f"token {api_key}",
        "Accept": "application/vnd.github.v3+json"
    }
    params = {
        "path": file_path,  # Specify the file path to get commits for this specific file
        "per_page": 1,  # We only need the latest commit, so limit the result to 1
    }

    async with session.get(url, headers=headers, params=params) as response:
        if response.status == 200:
            commits = await response.json()
            if commits:
                return commits[0]['commit']['committer']['date']  # Last commit date
            else:
                return "Unknown"  # If no commits found, return "Unknown"
        else:
            print(f"Error fetching commit info for {repo_full_name}/{file_path}: {response.status}")
            return "Unknown"


async def scrape_md_files(org_name: str, api_key: str, repo_limit=None) -> list[dict]:
    """
    Main function to scrape .md files from all repositories in the organization.
    Returns a list of dictionaries containing the repo_full_name, path, self_url,
    html_url, git_url, download_url and last_modified.
    """
    async with aiohttp.ClientSession() as session:
        repos = await fetch_repositories(session, org_name, api_key, repo_limit)

        # Create async tasks for each repo to fetch .md files concurrently
        tasks = [fetch_md_files(session, repo['full_name'], api_key) for repo in repos]

        all_md_files = await asyncio.gather(*tasks)

        # Flatten the list of lists into a single list
        md_files = [md_file for repo_files in all_md_files for md_file in repo_files]

        for md_file in md_files:
            md_file['last_modified'] = await fetch_last_modified_date(
                session,
                repo_full_name=md_file['repo_full_name'],
                file_path=md_file['path'],
                api_key=api_key
            )
        return md_files