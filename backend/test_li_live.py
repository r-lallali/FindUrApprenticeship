import asyncio
import sys
import os

# Add backend directory to sys.path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from scrapers.linkedin import LinkedInScraper

async def test_scraper():
    scraper = LinkedInScraper()
    print("Scraping started...")
    offers = await scraper.scrape(search_terms=["alternance developpeur"], max_pages=1)
    print(f"Found {len(offers)} offers")
    for idx, offer in enumerate(offers[:3]):
        print(f"\nOffer {idx+1}:")
        print(f"ID: {offer.get('source_id')}")
        print(f"Title: {offer.get('title')}")
        print(f"URL: {offer.get('url')}")
        desc = offer.get('description')
        print(f"Description Length: {len(desc) if desc else 0}")
        if desc:
            print(f"Snippet: {desc[:200]}")
        else:
            print("Description is None or empty")

if __name__ == "__main__":
    asyncio.run(test_scraper())
