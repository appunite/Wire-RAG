import aiohttp
import asyncio
from urllib.parse import urljoin, urlparse
import re
from datetime import datetime
from bs4 import BeautifulSoup
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import requests

DATE_FORMATS = [
    '%Y-%m-%d',  # Format: 2024-09-20
    '%Y/%m/%d',  # Format: 2024/09/20
    '%m-%d-%Y',  # Format: 09-20-2024
    '%m/%d/%Y',  # Format: 09/20/2024
    '%d-%m-%Y',  # Format: 20-09-2024
    '%d/%m/%Y',  # Format: 20/09/2024
    '%d %B %Y',  # Format: 20 September 2024
    '%B %d, %Y',  # Format: September 20, 2024
    '%d %b %Y',  # Format: 20 Sep 2024 (short month)
    '%b %d, %Y',  # Format: Sep 20, 2024 (short month)
    '%d-%b-%Y',  # Format: 20-Sep-2024 (short month)
    '%b-%d-%Y',  # Format: Sep-20-2024 (short month)
    '%A, %d %B %Y',  # Format: Friday, 20 September 2024 (with weekday)
    '%A, %B %d, %Y',  # Format: Friday, September 20, 2024 (with weekday)
    '%Y.%m.%d',  # Format: 2024.09.20
    '%d.%m.%Y',  # Format: 20.09.2024 (European format)
    '%Y %b %d',  # Format: 2024 Sep 20 (short month)
    '%Y %B %d',  # Format: 2024 September 20
    '%d %B, %Y',  # Format: 20 September, 2024 (comma after day)
    '%B %d %Y'  # Format: September 20 2024 (no comma)
]

# Regular expression patterns for various date formats
DATE_PATTERNS = [
    r'\b\d{4}-\d{2}-\d{2}\b',  # Matches YYYY-MM-DD (e.g., 2024-09-20)
    r'\b\d{4}/\d{2}/\d{2}\b',  # Matches YYYY/MM/DD (e.g., 2024/09/20)
    r'\b\d{2}-\d{2}-\d{4}\b',  # Matches MM-DD-YYYY (e.g., 09-20-2024)
    r'\b\d{2}/\d{2}/\d{4}\b',  # Matches MM/DD/YYYY (e.g., 09/20/2024)
    r'\b\d{2}-\d{2}-\d{4}\b',  # Matches DD-MM-YYYY (e.g., 20-09-2024)
    r'\b\d{2}/\d{2}/\d{4}\b',  # Matches DD/MM/YYYY (e.g., 20/09/2024)
    r'\b\d{1,2}\s+[A-Za-z]+\s+\d{4}\b',  # Matches 20 September 2024
    r'\b[A-Za-z]+\s+\d{1,2},\s+\d{4}\b',  # Matches September 20, 2024
    r'\b\d{1,2}\s+[A-Za-z]{3}\s+\d{4}\b',  # Matches 20 Sep 2024 (short month)
    r'\b[A-Za-z]{3}\s+\d{1,2},\s+\d{4}\b',  # Matches Sep 20, 2024 (short month)
    r'\b\d{1,2}-[A-Za-z]{3}-\d{4}\b',  # Matches 20-Sep-2024 (short month)
    r'\b[A-Za-z]{3}-\d{1,2}-\d{4}\b',  # Matches Sep-20-2024 (short month)
    r'\b[A-Za-z]+,\s+\d{1,2}\s+[A-Za-z]+\s+\d{4}\b',  # Matches Friday, 20 September 2024 (with weekday)
    r'\b[A-Za-z]+,\s+[A-Za-z]+\s+\d{1,2},\s+\d{4}\b',  # Matches Friday, September 20, 2024 (with weekday)
    r'\b\d{4}\.\d{2}\.\d{2}\b',  # Matches YYYY.MM.DD (e.g., 2024.09.20)
    r'\b\d{2}\.\d{2}\.\d{4}\b',  # Matches DD.MM.YYYY (e.g., 20.09.2024)
    r'\b\d{4}\s+[A-Za-z]{3}\s+\d{1,2}\b',  # Matches 2024 Sep 20
    r'\b\d{4}\s+[A-Za-z]+\s+\d{1,2}\b',  # Matches 2024 September 20
    r'\b\d{1,2}\s+[A-Za-z]+,\s+\d{4}\b',  # Matches 20 September, 2024 (comma after day)
    r'\b[A-Za-z]+\s+\d{1,2}\s+\d{4}\b'  # Matches September 20 2024 (no comma)
]


# Asynchronous URL fetching with retry logic
async def fetch_urls(url_to_fetch: str, session: aiohttp.ClientSession, retries=3) -> set[str]:
    attempt = 0
    while attempt < retries:
        try:
            async with session.get(url_to_fetch, timeout=15) as response:
                if response.status != 200:
                    # print(f"Couldn't fetch {url} - status {response.status}")
                    return set()  # Return an empty set if the page doesn't load
                text_content = await response.text()
                soup = BeautifulSoup(text_content, "html.parser")
                urls = set(
                    urljoin(url_to_fetch, link['href'])
                    for link in soup.find_all('a', href=True)
                    if urlparse(urljoin(url_to_fetch, link['href'])).scheme in ('http', 'https')
                )
                # if attempt > 0: print(f"Successfully fetched URL: {url} on attempt {attempt + 1}")
                return urls
        except (aiohttp.ClientError, asyncio.TimeoutError):
            attempt += 1
            if attempt < retries:
                await asyncio.sleep(2 ** attempt)  # Exponential backoff
        except Exception as e:
            print(e)
            return set()

    print(f"Failed to fetch URL {url_to_fetch} after {retries} attempts.")
    return set()


