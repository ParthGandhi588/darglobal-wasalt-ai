import json
import re
import urllib.request
import os
import time

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.9',
}

URLS = [
    ('https://wasalt.com/en/properties-for-sale-in-riyadh', 'Riyadh', 'Sale', 'All'),
    ('https://wasalt.com/en/apartments-for-sale-in-riyadh', 'Riyadh', 'Sale', 'Apartments'),
    ('https://wasalt.com/en/villas-for-sale-in-riyadh', 'Riyadh', 'Sale', 'Villas'),
    ('https://wasalt.com/en/properties-for-sale-in-jeddah', 'Jeddah', 'Sale', 'All'),
    ('https://wasalt.com/en/apartments-for-sale-in-jeddah', 'Jeddah', 'Sale', 'Apartments'),
    ('https://wasalt.com/en/villas-for-sale-in-jeddah', 'Jeddah', 'Sale', 'Villas'),
    ('https://wasalt.com/en/properties-for-sale-in-al-khobar', 'Al Khobar', 'Sale', 'All'),
    ('https://wasalt.com/en/villas-for-sale-in-al-khobar', 'Al Khobar', 'Sale', 'Villas'),
    ('https://wasalt.com/en/properties-for-sale-in-dammam', 'Dammam', 'Sale', 'All'),
    ('https://wasalt.com/en/apartments-for-sale-in-makkah', 'Makkah', 'Sale', 'Apartments'),
    ('https://wasalt.com/en/apartments-for-sale-in-madinah', 'Madinah', 'Sale', 'Apartments'),
]

def parse_single_property(p, city, property_for, category, default_url):
    info = p.get('propertyInfo') or p.get('projectInfo') or {}
    attrs = p.get('attributes') or []
    
    attr_dict = {}
    for a in attrs:
        if isinstance(a, dict):
            k = a.get('key') or a.get('name')
            val = a.get('value')
            unit = a.get('unit', '')
            if k and val is not None:
                attr_dict[str(k).lower()] = f"{val} {unit}".strip()

    slug = info.get('slug') or p.get('slug')
    prop_url = f"https://wasalt.com/en/sale/property/{slug}" if slug else default_url

    title = info.get('title') or info.get('propertyName') or f"{category} in {city}"
    price = info.get('salePrice') or info.get('conversionPrice') or info.get('conversionPriceMin')
    
    # Try finding bedrooms and area
    bedrooms = attr_dict.get('noofbedrooms') or attr_dict.get('bedrooms')
    area = attr_dict.get('builtuparea') or attr_dict.get('area') or f"{info.get('floorSize', '')} {info.get('unitType', 'SQM')}".strip()
    status = attr_dict.get('completionyear') or attr_dict.get('age') or info.get('propertyStatusType')

    return {
        "source": "Wasalt",
        "id": p.get('id'),
        "title": title,
        "property_type": info.get('propertySubType') or info.get('propertyMainType') or category,
        "property_main_type": info.get('propertyMainType', 'Residential'),
        "property_for": info.get('propertyFor', property_for),
        "city": info.get('city') or city,
        "district": info.get('district') or info.get('zone'),
        "address": info.get('address') or f"{city}, Saudi Arabia",
        "price_sar": price,
        "currency": info.get('currencyTypeMarker') or info.get('currencyType', 'SAR'),
        "bedrooms": bedrooms,
        "area_sqm": area,
        "completion_status": status,
        "url": prop_url,
        "features": [f.get('name') for f in p.get('featureAmenities', []) if isinstance(f, dict) and f.get('name')],
    }

def scrape_wasalt_page(url, city, property_for, category):
    print(f"Scraping {city} - {category} ({url})...")
    try:
        req = urllib.request.Request(url, headers=HEADERS)
        with urllib.request.urlopen(req, timeout=15) as resp:
            html = resp.read().decode('utf-8', errors='ignore')
    except Exception as e:
        print(f"Failed to fetch {url}: {e}")
        return [], []

    next_data_match = re.search(r'<script id="__NEXT_DATA__" type="application/json">(.*?)</script>', html)
    if not next_data_match:
        print(f"No __NEXT_DATA__ in {url}")
        return [], []

    try:
        data = json.loads(next_data_match.group(1))
    except Exception as e:
        print(f"JSON parse error for {url}: {e}")
        return [], []

    page_props = data.get('props', {}).get('pageProps', {})
    search_result = page_props.get('searchResult', {})
    properties_raw = search_result.get('properties', [])
    
    extracted_properties = []
    for item in properties_raw:
        if isinstance(item, dict):
            extracted_properties.append(parse_single_property(item, city, property_for, category, url))
        elif isinstance(item, list):
            for sub_item in item:
                if isinstance(sub_item, dict):
                    extracted_properties.append(parse_single_property(sub_item, city, property_for, category, url))

    # extract FAQs
    faq_schema = page_props.get('FAQSchema', {})
    faqs = []
    if isinstance(faq_schema, dict) and 'mainEntity' in faq_schema:
        for q_obj in faq_schema['mainEntity']:
            q = q_obj.get('name')
            ans = q_obj.get('acceptedAnswer', {}).get('text')
            if q and ans:
                faqs.append({
                    "source": "Wasalt",
                    "city": city,
                    "category": category,
                    "question": q,
                    "answer": re.sub(r'<[^>]+>', '', ans),
                    "url": url
                })

    print(f"Extracted {len(extracted_properties)} properties and {len(faqs)} FAQs.")
    return extracted_properties, faqs

def main():
    all_properties = []
    all_faqs = []
    seen_ids = set()

    for url, city, p_for, cat in URLS:
        props, faqs = scrape_wasalt_page(url, city, p_for, cat)
        for p in props:
            pid = p.get('id') or p.get('url')
            if pid not in seen_ids:
                seen_ids.add(pid)
                all_properties.append(p)
        all_faqs.extend(faqs)
        time.sleep(1)

    print(f"\n==========================================")
    print(f"Total unique Wasalt properties scraped: {len(all_properties)}")
    print(f"Total Wasalt FAQs scraped: {len(all_faqs)}")
    print(f"==========================================")

    os.makedirs("data/raw", exist_ok=True)
    os.makedirs("data/processed", exist_ok=True)

    with open("data/raw/wasalt_properties.json", "w", encoding="utf-8") as f:
        json.dump(all_properties, f, indent=2, ensure_ascii=False)

    with open("data/raw/wasalt_faqs.json", "w", encoding="utf-8") as f:
        json.dump(all_faqs, f, indent=2, ensure_ascii=False)

    print("Saved raw Wasalt datasets to data/raw/.")

if __name__ == "__main__":
    main()
