import requests
from bs4 import BeautifulSoup
import html

def fetch_page_content(url):
    """Fetches and returns the content of a webpage."""
    response = requests.get(url)
    if response.status_code == 200:
        return response.text
    else:
        print(f"Błąd pobierania strony: {response.status_code}")
        return None

def parse_internal_links(main_div, limit=5):
    """Extracts internal links from the article."""
    links = [
        a['title'] for a in main_div.find_all('a', href=True)
        if a['href'].startswith('/wiki/') and ':' not in a['href'][6:]
    ][:limit]
    return " | ".join(links)

def parse_image_sources(main_div, limit=3):
    """Extracts URLs of images used in the article."""
    images = [
        img["src"] for img in main_div.find_all("img")
        if '/wiki/' not in img['src']
    ][:limit]
    return " | ".join(images) if images else ""

def parse_external_references(soup, limit=3):
    """Extracts external reference URLs."""
    refs_div = soup.find("div", class_="mw-references-wrap mw-references-columns") or \
               soup.find("div", class_="do-not-make-smaller refsection")
    
    if refs_div:
        refs = [
            html.escape(a['href']) for ref in refs_div.find_all("li")
            for span in ref.find_all("span", class_="reference-text")
            for a in span.find_all("a", href=True) if "http" in a['href']
        ][:limit]
        return " | ".join(refs)
    return ""

def parse_categories(soup, limit=3):
    """Extracts categories assigned to the article."""
    kat_div = soup.find("div", class_="mw-normal-catlinks")
    if kat_div:
        categories = [a.text.strip() for a in kat_div.find('ul').find_all("a")][:limit]
        return " | ".join(categories)
    return ""

def wiki_article_summary(nazwa):
    """Fetches and summarizes the article content by extracting specific data."""
    url = f'https://pl.wikipedia.org{nazwa}'
    content = fetch_page_content(url)
    if content:
        soup = BeautifulSoup(content, 'html.parser')
        main_div = soup.find("div", class_="mw-body-content")
        
        # Collect different article components
        summary = [
            parse_internal_links(main_div),
            parse_image_sources(main_div),
            parse_external_references(soup),
            parse_categories(soup)
        ]
        return summary
    return []

def fetch_category_articles(category_name, limit=2):
    """Fetches article links for a given category."""
    base_url = 'https://pl.wikipedia.org/wiki/Kategoria:'
    category_url = base_url + category_name.replace(" ", "_")
    content = fetch_page_content(category_url)
    
    if content:
        soup = BeautifulSoup(content, 'html.parser')
        main_div = soup.find("div", class_="mw-category mw-category-columns")
        
        if main_div:
            return [a["href"] for a in main_div.find_all("a")[:limit]]
    return []

def main():
    category = input("Podaj nazwę kategorii: ")
    article_links = fetch_category_articles(category)
    
    for link in article_links:
        summary = wiki_article_summary(link)
        for item in summary:
            print(item)

if __name__ == "__main__":
    main()
