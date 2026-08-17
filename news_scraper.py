import requests
from bs4 import BeautifulSoup
import csv
import json
import time
from urllib.parse import urljoin
from urllib.robotparser import RobotFileParser
from datetime import datetime


# =========================================================
# PROJECT: WEB SCRAPER FOR HEADLINES
# =========================================================

# News sources
SOURCES = {
    "Hacker News": "https://news.ycombinator.com/",
    "BBC News": "https://www.bbc.com/news"
}

# User-Agent
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                  "AppleWebKit/537.36 (KHTML, like Gecko) "
                  "Chrome/151.0.0.0 Safari/537.36"
}


# =========================================================
# CHECK ROBOTS.TXT
# =========================================================

def allowed_by_robots(url):
    """
    Check whether scraping the website is allowed by robots.txt.
    """

    try:
        parsed_url = requests.utils.urlparse(url)

        robots_url = (
            parsed_url.scheme
            + "://"
            + parsed_url.netloc
            + "/robots.txt"
        )

        rp = RobotFileParser()
        rp.set_url(robots_url)
        rp.read()

        return rp.can_fetch(HEADERS["User-Agent"], url)

    except Exception as e:
        print("Could not check robots.txt:", e)

        # If robots.txt cannot be checked, stop scraping
        return False


# =========================================================
# FETCH WEB PAGE
# =========================================================

def fetch_page(url):
    """
    Download the webpage using requests.
    """

    try:
        print("\nFetching:", url)

        response = requests.get(
            url,
            headers=HEADERS,
            timeout=15
        )

        response.raise_for_status()

        print("Page downloaded successfully.")

        return response.text

    except requests.exceptions.Timeout:
        print("Error: Request timed out.")

    except requests.exceptions.ConnectionError:
        print("Error: Could not connect to the website.")

    except requests.exceptions.HTTPError as e:
        print("HTTP Error:", e)

    except requests.exceptions.RequestException as e:
        print("Request Error:", e)

    return None


# =========================================================
# SCRAPE HACKER NEWS
# =========================================================

def scrape_hacker_news(html):
    """
    Extract headlines and URLs from Hacker News.
    """

    soup = BeautifulSoup(html, "html.parser")

    articles = []

    rows = soup.select("tr.athing")

    for row in rows:

        title_tag = row.select_one("span.titleline > a")

        if not title_tag:
            continue

        title = title_tag.get_text(strip=True)

        link = title_tag.get("href")

        if not link:
            continue

        # Convert relative URLs into complete URLs
        link = urljoin(
            "https://news.ycombinator.com/",
            link
        )

        # Find time information
        subtext = row.find_next_sibling("tr")

        published_time = "Not available"

        if subtext:

            age_tag = subtext.select_one("span.age")

            if age_tag:
                published_time = age_tag.get_text(
                    strip=True
                )

        articles.append({
            "title": title,
            "url": link,
            "time": published_time
        })

    return articles


# =========================================================
# SCRAPE BBC NEWS
# =========================================================

def scrape_bbc_news(html):
    """
    Extract headlines from BBC News.
    """

    soup = BeautifulSoup(html, "html.parser")

    articles = []

    # BBC uses several heading levels for news cards.
    headings = soup.find_all(
        ["h2", "h3"]
    )

    seen_urls = set()

    for heading in headings:

        link_tag = heading.find("a")

        if not link_tag:
            continue

        title = heading.get_text(
            " ",
            strip=True
        )

        href = link_tag.get("href")

        if not title or not href:
            continue

        # Only collect BBC article links
        if href.startswith("/"):
            href = urljoin(
                "https://www.bbc.com",
                href
            )

        if not href.startswith(
            ("https://www.bbc.com",
             "https://www.bbc.co.uk")
        ):
            continue

        if href in seen_urls:
            continue

        seen_urls.add(href)

        articles.append({
            "title": title,
            "url": href,
            "time": "Not available"
        })

    return articles


# =========================================================
# FILTER BY KEYWORD
# =========================================================

def filter_articles(articles, keyword):
    """
    Filter headlines using a keyword.
    """

    if not keyword:
        return articles

    keyword = keyword.lower()

    filtered = []

    for article in articles:

        if keyword in article["title"].lower():
            filtered.append(article)

    return filtered


# =========================================================
# DISPLAY RESULTS
# =========================================================

