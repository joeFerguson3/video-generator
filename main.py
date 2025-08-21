import feedparser
import requests
from bs4 import BeautifulSoup

# BBC Technology RSS
url = "http://feeds.bbci.co.uk/news/technology/rss.xml"
feed = feedparser.parse(url)

# Print latest headlines
for entry in feed.entries[:5]:
    print("Title:", entry.title)
    print("Link:", entry.link)
    print("Published:", entry.published)
    print()

url = 'https://www.bbc.co.uk/news/articles/c24zdel5j18o?at_medium=RSS&at_campaign=rss'

headers = {
    'User-Agent': 'Mozilla/5.0'
}

response = requests.get(url, headers=headers)
html = response.text

soup = BeautifulSoup(html, 'html.parser')
title = soup.find(id="main-heading").find("span")
print(title)
article = soup.find_all("article")
for a in article:
    print(a.text)