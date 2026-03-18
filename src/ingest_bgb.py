"""
BGB Scraper
Fetches and processes all sections from the German Civil Code (BGB)
"""
import os
import json
import requests
from bs4 import BeautifulSoup
from typing import List, Dict
from dotenv import load_dotenv

load_dotenv()


class BGBScraper:
    def __init__(self):
        self.url = os.getenv("BGB_URL", "https://www.gesetze-im-internet.de/bgb/BJNR001950896.html")
        self.data_dir = "data"
        os.makedirs(self.data_dir, exist_ok=True)

    def fetch_html(self) -> str:
        """Fetch the BGB HTML from the official website"""
        print(f"Fetching BGB from {self.url}...")
        response = requests.get(self.url, timeout=30)
        response.raise_for_status()
        print("Successfully fetched BGB HTML")
        return response.text

    def extract_all_sections(self, html: str) -> List[Dict[str, str]]:
        """
        Extract all sections from the BGB HTML
        Returns a list of dictionaries with section number, title, and content

        HTML Structure:
        - Each section is in <div class="jnnorm" ... title="Einzelnorm">
        - Section number: <span class="jnenbez">§ 1</span>
        - Section title: <span class="jnentitel">Title</span>
        - Content paragraphs: <div class="jurAbsatz">...</div>
        """
        soup = BeautifulSoup(html, 'lxml')
        sections = []

        # Find all norm divs (individual law sections)
        all_norms = soup.find_all('div', class_='jnnorm')
        print(f"Found {len(all_norms)} total norm sections in BGB")

        # Extract all sections - no filtering
        for i, norm in enumerate(all_norms, 1):
            section_data = self._parse_norm(norm)
            if section_data:
                sections.append(section_data)

                # Progress indicator for large datasets
                if i % 500 == 0:
                    print(f"  Processed {i}/{len(all_norms)} norms, extracted {len(sections)} sections...")

        print(f"Extracted {len(sections)} sections from BGB")
        return sections

    def _parse_norm(self, norm_div) -> Dict[str, str]:
        """
        Parse a norm div to extract § number, title, and content

        Structure:
        <div class="jnnorm">
          <div class="jnheader">
            <h3>
              <span class="jnenbez">§ 1922</span>
              <span class="jnentitel">Title</span>
            </h3>
          </div>
          <div class="jnhtml">
            <div class="jurAbsatz">Paragraph 1</div>
            <div class="jurAbsatz">Paragraph 2</div>
          </div>
        </div>
        """
        # Extract section number
        section_span = norm_div.find('span', class_='jnenbez')
        if not section_span:
            return None

        section_num = section_span.get_text(strip=True)

        # Extract title
        title_span = norm_div.find('span', class_='jnentitel')
        title = title_span.get_text(strip=True) if title_span else ''

        # Extract content paragraphs
        content_divs = norm_div.find_all('div', class_='jurAbsatz')
        content_parts = []

        for div in content_divs:
            text = div.get_text(strip=True)
            if text:
                content_parts.append(text)

        content = '\n\n'.join(content_parts)

        # Only return if we have at least section number and some content
        if section_num and (content or title):
            return {
                'section': section_num,
                'title': title,
                'content': content
            }

        return None

    def save_sections(self, sections: List[Dict[str, str]], filename: str = "bgb_all.json"):
        """Save extracted sections to JSON file"""
        filepath = os.path.join(self.data_dir, filename)
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(sections, f, ensure_ascii=False, indent=2)
        print(f"Saved {len(sections)} sections to {filepath}")
        return filepath

    def scrape_and_save(self) -> str:
        """Main method to scrape BGB and save all sections"""
        html = self.fetch_html()
        sections = self.extract_all_sections(html)

        if not sections:
            print("WARNING: No sections extracted. The HTML structure may have changed.")
            print("Attempting alternative parsing method...")
            sections = self._alternative_parsing(html)

        if sections:
            filepath = self.save_sections(sections)
            return filepath
        else:
            raise Exception("Failed to extract any sections from BGB")

    def _alternative_parsing(self, html: str) -> List[Dict[str, str]]:
        """
        Alternative parsing method - extracts all sections from BGB
        """
        soup = BeautifulSoup(html, 'lxml')
        sections = []

        # Find all norm divs
        all_norms = soup.find_all('div', class_='jnnorm')
        print(f"Alternative parsing: Found {len(all_norms)} norm sections")

        for i, norm in enumerate(all_norms, 1):
            section_data = self._parse_norm(norm)
            if section_data:
                sections.append(section_data)

                # Progress indicator
                if i % 500 == 0:
                    print(f"  Extracted {len(sections)} sections so far...")

        print(f"Alternative parsing: Extracted {len(sections)} sections from BGB")
        return sections


def main():
    """Main entry point for scraping BGB"""
    scraper = BGBScraper()
    try:
        filepath = scraper.scrape_and_save()
        print(f"\n✓ Successfully scraped entire BGB")
        print(f"✓ Data saved to: {filepath}")
    except Exception as e:
        print(f"\n✗ Error scraping BGB: {e}")
        raise


if __name__ == "__main__":
    main()