def display_articles(articles):

    print("\n")
    print("=" * 80)
    print("HEADLINES")
    print("=" * 80)

    if not articles:
        print("No headlines found.")
        return

    for i, article in enumerate(articles, start=1):

        print(f"\n{i}. {article['title']}")
        print(f"   URL  : {article['url']}")
        print(f"   Time : {article['time']}")

    print("\n" + "=" * 80)


# =========================================================
# SAVE AS JSON
# =========================================================

def save_json(articles, filename="headlines.json"):

    try:

        with open(
            filename,
            "w",
            encoding="utf-8"
        ) as file:

            json.dump(
                articles,
                file,
                indent=4,
                ensure_ascii=False
            )

        print(
            f"\nJSON file created successfully: {filename}"
        )

    except Exception as e:

        print(
            "Error while saving JSON:",
            e
        )


# =========================================================
# SAVE AS CSV
# =========================================================

def save_csv(articles, filename="headlines.csv"):

    try:

        with open(
            filename,
            "w",
            newline="",
            encoding="utf-8"
        ) as file:

            writer = csv.DictWriter(
                file,
                fieldnames=[
                    "title",
                    "url",
                    "time"
                ]
            )

            writer.writeheader()

            writer.writerows(articles)

        print(
            f"CSV file created successfully: {filename}"
        )

    except Exception as e:

        print(
            "Error while saving CSV:",
            e
        )


# =========================================================
# SCRAPE ONE SOURCE
# =========================================================

def scrape_source(source_name, source_url):

    print("\n" + "=" * 80)
    print("SOURCE:", source_name)
    print("=" * 80)

    # Check robots.txt
    print("Checking robots.txt...")

    if not allowed_by_robots(source_url):

        print(
            "Scraping is not allowed by robots.txt."
        )

        return []

    print("robots.txt allows scraping.")

    # Add delay before request
    time.sleep(2)

    # Download page
    html = fetch_page(source_url)

    if not html:
        return []

    # Select correct parser
    if source_name == "Hacker News":

        articles = scrape_hacker_news(html)

    elif source_name == "BBC News":

        articles = scrape_bbc_news(html)

    else:

        articles = []

    return articles


# =========================================================
# MAIN PROGRAM
# =========================================================

def main():

    print("\n")
    print("*" * 80)
    print("        WEB SCRAPER FOR HEADLINES")
    print("*" * 80)

    print("\nAvailable sources:")

    source_names = list(SOURCES.keys())

    for i, source in enumerate(
        source_names,
        start=1
    ):
        print(f"{i}. {source}")

    print(f"{len(source_names) + 1}. All sources")

    # Select source
    try:

        choice = int(
            input(
                "\nEnter your choice: "
            )
        )

    except ValueError:

        print(
            "Invalid input. Please enter a number."
        )

        return

    # Keyword
    keyword = input(
        "\nEnter keyword to filter "
        "(press Enter for all headlines): "
    ).strip()

    all_articles = []

    # =====================================================
    # SELECT SOURCE
    # =====================================================

    if choice == len(source_names) + 1:

        # Scrape all sources

        for source_name, source_url in SOURCES.items():

            articles = scrape_source(
                source_name,
                source_url
            )

            for article in articles:

                article["source"] = source_name

            all_articles.extend(articles)

            # Delay between sources
            time.sleep(3)

    elif 1 <= choice <= len(source_names):

        source_name = source_names[
            choice - 1
        ]

        source_url = SOURCES[
            source_name
        ]

        all_articles = scrape_source(
            source_name,
            source_url
        )

        for article in all_articles:

            article["source"] = source_name

    else:

        print("Invalid choice.")
        return

    # =====================================================
    # FILTER
    # =====================================================

    all_articles = filter_articles(
        all_articles,
        keyword
    )

    # =====================================================
    # DISPLAY
    # =====================================================

    display_articles(
        all_articles
    )

    # =====================================================
    # SAVE FILES
    # =====================================================

    if all_articles:

        timestamp = datetime.now().strftime(
            "%Y%m%d_%H%M%S"
        )

        json_filename = (
            f"headlines_{timestamp}.json"
        )

        csv_filename = (
            f"headlines_{timestamp}.csv"
        )

        save_json(
            all_articles,
            json_filename
        )

        save_csv(
            all_articles,
            csv_filename
        )

    else:

        print(
            "\nNo data available to save."
        )

    print("\nProgram completed successfully.")


# =========================================================
# RUN PROGRAM
# =========================================================

if __name__ == "__main__":
    main()