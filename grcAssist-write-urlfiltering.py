# grcAssist.py
# GRC Relevant News Assist

#This program is designed to pull relevant current news articles for keywords defined in a keywords.csv fie.
#GRC professionals can use this to build a bank of quic-to-access relevant cyber news stories or for a Just-in-Time news story to educate end users.

#The python file is called grcAssist.py.
#The keywords.csv file should have keyword(s) per row.  
#Multiple keywords should be placed on same row with a %20 separating keywords
#e.g. cybersecurity   OR cybersecurity%20healthcare
#IF you have row 1 say cybersecurity and row 2 say healthcare, the script will run two separate queries, one for cybersecurity and one for healthcare. This will likely result in less helpful stories.
#The grcdata.csv file is the output file that the script appends to. It has 5 columns. date,keyword,title,desc,url
#all 3 files should be in the same directory.
#run "python grcAssist.py"
#Python 3

#You need to register a free tier API key from newsdata.io. 
#You get 200 API pulls a day and each story counts as 10 pulls (per newsdata.io site)
#I'd suggest checking API terms when creating your free API key.

# https://newsdata.io/
# Replace your api key in script with the one issued you by Newsdata.io

#Gerald Auger, 7/22/24, SimplyCyber.io

import csv
import requests
import datetime
from openpyxl import Workbook
import urllib.parse

def search_news(keyword, api_key, category="technology", language="en"):
  """
  Searches NewsData.io API for a keyword and returns relevant articles.

  Args:
      keyword: The keyword to search for (e.g., "cybersecurity").
      api_key: Your NewsData.io API key.
      category: Optional category to filter results (defaults to "technology").
      language: Optional language parameter (defaults to "en").

  Returns:
      A list of dictionaries, each containing headline, description, and url.
  """
  url = f"https://newsdata.io/api/1/news?apikey={api_key}&q={keyword}&language={language}&category={category}"
  response = requests.get(url)
  print(url)

  try:
    data = response.json()
    articles = []
    if data["status"] == "success":
      for article in data["results"]:
        articles.append({
          "headline": article["title"],
          "description": article["description"],
          "url": article["link"],
        })


import re
from urllib.parse import urlparse

# Minimal domain blacklist (extend as needed)
PAYWALL_DOMAINS = {
    "wsj.com", "ft.com", "bloomberg.com", "economist.com", "nytimes.com",
    "washingtonpost.com", "telegraph.co.uk", "latimes.com"
}

# Keywords frequently present on paywall/auth pages
PAYWALL_KEYWORDS = {
    "subscribe", "subscription", "paywall", "members only",
    "sign in", "log in", "register to read", "content is available to subscribers",
    "free trial", "purchase"
}

def is_valid_url_format(url: str) -> bool:
    try:
        parsed = urlparse(url)
        return parsed.scheme in ("http", "https") and bool(parsed.netloc)
    except Exception:
        return False

def domain_in(host: str, blocklist: set) -> bool:
    # Match root and subdomains (e.g., "www.wsj.com" -> "wsj.com")
    for d in blocklist:
        if host == d or host.endswith("." + d):
            return True
    return False

def sniff_is_paywalled(html_text: str) -> bool:
    # Simple keyword presence (case-insensitive)
    lowered = html_text.lower()
    return any(k in lowered for k in PAYWALL_KEYWORDS)

def validate_article_url(url: str, timeout_sec: float = 5.0) -> bool:
    """Return True if the URL is reachable and likely readable without auth/paywall."""
    if not is_valid_url_format(url):
        return False

    host = urlparse(url).netloc.lower()
    if domain_in(host, PAYWALL_DOMAINS):
        return False

    headers = {
        "User-Agent": "Mozilla/5.0 (validation-bot; +https://example.org)",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
        "Connection": "close",
    }

    try:
        # Use HEAD first: cheap reachability + final status after redirects
        head = requests.head(url, headers=headers, allow_redirects=True, timeout=timeout_sec)
        # Reject obvious auth/paywall
        if head.status_code in (401, 403):
            return False

        # If HEAD is not conclusive, do a small GET with stream to avoid large downloads
        if head.status_code != 200:
            get = requests.get(url, headers=headers, allow_redirects=True, timeout=timeout_sec, stream=True)
        else:
            get = requests.get(url, headers=headers, allow_redirects=True, timeout=timeout_sec, stream=True)

        # After redirects, we expect 200 OK
        if get.status_code != 200:
            return False

        # Check Content-Type (prefer text/html)
        ctype = get.headers.get("Content-Type", "")
        if "text/html" not in ctype:
            # Many PDFs or binaries are not ideal for quick-read news; reject or adjust to taste
            return False

        # Read a small chunk to sniff page nature (no heavy download)
        chunk = next(get.iter_content(chunk_size=4096), b"")
        text_sample = chunk.decode("utf-8", errors="ignore")

        # Reject near-empty or JS-only loader shells
        if len(text_sample.strip()) < 100:
            return False

        # Simple paywall sniffing
        if sniff_is_paywalled(text_sample):
            return False

        return True
    except requests.exceptions.RequestException:
        # DNS, timeouts, SSL errors, connection errors -> reject


      # Write articles to spreadsheet
      filename = "grcdata.csv"
      write_to_spreadsheet(articles, filename, keyword)
    return articles
  except (requests.exceptions.RequestException, KeyError):
    print(f"Error: An error occurred while fetching data from the API.")
    return []

def write_to_spreadsheet(articles, filename, keyword):
  """
  Writes a list of articles to a spreadsheet file.

  Args:
      articles: A list of dictionaries containing article data.
      filename: The filename for the spreadsheet.
  """
  today = datetime.date.today().strftime("%Y-%m-%d")
  with open(filename, 'a', newline='', encoding='utf-8') as csvfile:
    writer = csv.writer(csvfile)
    for article in articles:
      writer.writerow([today, keyword, article["headline"], article["description"], article["url"]])


def main():
  """
  Reads keywords from a CSV file or user input and searches for cybersecurity news.
  """
  # Clear the output file at the start of each run
  
  open("grcdata.csv", "w", encoding="utf-8").close()
  
  # Get keywords (modify to read from CSV or get user input)
  keywords_file = "keywords.csv"  # Replace with your filename
  keywords = []
  with open(keywords_file, 'r') as file:
    reader = csv.reader(file)
    for row in reader:
      keywords.append(urllib.parse.unquote(row[0])) #URL-decode each keyword

  # Alternatively, get keywords from user input
  # keywords = input("Enter keywords separated by commas: ").split(",")

  api_key = "pub_0b629ea1e3b5411791241b076682c005"  # Replace with your actual NewsData.io API key

  for keyword in keywords:
    articles = search_news(keyword.strip(), api_key)
    if articles:
      print(f"\nSearch results for '{keyword}':")
      for article in articles:
        print(f"\t- {article['headline']}")
        print(f"\t\t{article['description']}")
        print(f"\t\t{article['url']}\n")
    else:
      print(f"No articles found for '{keyword}'.")


if __name__ == "__main__":
  main()


