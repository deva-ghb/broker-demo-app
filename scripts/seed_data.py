"""
Seed script — populates MongoDB with sample property data for testing.
Run: python scripts/seed_data.py
"""
import asyncio
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.database import connect_db, close_db, get_collection
from models.property import PropertyDocument, PROPERTY_COLLECTION


SAMPLE_PROPERTIES = [
    PropertyDocument(
        property_id="prop_dubai_creek",
        name="Dubai Creek Harbour Residences",
        developer="Emaar Properties",
        location="Dubai Creek Harbour, Dubai, UAE",
        property_type="Apartment",
        assets=[
            {"type": "text", "content": "Luxurious waterfront apartments with breathtaking views of the Dubai Creek Tower and the Downtown skyline. Units range from studios to 4-bedroom penthouses.", "description": "Property Overview", "url": None},
            {"type": "text", "content": "Starting from AED 1.2M for studios, AED 2.4M for 2-bedrooms, up to AED 15M for penthouses. Flexible 60/40 payment plan with post-handover options.", "description": "Pricing & Payment Plans", "url": None},
            {"type": "text", "content": "Projected rental yield of 7-9% p.a. Capital appreciation of 12-15% expected over 3 years. Dubai's tax-free environment maximizes net returns.", "description": "ROI & Investment Returns", "url": None},
            {"type": "image", "content": "exterior_view.jpg", "description": "Stunning waterfront tower exterior with marina views", "url": "https://images.unsplash.com/photo-1512453979798-5ea266f8880c?w=800"},
            {"type": "image", "content": "pool_amenities.jpg", "description": "Infinity pool overlooking Dubai Creek", "url": "https://images.unsplash.com/photo-1582268611958-ebfd161ef9cf?w=800"},
            {"type": "image", "content": "interior_living.jpg", "description": "Modern open-plan living area with floor-to-ceiling windows", "url": "https://images.unsplash.com/photo-1600596542815-ffad4c1539a9?w=800"},
            {"type": "text", "content": "World-class amenities including infinity pool, state-of-the-art gym, children's play areas, BBQ deck, business center, and 24/7 concierge service.", "description": "Amenities & Facilities", "url": None},
            {"type": "text", "content": "Properties above AED 2M qualify for the UAE Golden Visa (10-year residency). Our dedicated team assists with the entire application process.", "description": "Golden Visa Eligibility", "url": None},
        ],
        usps=["Waterfront Living", "Emaar Quality", "Golden Visa Eligible", "7-9% Rental Yield", "Tax-Free Returns", "Flexible Payment Plans"],
        price_range="AED 1.2M - 15M",
        payment_plans="60/40 split, post-handover options available",
        golden_visa_eligible=True,
        projected_roi="7-9% rental yield, 12-15% capital appreciation",
        broker_name="Ahmed Al-Rashid",
        broker_phone="+971501234567",
        broker_email="ahmed@sellsmart.io",
        brand_color="#0d47a1",
    ),
    PropertyDocument(
        property_id="prop_palm_villa",
        name="Palm Jumeirah Signature Villas",
        developer="Nakheel",
        location="Palm Jumeirah, Dubai, UAE",
        property_type="Villa",
        assets=[
            {"type": "text", "content": "Exclusive beachfront villas on the iconic Palm Jumeirah. 5 and 6-bedroom configurations with private beaches, pools, and panoramic sea views.", "description": "Property Overview", "url": None},
            {"type": "text", "content": "Starting from AED 25M. Premium fronds from AED 40M. Bespoke financing through select UAE banks with competitive rates.", "description": "Pricing & Payment Plans", "url": None},
            {"type": "text", "content": "Palm Jumeirah villas have shown 20%+ appreciation over the past 2 years. Rental yields of 5-6% for luxury segment. Iconic address with limited supply.", "description": "ROI & Investment Returns", "url": None},
            {"type": "image", "content": "villa_exterior.jpg", "description": "Beachfront villa with private pool and sea view", "url": "https://images.unsplash.com/photo-1613490493576-7fde63acd811?w=800"},
            {"type": "image", "content": "villa_interior.jpg", "description": "Luxurious villa interior with marble finishes", "url": "https://images.unsplash.com/photo-1600607687939-ce8a6c25118c?w=800"},
            {"type": "text", "content": "Private beach access, infinity pool, landscaped gardens, smart home technology, Italian marble throughout, Gaggenau kitchen appliances.", "description": "Amenities & Facilities", "url": None},
            {"type": "text", "content": "Close to top-tier schools including GEMS Wellington, Dubai College, and Brighton College. Family-oriented community with children's parks.", "description": "School Proximity & Family Living", "url": None},
        ],
        usps=["Private Beach", "Palm Jumeirah Address", "20%+ Appreciation", "Smart Home", "Premium Finishes", "Family-Friendly"],
        price_range="AED 25M - 80M",
        payment_plans="Bank financing available, custom payment structures",
        golden_visa_eligible=True,
        projected_roi="5-6% rental yield, 20%+ capital appreciation",
        broker_name="Sarah Johnson",
        broker_phone="+971509876543",
        broker_email="sarah@sellsmart.io",
        brand_color="#1b5e20",
    ),
]


async def seed():
    """Run the seed script."""
    await connect_db()

    collection = get_collection(PROPERTY_COLLECTION)

    for prop in SAMPLE_PROPERTIES:
        # Upsert by property_id
        await collection.update_one(
            {"property_id": prop.property_id},
            {"$set": prop.model_dump()},
            upsert=True,
        )
        print(f"✅ Seeded property: {prop.name} ({prop.property_id})")

    count = await collection.count_documents({})
    print(f"\n📦 Total properties in database: {count}")

    await close_db()


if __name__ == "__main__":
    asyncio.run(seed())
