"""Temporary script to analyze the BGB HTML structure"""
import requests
from bs4 import BeautifulSoup

url = "https://www.gesetze-im-internet.de/bgb/BJNR001950896.html"
print(f"Fetching {url}...")
response = requests.get(url, timeout=30)
response.raise_for_status()

soup = BeautifulSoup(response.text, 'lxml')

# Find all links or structures that might contain "Buch 5" or "Erbrecht"
print("\n=== Looking for Book 5 / Erbrecht ===")
for elem in soup.find_all(['a', 'h1', 'h2', 'h3', 'h4', 'div', 'span'])[:200]:
    text = elem.get_text(strip=True)
    if 'Buch 5' in text or 'Erbrecht' in text or '§ 1922' in text:
        print(f"\nTag: {elem.name}")
        print(f"Classes: {elem.get('class', [])}")
        print(f"ID: {elem.get('id', '')}")
        print(f"Text: {text[:100]}")
        print(f"Parent: {elem.parent.name if elem.parent else 'None'}")

# Look for patterns with § symbols
print("\n\n=== Sample § patterns ===")
count = 0
for elem in soup.find_all(['a', 'div', 'span', 'p']):
    text = elem.get_text(strip=True)
    if text.startswith('§') and len(text) < 100:
        print(f"{elem.name}.{'.'.join(elem.get('class', []))}: {text}")
        count += 1
        if count > 10:
            break

# Look for overall structure
print("\n\n=== Main content structure ===")
body = soup.find('body')
if body:
    for child in list(body.children)[:20]:
        if hasattr(child, 'name'):
            print(f"{child.name}: {child.get('class', [])} - {child.get('id', '')}")
