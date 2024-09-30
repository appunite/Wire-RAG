import aiohttp
import asyncio
import time

async def handle_rate_limit(headers) -> None:
    """
    Handle GitHub API rate limit by checking the 'X-RateLimit-Reset' header.
    If the rate limit is hit, this function will sleep until the rate limit resets.
    """
    if 'X-RateLimit-Reset' in headers:
        reset_time = int(headers['X-RateLimit-Reset'])
        current_time = int(time.time())
        sleep_duration = reset_time - current_time
        if sleep_duration > 0:
            print(f"Rate limit hit. Sleeping for {sleep_duration} seconds.")
            await asyncio.sleep(sleep_duration)
    else:
        # Sleep for a fixed time in case of abuse detection
        print(f"Sleeping for 60 seconds due to potential abuse detection.")
        await asyncio.sleep(60)


async def fetch_repositories(session: aiohttp.ClientSession, org_name: str,
                             api_key: str, repo_limit=None) -> list[dict]:
    """
    Returns a list of repositories in the given organization.
    Each repository is represented as a dictionary with repository metadata.
    If repo_limit is provided, only that number of repositories is fetched.
    This function handles rate limiting and retry logic for 403 errors.
    """
    all_repos = []
    page = 1

    url = f"https://api.github.com/orgs/{org_name}/repos"
    headers = {
        "Authorization": f"token {api_key}",
        "Accept": "application/vnd.github.v3+json"
    }

    while True:
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
            elif response.status == 403:
                print(f"403 error for {org_name}. Checking for rate limits or abuse detection.")
                await handle_rate_limit(response.headers)
            else:
                print(f"Error fetching repositories for {org_name}: {response.status}")
                break

    return all_repos


async def fetch_last_modified_date(session: aiohttp.ClientSession, repo_full_name: str,
                                   file_path: str, api_key: str) -> str:
    """
    Fetches the last commit date for a given file in the repository by checking its commit history.
    Returns the date in ISO 8601 format (e.g., "2023-09-26T12:34:56Z").
    This function handles rate limiting and retry logic for 403 errors.
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

    while True:
        async with session.get(url, headers=headers, params=params) as response:
            if response.status == 200:
                commits = await response.json()
                if commits:
                    return commits[0]['commit']['committer']['date']  # Last commit date
                else:
                    return "Unknown"  # If no commits found, return "Unknown"
            elif response.status == 403:
                # Sleep for rate limit handling or abuse detection and then retry
                await handle_rate_limit(response.headers)
            else:
                print(f"Error fetching date for {repo_full_name}/{file_path}: {response.status}")
                return "Unknown"


async def fetch_file_content(session: aiohttp.ClientSession, url: str) -> str:
    """
    Fetch the content of the given file URL using aiohttp.
    This function handles rate limiting and retry logic for 403 errors.
    """
    while True:
        async with session.get(url) as response:
            if response.status == 200:
                return await response.text()
            elif response.status == 403:
                # Sleep for rate limit handling or abuse detection and then retry
                await handle_rate_limit(response.headers)
            else:
                print(f"Failed to fetch file: {response.status}")
                return ""


async def fetch_repo_contents(session: aiohttp.ClientSession, repo_full_name: str,
                              api_key: str, path="") -> list[dict]:
    """
    Returns the contents of a given repository, which can include files and directories.
    The contents are represented as a list of dictionaries.
    This function handles rate limiting and retry logic for 403 errors.
    """
    url = f"https://api.github.com/repos/{repo_full_name}/contents/{path}"
    headers = {
        "Authorization": f"token {api_key}",
        "Accept": "application/vnd.github.v3+json"
    }

    while True:
        async with session.get(url, headers=headers) as response:
            if response.status == 200:
                # Successfully fetched the content
                return await response.json()
            elif response.status == 403:
                # Sleep for rate limit handling or abuse detection and then retry
                await handle_rate_limit(response.headers)
            else:
                # Other errors (e.g., 404, 500)
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
                'content': await fetch_file_content(session, item['download_url']),
                'metadata': {
                    'url': item['html_url'],
                    'title': repo_full_name.split('/')[-1] + '/' + item['path'],
                    'headline': '', # url_scraper document has this field
                    'date': await fetch_last_modified_date(session, repo_full_name=repo_full_name,
                                                           file_path=item['path'], api_key=api_key)
                }
            })
        elif (item['type'] == 'dir' and
              item['name'] not in [".github"]):  # If it's a directory, recursively fetch contents
            md_files += await fetch_md_files(session, repo_full_name, api_key, item['path'])

    return md_files


async def scrape_md_files(org_name: str, api_key: str, repo_limit=None) -> list[dict]:
    """
    Main function to scrape .md files from all repositories in the organization.
    Returns a list of dictionaries containing the repo_full_name, path, self_url,
    html_url, git_url, download_url and last_modified.
    """
    # Use this if you are having error with ssl
    # async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(ssl=ssl.create_default_context(cafile=certifi.where()))) as session:
    async with aiohttp.ClientSession() as session:
        repos = await fetch_repositories(session, org_name, api_key, repo_limit)

        # Create async tasks for each repo to fetch .md files concurrently
        tasks = [fetch_md_files(session, repo['full_name'], api_key) for repo in repos]
        all_md_files = await asyncio.gather(*tasks)

        # Flatten the list of lists into a single list
        return [md_file for repo_files in all_md_files for md_file in repo_files]