# Check if URL should be allowed
def is_url_allowed(url_to_check: str, special_list: dict[str, list[str]] | None) -> bool:
    if special_list is None: return True

    # Return False if url is not in white_list
    if not any(url_to_check.startswith(i) for i in special_list["white_list"]): return False

    # Return False if url is in black_list
    if any(url_to_check.startswith(i) for i in special_list["black_list"]): return False
    return True


# Asynchronous scraping with blacklist/whitelist and depth handling
async def scrape_urls(current_url: str, session: aiohttp.ClientSession, max_depth: int, current_depth=0, visited=None,
                      list_data=None) -> list[str]:
    if visited is None:
        visited = []

    if current_depth > max_depth:
        return visited  # Stop recursion if depth limit exceeded

    visited.append(current_url)  # Store URL with its depth
    # Extract URLs from the current page
    urls = await fetch_urls(current_url, session)

    tasks = []
    for new_url in urls:
        if new_url not in visited and is_url_allowed(new_url, list_data):
            # Continue scraping at the next depth level if within depth limit
            if current_depth < max_depth:
                tasks.append(scrape_urls(new_url, session, max_depth, current_depth + 1, visited, list_data))

    # Await all the tasks concurrently
    await asyncio.gather(*tasks)
    return visited


# Entry point for asynchronous scraping
async def start_scraping(entry_url: str, depth: int, list_data=None) -> list[str]:
    """
    Returns list of scraped urls
    list_data - dict{'white_list': [str], 'black_list': [str]}
    """
    async with aiohttp.ClientSession() as session:
        found_urls = await scrape_urls(entry_url, session, depth, list_data=list_data)
    return found_urls



def find_all_dates_with_regex(text, date_patterns):
    """Search for all date matches using regex patterns."""
    dates = []
    for pattern in date_patterns:
        matches = re.findall(pattern, text)  # Find all matches for the pattern
        dates.extend(matches)
    return dates


def parse_date(date_str, date_formats):
    for date_format in date_formats:
        try:
            return datetime.strptime(date_str, date_format)
        except ValueError:
            pass
    return None


def get_latest_date(dates, date_formats):
    """Return the latest valid date from a list of date strings."""
    parsed_dates = [parse_date(date, date_formats) for date in dates]
    # Filter out any dates that couldn't be parsed and return the latest one
    valid_dates = [d for d in parsed_dates if d is not None]
    return max(valid_dates).strftime('%Y-%m-%d') if valid_dates else "Unknown"


def extract_date(my_soup: BeautifulSoup, date_formats, date_patterns) -> str:
    # Extract all text content to search for a date pattern
    text_content = my_soup.get_text(separator=' ', strip=True)

    # Use regex to find all dates in the page's text content
    dates = find_all_dates_with_regex(text_content, date_patterns)

    # Get the latest date found
    latest_date = get_latest_date(dates, date_formats)
    return latest_date


def requests_retry_session(
        retries=3,
        backoff_factor=0.3,
        status_forcelist=(500, 502, 504),
        session=None,
):
    session = session or requests.Session()
    retry = Retry(
        total=retries,
        read=retries,
        connect=retries,
        backoff_factor=backoff_factor,
        status_forcelist=status_forcelist,
    )
    adapter = HTTPAdapter(max_retries=retry)
    session.mount('http://', adapter)
    session.mount('https://', adapter)
    return session


def extract_content_and_metadata(url: str, date_formats: list[str], date_patterns: list[str]) -> list[dict] | None:
    """
    Returns list of dictionaries {content: string, metadata: dict}
    content - cleaned html text split by headlines
    metadata - url, title, headline, date
    """
    try:
        # Use retry session for robust requests
        session = requests_retry_session()
        response = session.get(url, timeout=10)

        # Check if request was successful
        response.raise_for_status()

        soup = BeautifulSoup(response.content, 'html.parser')
        title = soup.title.string if soup.title else "Unknown"
        date = extract_date(soup, date_formats, date_patterns)

        content_by_headline = {}
        current_header = None

        # Loop through the elements, keeping track of headlines and paragraphs
        for element in soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'p', 'ul', 'ol']):
            if element.name.startswith('h'):
                # Headline
                current_header = element.get_text(strip=True)
                current_header = current_header.replace("\n", "")
                current_header = re.sub(r"\s+", " ", current_header)

            elif element.name in ['p', 'ul', 'ol'] and current_header:
                # Append the text under the last seen headline
                value = content_by_headline[current_header] if current_header in content_by_headline else ""
                new_content = element.get_text(strip=True).replace('\n', ' ')
                content_by_headline[current_header] = f"{value} {new_content}"

        result_dicts = []
        for headline, content in content_by_headline.items():
            result_dicts.append(
                {"content": content, "metadata": {"url": url, "title": title, "headline": headline, "date": date}})

        return result_dicts

    except requests.exceptions.RequestException as e:
        print(f"Error fetching {url}: {e}")
        return None