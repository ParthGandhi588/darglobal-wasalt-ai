import json
import os
import re
import urllib.request

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
}

DARGLOBAL_PROJECTS = [
    {
        "id": "dg-tierra-viva",
        "name": "Tierra Viva (by Automobili Lamborghini)",
        "developer": "DarGlobal",
        "brand_partner": "Automobili Lamborghini",
        "country": "Spain",
        "city": "Benahavís, Costa del Sol (Marbella)",
        "location_details": "Gated luxury community of Los Jararillos in Benahavís, perched on hills overlooking Marbella and Puerto Banús with panoramic Mediterranean Sea views.",
        "property_types": ["Ultra-Luxury Hillside Villas"],
        "total_units": 53,
        "villa_types": [
            {"tier": "Esmeralda Villas", "bedrooms": "4 Bedrooms", "features": "Terraced gardens, infinity pool, floor-to-ceiling windows"},
            {"tier": "Zafiro Villas", "bedrooms": "5 Bedrooms", "features": "Wine cellar, home cinema, private spa, swimming pool"},
            {"tier": "Diamante Villas", "bedrooms": "6 Bedrooms", "features": "Private rooftop terrace, multiple pools, panoramic 180° Mediterranean views"},
            {"tier": "Painite Villas", "bedrooms": "Elite Custom", "features": "Internal car elevators to park supercars inside the living gallery"}
        ],
        "price_guide": "From €3,600,000 to €8,300,000+ (approx. $3.9M - $9.0M USD)",
        "handover_year": "2027",
        "architecture_finishes": "Directly inspired by Lamborghini sports cars with sharp hexagonal design, polished marble, carbon fiber details, Miele chef kitchens, and Duravit/Kohler sanitary ware.",
        "amenities": ["24/7 Gated Security", "Private Swimming Pools", "Internal Car Lift (select villas)", "Spa & Sauna", "Home Theaters", "Rooftop Terraces"],
        "url": "https://darglobal.co.uk/en/project/tierra-viva"
    },
    {
        "id": "dg-davinci-tower",
        "name": "DaVinci Tower (Interiors by Pagani)",
        "developer": "DarGlobal",
        "brand_partner": "Pagani Automobili",
        "country": "United Arab Emirates",
        "city": "Dubai",
        "location_details": "Prime waterfront along the Dubai Water Canal in Business Bay, overlooking Downtown Dubai and Burj Khalifa.",
        "property_types": ["Ultra-Luxury Residences & Penthouses"],
        "total_units": 80,
        "configurations": "2, 3, and 4-bedroom residences plus exclusive Pagani Penthouses.",
        "price_guide": "Starting from AED 7,500,000+ (approx. $2.04M USD)",
        "handover_year": "2025/2026",
        "architecture_finishes": "First residential building designed by Horacio Pagani. Features hand-stitched leather, exposed carbon fiber, aeronautical titanium elements, and bespoke Pagani furniture.",
        "amenities": ["Pagani Residents Lounge", "Canal-View Infinity Pool", "Smart Home Automation (iPad & Facial Recognition)", "Private Gym & Spa", "24/7 Concierge & Valet"],
        "url": "https://darglobal.co.uk/en/project/davinci-tower"
    },
    {
        "id": "dg-urban-oasis",
        "name": "Urban Oasis (Interiors by Missoni)",
        "developer": "DarGlobal",
        "brand_partner": "Missoni",
        "country": "United Arab Emirates",
        "city": "Dubai",
        "location_details": "On the banks of Dubai Water Canal, Business Bay, Dubai. 5 minutes from Downtown Dubai and Dubai Mall.",
        "property_types": ["Luxury Waterfront Apartments & Penthouses"],
        "total_units": 450,
        "configurations": "Studios, 1, 2, 3-bedroom luxury apartments and exclusive 4-bedroom penthouses with private elevators.",
        "price_guide": "Launched at ~AED 800M GDV; resale/premium inventory starting approx. AED 1,600,000+ ($435,000+ USD)",
        "handover_year": "Completed / Ready for occupancy",
        "architecture_finishes": "Interiors curated by MissoniHome with Miami-inspired vibrant zigzag patterns, high-end Italian ceramics, and panoramic canal vistas.",
        "amenities": ["Canal-front Infinity Pool", "Waterfront Gymnasium", "Missoni-designed Lobby", "Private Elevator Access for Penthouses", "Covered Parking"],
        "url": "https://darglobal.co.uk/en/project/urban-oasis"
    },
    {
        "id": "dg-the-astera",
        "name": "The Astera (Interiors by Aston Martin)",
        "developer": "DarGlobal",
        "brand_partner": "Aston Martin",
        "country": "United Arab Emirates",
        "city": "Al Marjan Island, Ras Al Khaimah",
        "location_details": "Direct beachfront plot on Al Marjan Island, adjacent to the upcoming Wynn Resort Casino in Ras Al Khaimah.",
        "property_types": ["Beachfront Residences & Sky Villas"],
        "total_units": 260,
        "configurations": "1, 2, 3-bedroom luxury waterfront apartments and 3-bedroom beachfront sky villas.",
        "price_guide": "Starting from AED 2,700,000 (~$735,000 USD)",
        "handover_year": "Q4 2028",
        "architecture_finishes": "Aston Martin design philosophy combining British bespoke automotive craftsmanship, fine fluted wood panels, rich leather trims, and floor-to-ceiling sea views.",
        "amenities": ["Private Beach Access", "Infinity Pool & Pool Bar", "Spa & Wellness Center", "Indoor Cinema", "Yoga Lawn", "Multipurpose Lounge"],
        "url": "https://darglobal.co.uk/en/project/the-astera"
    },
    {
        "id": "dg-dg1-living",
        "name": "DG1 Living",
        "developer": "DarGlobal",
        "brand_partner": "Gensler Architects (Architectural Design)",
        "country": "United Arab Emirates",
        "city": "Dubai",
        "location_details": "Waterfront plot in Business Bay, direct access to Dubai Water Canal boardwalk.",
        "property_types": ["Contemporary Luxury Urban Residences"],
        "total_units": 340,
        "configurations": "Studios, 1, 2, and 3-bedroom residences (452 sq. ft. to 2,476 sq. ft.).",
        "price_guide": "Starting from AED 1,500,000+ (~$408,000 USD)",
        "handover_year": "Q2 2027",
        "architecture_finishes": "Sculptural twisted facade by Gensler representing haute couture architecture. European porcelain tile, European minimalist kitchens, floor-to-ceiling soundproof glass.",
        "amenities": ["Rooftop Sky Garden & Lounge", "Canal-View Infinity Pool", "Gymnasium & Yoga Studio", "24/7 Concierge", "Valet Parking"],
        "url": "https://darglobal.co.uk/en/project/dg1"
    },
    {
        "id": "dg-les-vagues",
        "name": "Les Vagues (Interiors by ELIE SAAB)",
        "developer": "DarGlobal",
        "brand_partner": "ELIE SAAB",
        "country": "Qatar",
        "city": "Doha (Qetaifan Island North)",
        "location_details": "Prime first-line marine plot on Qetaifan Island North, Lusail/Doha, overlooking the marina and sea.",
        "property_types": ["Waterfront Luxury Residences"],
        "total_units": 424,
        "configurations": "1, 2, and 3-bedroom sea-facing residences (81 sqm to 257 sqm).",
        "price_guide": "Starting from QAR 2,000,000 (~$549,000 USD)",
        "handover_year": "Q4 2027",
        "architecture_finishes": "Elie Saab haute couture interior aesthetic, warm bronze and marble finishes, palm-lined oceanfront terraces, and floor-to-ceiling glass.",
        "amenities": ["Infinity Sea-view Swimming Pool", "Elie Saab Resident Lounge", "Fitness Center", "Landscaped Courtyards", "Private Marina Access", "Dedicated Service Lifts"],
        "url": "https://darglobal.co.uk/en/project/les-vagues"
    },
    {
        "id": "dg-aida-oman",
        "name": "AIDA Master Development (Trump Golf, Trump Cliff & Fendi Casa)",
        "developer": "DarGlobal (in joint partnership with Omran Group)",
        "brand_partner": "The Trump Organization & Fendi Casa",
        "country": "Oman",
        "city": "Muscat (Yiti & Yenkit Cliffs)",
        "location_details": "Dramatic 3.5 million sqm clifftop master community perched 130 meters above the Gulf of Oman with 3 pristine beaches.",
        "property_types": ["Trump Golf Villas", "Trump Cliff Villas", "Azure Oceanfront Villas by Fendi Casa", "Trump International Hotel Residences"],
        "sub_developments": [
            {
                "name": "Azure Oceanfront Villas (Interiors by Fendi Casa)",
                "units": 19,
                "types": "4 & 5-Bedroom clifftop mansions (approx. 407 sqm)",
                "pricing": "From OMR 1,505,700 to OMR 1,956,710 (~$3.91M - $5.09M USD)",
                "features": "Fendi Casa Roman craftsmanship, private infinity pools, cliff-edge gardens, private gyms, 100% sea views"
            },
            {
                "name": "Trump Golf Villas & Trump Cliff Villas",
                "types": "5-Bedroom fairway villas (406+ sqm) & 3-5 bedroom cliffside residences",
                "pricing": "Starting from ~£1,560,000 / $2,350,000 USD (hotel residences from £265,700)",
                "features": "Direct frontage on 18-hole Trump International Golf Course Oman, Trump Members Club privileges, private golf cart"
            }
        ],
        "handover_year": "Q4 2028",
        "key_investor_benefits": "100% Freehold ownership for all nationalities under Integrated Tourism Complex (ITC), Lifetime Omani Golden Residency, 0% personal income tax, 0% capital gains tax, 0% inheritance tax.",
        "amenities": ["18-Hole Trump International Championship Golf Course", "Trump International Hotel", "Private Beaches", "Wellness Centers", "Hiking & Running Trails"],
        "url": "https://darglobal.co.uk/en/project/aida"
    },
    {
        "id": "dg-trump-tower-dubai",
        "name": "Trump International Hotel & Tower Dubai",
        "developer": "DarGlobal",
        "brand_partner": "The Trump Organization",
        "country": "United Arab Emirates",
        "city": "Dubai (Sheikh Zayed Road)",
        "location_details": "Landmark skyscraper along Sheikh Zayed Road, gateway to Downtown Dubai.",
        "property_types": ["5-Star Branded Hotel, Luxury Residences & Penthouses"],
        "building_height": "~350 meters, 80 floors",
        "configurations": "1, 2, 3-bedroom luxury residences (764 sq. ft. to 7,720 sq. ft.) and 4-bedroom duplex penthouses inspired by Trump Tower 5th Avenue.",
        "price_guide": "Starting from AED 4,500,000+ (~$1.22M USD)",
        "handover_year": "Q4 2031",
        "amenities": ["Trump Members-Only Private Club", "World's Highest Outdoor Sky Infinity Pool", "Private Sky Pools for Penthouses", "Trump Spa & Wellness", "Michelin-caliber Dining"],
        "url": "https://darglobal.co.uk/en/project/trump-tower-dubai"
    },
    {
        "id": "dg-trump-jeddah",
        "name": "Trump Tower Jeddah & Trump Plaza Jeddah",
        "developer": "DarGlobal",
        "brand_partner": "The Trump Organization",
        "country": "Saudi Arabia",
        "city": "Jeddah",
        "location_details": "Trump Tower on Jeddah Corniche (47 floors); Trump Plaza within the Amaya master community on King Abdulaziz Road ($1 Billion GDV).",
        "property_types": ["Seafront Residences, Executive Apartments & Townhouses"],
        "configurations": "Trump Tower: 1-4 bedroom seafront apartments & penthouses (70-365 sqm). Trump Plaza: Executive suites, park residences, and 4-bedroom townhouses (69-364 sqm).",
        "handover_year": "December 2029 (Trump Tower) / 2028-2029 (Trump Plaza)",
        "amenities": ["Vitality Club Spa & Sports Medicine", "Trump Private Club & Cigar Lounge", "Golf Simulator Rooms", "Corniche-Facing Swimming Pools", "Grade-A Corporate Offices"],
        "url": "https://darglobal.co.uk/en/project/trump-jeddah"
    },
    {
        "id": "dg-mouawad-neptune",
        "name": "Neptune Villas (Interiors by Mouawad)",
        "developer": "DarGlobal",
        "brand_partner": "Mouawad (High Jewelry House)",
        "country": "Saudi Arabia",
        "city": "Riyadh (SEDRA Community)",
        "location_details": "SEDRA master-planned community in North Riyadh, near the World Expo 2030 site.",
        "property_types": ["Haute-Joaillerie Branded Luxury Villas"],
        "total_units": 200,
        "configurations": "5-bedroom luxury villas (300 sqm to 448 sqm).",
        "development_value": "SAR 880 Million",
        "price_guide": "From SAR 4,200,000 to SAR 7,500,000+ (~$1.12M - $2.0M USD)",
        "handover_year": "Q4 2026",
        "architecture_finishes": "First residential project in the world by Mouawad, incorporating jewelry cuts, gemstone palettes, gold leaf accents, and bespoke craftsmanship.",
        "amenities": ["Private Landscaped Gardens", "Smart Home Automation", "Private Pools", "Proximity to SEDRA Central Park & Metro"],
        "url": "https://darglobal.co.uk/en/project/mouawad-neptune"
    },
    {
        "id": "dg-marea-missoni",
        "name": "Marea (Interiors by Missoni)",
        "developer": "DarGlobal",
        "brand_partner": "Missoni",
        "country": "Spain",
        "city": "Cortesin, Costa del Sol",
        "location_details": "Within the world-famous Finca Cortesin golf resort in Casares/Manilva, Costa del Sol, Spain.",
        "property_types": ["Branded Luxury Golf Residences"],
        "configurations": "2, 3, and 4-bedroom residences with 270-degree panoramic views of Marbella, Gibraltar, and the Moroccan coast.",
        "price_guide": "From €1,100,000 to €2,500,000+ (~$1.2M - $2.7M USD)",
        "handover_year": "2027",
        "amenities": ["Finca Cortesin Championship Golf Access", "Infinity Swimming Pool", "Tennis Courts", "Hanging Observation Deck", "Missoni-Styled Community Lounges"],
        "url": "https://darglobal.co.uk/en/project/marea"
    }
]

