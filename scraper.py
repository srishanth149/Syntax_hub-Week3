import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import time


HEADERS = {
    "User-Agent": "WebScraperForHeadlines/1.0"
}


# =========================================================
# NEWS SOURCES
# =========================================================

SOURCES = {
    "The Guardian": "https://www.theguardian.com/world/rss",
    "DW News": "https://rss.dw.com/rdf/rss-en-all",
    "Al Jazeera": "https://www.aljazeera.com/xml/rss/all.xml"
}


# =========================================================
# GENERIC RSS SCRAPER
# =========================================================

def scrape_rss(source_name, feed_url):

    try:

        response = requests.get(
            feed_url,
            headers=HEADERS,
            timeout=15
        )

        response.raise_for_status()

        soup = BeautifulSoup(
        response.content,
        "html.parser"
        )

        articles = []

        items = soup.find_all("item")

        for item in items:

            title_tag = item.find("title")
            link_tag = item.find("link")
            date_tag = item.find("pubDate")

            if not title_tag or not link_tag:
                continue

            title = title_tag.get_text(
                strip=True
            )

            link = link_tag.get_text(
                strip=True
            )

            published_time = "Not available"

            if date_tag:

                published_time = date_tag.get_text(
                    strip=True
                )

            articles.append({
                "title": title,
                "url": link,
                "time": published_time,
                "source": source_name
            })

        return articles

    except requests.exceptions.Timeout:

        raise Exception(
            f"{source_name}: Request timed out."
        )

    except requests.exceptions.ConnectionError:

        raise Exception(
            f"{source_name}: Could not connect."
        )

    except requests.exceptions.HTTPError as e:

        raise Exception(
            f"{source_name}: HTTP error {e}"
        )

    except Exception as e:

        raise Exception(
            f"{source_name}: {e}"
        )


# =========================================================
# HACKER NEWS
# =========================================================

def scrape_hacker_news():

    url = "https://news.ycombinator.com/"

    try:

        response = requests.get(
            url,
            headers=HEADERS,
            timeout=15
        )

        response.raise_for_status()

        soup = BeautifulSoup(
            response.text,
            "html.parser"
        )

        articles = []

        rows = soup.select(
            "tr.athing"
        )

        for row in rows:

            title_tag = row.select_one(
                "span.titleline > a"
            )

            if not title_tag:
                continue

            title = title_tag.get_text(
                strip=True
            )

            link = title_tag.get(
                "href"
            )

            if not link:
                continue

            link = urljoin(
                url,
                link
            )

            published_time = "Not available"

            subtext = row.find_next_sibling(
                "tr"
            )

            if subtext:

                age = subtext.select_one(
                    "span.age"
                )

                if age:

                    published_time = age.get_text(
                        strip=True
                    )

            articles.append({
                "title": title,
                "url": link,
                "time": published_time,
                "source": "Hacker News"
            })

        return articles

    except Exception as e:

        raise Exception(
            f"Hacker News: {e}"
        )


# =========================================================
# SCRAPE SELECTED SOURCE
# =========================================================

def scrape_source(source_name):

    if source_name == "Hacker News":

        return scrape_hacker_news()

    if source_name in SOURCES:

        return scrape_rss(
            source_name,
            SOURCES[source_name]
        )

    return []


# =========================================================
# SCRAPE ALL SOURCES
# =========================================================

def scrape_all_sources():

    all_articles = []

    # Hacker News
    try:

        articles = scrape_hacker_news()

        all_articles.extend(
            articles
        )

    except Exception as e:

        print(e)

    time.sleep(2)

    # RSS sources
    for source_name, feed_url in SOURCES.items():

        try:

            articles = scrape_rss(
                source_name,
                feed_url
            )

            all_articles.extend(
                articles
            )

        except Exception as e:

            print(e)

        time.sleep(2)

    return all_articles


# =========================================================
# KEYWORD FILTER
# =========================================================

def filter_headlines(
    articles,
    keyword
):

    if not keyword:

        return articles

    keyword = keyword.strip().lower()

    return [
        article
        for article in articles
        if keyword in article["title"].lower()
    ]