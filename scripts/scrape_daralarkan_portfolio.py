import urllib.request
import re
import json
import os
import time

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
}

PORTFOLIO_SLUGS = [
    "rayana-wadi-safar",
    "upside-living-villas-by-versace-home",
    "amaya-jeddah",
    "dar-al-mashaer",
    "shams-ar-riyadh",
    "shams-al-arous",
    "parisiana",
    "parisiana-living",
    "golden-coast",
    "qasr-mall",
    "buraidah-hills",
    "naeem-al-jiwar",
    "al-awali-villas",
    "al-noor-villas",
    "qurtoba",
    "al-falah",
    "al-manar",
    "al-maseef",
    "al-munsiyah",
    "al-rabie",
    "al-tawoun",
    "al-yarmouk"
]

def scrape_daralarkan_project(slug):
    url = f"https://www.daralarkan.com/en/portfolio/{slug}"
    print(f"Scraping Dar Al Arkan project: {slug}...")
    try:
        req = urllib.request.Request(url, headers=HEADERS)
        with urllib.request.urlopen(req, timeout=12) as resp:
            html = resp.read().decode('utf-8', errors='ignore')
    except Exception as e:
        print(f"Failed to fetch {slug}: {e}")
        return None

    # Title extraction
    title_match = re.search(r'<title>(.*?)</title>', html)
    raw_title = title_match.group(1).split('|')[0].strip() if title_match else slug.replace('-', ' ').title()

    # Meta description
    meta_desc_match = re.search(r'<meta\s+name=["\']description["\']\s+content=["\'](.*?)["\']', html)
    meta_desc = meta_desc_match.group(1).strip() if meta_desc_match else ""

    # Paragraphs extraction
    paragraphs = re.findall(r'<p[^>]*>(.*?)</p>', html, re.DOTALL)
    cleaned_paras = []
    for p in paragraphs:
        clean = re.sub(r'<[^>]+>', ' ', p)
        clean = re.sub(r'\s+', ' ', clean).strip()
        # Filter out navigation / small words
        if len(clean) > 30 and not any(skip in clean.lower() for skip in ['cookie', 'javascript', 'privacy policy', 'rights reserved', 'back to portfolio']):
            cleaned_paras.append(clean)

    # Bullet points / list items
    list_items = re.findall(r'<li[^>]*>(.*?)</li>', html, re.DOTALL)
    cleaned_bullets = []
    for item in list_items:
        clean = re.sub(r'<[^>]+>', ' ', item)
        clean = re.sub(r'\s+', ' ', clean).strip()
        if len(clean) > 15 and not any(skip in clean.lower() for skip in ['menu', 'home', 'about us']):
            cleaned_bullets.append(clean)

    full_description = "\n\n".join(cleaned_paras)

    return {
        "source": "Dar Al Arkan / DarGlobal",
        "slug": slug,
        "title": raw_title,
        "meta_description": meta_desc,
        "description": full_description,
        "highlights": cleaned_bullets[:10],
        "url": url
    }

def main():
    projects = []
    for slug in PORTFOLIO_SLUGS:
        proj = scrape_daralarkan_project(slug)
        if proj:
            projects.append(proj)
        time.sleep(0.5)

    print(f"\nSuccessfully scraped {len(projects)} Dar Al Arkan portfolio projects.")
    with open("data/raw/daralarkan_portfolio.json", "w", encoding="utf-8") as f:
        json.dump(projects, f, indent=2, ensure_ascii=False)
    print("Saved to data/raw/daralarkan_portfolio.json")

if __name__ == "__main__":
    main()