DARGLOBAL_CORPORATE = {
    "company_name": "DarGlobal PLC",
    "parent_company": "Dar Al Arkan Real Estate Development Company (Saudi Arabia, listed on Tadawul: 4300)",
    "stock_exchange": "London Stock Exchange (LSE: DAR)",
    "chief_executive_officer": "Ziad El Chaar",
    "vision_mission": "DarGlobal is the international luxury real estate arm of Dar Al Arkan, pioneering branded residences through partnerships with global luxury icons including Automobili Lamborghini, Pagani Automobili, Aston Martin, The Trump Organization, Missoni, Fendi Casa, Elie Saab, and Mouawad.",
    "investment_concepts": {
        "ROE": "Return on Ego - providing prestigious, design-led trophy assets that confer status and international distinction.",
        "ROL": "Return on Legacy - creating timeless generational wealth through resilient prime real estate in top global jurisdictions (London, Dubai, Spain, Oman, Qatar, Saudi Arabia)."
    },
    "key_operating_locations": ["London (UK)", "Dubai (UAE)", "Riyadh & Jeddah (Saudi Arabia)", "Muscat (Oman)", "Doha (Qatar)", "Costa del Sol (Spain)"],
    "financial_highlights": "Delivered 17.3% ROE in FY2025; robust balance sheet backed by prime international land bank and syndicated credit facilities with Emirates NBD ($250M).",
    "recruitment_contact": "careers@darglobal.co.uk",
    "general_contact": "info@darglobal.co.uk",
    "website": "https://darglobal.co.uk"
}

def main():
    print("Exporting DarGlobal rich knowledge base...")
    os.makedirs("data/raw", exist_ok=True)
    os.makedirs("data/processed", exist_ok=True)

    with open("data/raw/darglobal_projects.json", "w", encoding="utf-8") as f:
        json.dump(DARGLOBAL_PROJECTS, f, indent=2, ensure_ascii=False)

    with open("data/raw/darglobal_corporate.json", "w", encoding="utf-8") as f:
        json.dump(DARGLOBAL_CORPORATE, f, indent=2, ensure_ascii=False)

    print("Saved DarGlobal raw datasets.")

if __name__ == "__main__":
    main()
