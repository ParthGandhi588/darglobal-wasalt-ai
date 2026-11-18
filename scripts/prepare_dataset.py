import json
import os
import re

def clean_text(text):
    if not text:
        return ""
    text = re.sub(r'\s+', ' ', str(text))
    return text.strip()

def prepare_documents():
    docs = []

    # 1. DarGlobal Projects
    with open("data/raw/darglobal_projects.json", "r", encoding="utf-8") as f:
        dg_projects = json.load(f)

    for p in dg_projects:
        content_lines = [
            f"# {p['name']}",
            f"**Developer**: {p['developer']}",
            f"**Brand Partner / Collaboration**: {p.get('brand_partner', 'DarGlobal Luxury')}",
            f"**Location**: {p['city']}, {p['country']}",
            f"**Location Details**: {p['location_details']}",
            f"**Property Types**: {', '.join(p['property_types'])}",
            f"**Total Units**: {p.get('total_units', 'Exclusive Collection')}",
        ]
        
        if 'villa_types' in p:
            content_lines.append("**Villa Collections & Configurations**:")
            for v in p['villa_types']:
                content_lines.append(f"- *{v['tier']}* ({v['bedrooms']}): {v['features']}")
        elif 'configurations' in p:
            content_lines.append(f"**Configurations**: {p['configurations']}")

        if 'sub_developments' in p:
            content_lines.append("**Key Sub-Developments / Phases**:")
            for sub in p['sub_developments']:
                content_lines.append(f"- **{sub['name']}**: {sub.get('types', '')} | {sub.get('pricing', '')} | Features: {sub.get('features', '')}")

        if 'building_height' in p:
            content_lines.append(f"**Building Height & Floors**: {p['building_height']}")

        price_guide = p.get('price_guide', 'Inquire with DarGlobal sales')
        content_lines.extend([
            f"**Price Guide**: {price_guide}",
            f"**Target Handover**: {p.get('handover_year', 'Inquire with DarGlobal')}",
            f"**Architecture, Finishes & Craftsmanship**: {p.get('architecture_finishes', '')}",
            f"**Signature Amenities**: {', '.join(p.get('amenities', []))}",
        ])

        if 'key_investor_benefits' in p:
            content_lines.append(f"**Investor Perks & Ownership Benefits**: {p['key_investor_benefits']}")

        content_lines.append(f"**Official Project Link**: {p['url']}")

        full_content = "\n\n".join(content_lines)

        docs.append({
            "id": p['id'],
            "source": "DarGlobal",
            "category": "International Luxury Project",
            "title": p['name'],
            "brand": p.get('brand_partner', 'DarGlobal'),
            "country": p['country'],
            "city": p['city'],
            "price": price_guide,
            "url": p['url'],
            "content": full_content
        })

    # 2. DarGlobal Corporate Information
    with open("data/raw/darglobal_corporate.json", "r", encoding="utf-8") as f:
        dg_corp = json.load(f)

    corp_content = f"""# {dg_corp['company_name']} - Corporate Overview & Investor Profile

**Parent Company**: {dg_corp['parent_company']}
**Stock Exchange Listing**: {dg_corp['stock_exchange']}
**Chief Executive Officer (CEO)**: {dg_corp['chief_executive_officer']}
**Global Headquarters & Key Operating Locations**: {', '.join(dg_corp['key_operating_locations'])}

### Vision & Business Model
{dg_corp['vision_mission']}

### Investment Philosophies
- **ROE (Return on Ego)**: {dg_corp['investment_concepts']['ROE']}
- **ROL (Return on Legacy)**: {dg_corp['investment_concepts']['ROL']}

### Financial Performance & Highlights
{dg_corp['financial_highlights']}

### Contact & Careers
- Recruitment: {dg_corp['recruitment_contact']}
- General Inquiries: {dg_corp['general_contact']}
- Official Website: {dg_corp['website']}
"""

    docs.append({
        "id": "dg-corporate-profile",
        "source": "DarGlobal",
        "category": "Corporate Profile",
        "title": "DarGlobal PLC - Corporate & Investor Information",
        "brand": "DarGlobal",
        "country": "United Kingdom / Global",
        "city": "London / Dubai",
        "price": "N/A",
        "url": dg_corp['website'],
        "content": corp_content
    })

    # 3. Dar Al Arkan / DarGlobal Saudi Portfolio
    with open("data/raw/daralarkan_portfolio.json", "r", encoding="utf-8") as f:
        daa_projects = json.load(f)

    for p in daa_projects:
        content = f"""# {p['title']}

**Developer**: Dar Al Arkan / DarGlobal
**Project Type**: Saudi Master-Planned Community / Real Estate Development
**Overview**: {p['meta_description']}

### Description & Details
{p['description']}

### Highlights
{chr(10).join(['- ' + h for h in p.get('highlights', [])])}

**Official Page**: {p['url']}
"""
        docs.append({
            "id": f"daa-{p['slug']}",
            "source": "Dar Al Arkan / DarGlobal",
            "category": "Saudi Development",
            "title": p['title'],
            "brand": "Dar Al Arkan / DarGlobal",
            "country": "Saudi Arabia",
            "city": "Saudi Arabia",
            "price": "Inquire with sales",
            "url": p['url'],
            "content": content.strip()
        })

    # 4. Wasalt Properties
    with open("data/raw/wasalt_properties.json", "r", encoding="utf-8") as f:
        wasalt_props = json.load(f)

    for p in wasalt_props:
        price_str = f"{p['price_sar']:,} {p['currency']}" if isinstance(p.get('price_sar'), (int, float)) else "Contact for Price"
        content = f"""# {p['title']}

**Source**: Wasalt Real Estate Portal
**Property Type**: {p['property_type']} ({p['property_main_type']})
**Purpose**: For {p['property_for']}
**City**: {p['city']}
**District / Neighborhood**: {p.get('district') or 'Prime District'}
**Full Address**: {p['address']}
**Price**: {price_str}
**Bedrooms**: {p.get('bedrooms') or 'N/A'}
**Built-Up Area**: {p.get('area_sqm') or 'N/A'}
**Completion / Age**: {p.get('completion_status') or 'Ready to move'}
**Key Amenities / Features**: {', '.join(p.get('features', [])) if p.get('features') else 'Standard residential amenities'}

**Listing Link**: {p['url']}
"""
        docs.append({
            "id": f"wasalt-prop-{p['id']}",
            "source": "Wasalt",
            "category": f"Wasalt Property Listing ({p['property_type']})",
            "title": p['title'],
            "brand": "Wasalt",
            "country": "Saudi Arabia",
            "city": p['city'],
            "price": price_str,
            "url": p['url'],
            "content": content.strip()
        })

    # 5. Wasalt Real Estate Market FAQs
    with open("data/raw/wasalt_faqs.json", "r", encoding="utf-8") as f:
        wasalt_faqs = json.load(f)

    seen_q = set()
    for idx, faq in enumerate(wasalt_faqs):
        q = faq['question']
        if q in seen_q:
            continue
        seen_q.add(q)
        content = f"""# Frequently Asked Question: {faq['question']}

**City / Region**: {faq['city']}
**Category**: {faq['category']}
**Source**: Wasalt Real Estate Market Insights

### Answer
{faq['answer']}

**Reference**: {faq['url']}
"""
        docs.append({
            "id": f"wasalt-faq-{idx}",
            "source": "Wasalt",
            "category": "Real Estate FAQ",
            "title": faq['question'],
            "brand": "Wasalt",
            "country": "Saudi Arabia",
            "city": faq['city'],
            "price": "N/A",
            "url": faq['url'],
            "content": content.strip()
        })

    print(f"\n==========================================")
    print(f"Total Unified Knowledge Base Documents: {len(docs)}")
    print(f"==========================================")

    # Save to processed
    with open("data/processed/unified_knowledge_base.json", "w", encoding="utf-8") as f:
        json.dump(docs, f, indent=2, ensure_ascii=False)

    print("Saved data/processed/unified_knowledge_base.json")

if __name__ == "__main__":
    prepare_documents()
