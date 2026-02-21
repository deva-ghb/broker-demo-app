"""
Seed script — populates MongoDB with real property data and generates AI embeddings.
Run: conda run -n smartsell python scripts/seed_data.py
"""
import asyncio
import sys
import os
import json

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.database import connect_db, close_db, get_collection
from models.property import PropertyDocument, PropertyAsset, PROPERTY_COLLECTION
from services.ai_client import ai_client


async def get_embedding(text: str) -> list[float]:
    """Generate an embedding for a text string."""
    if not text:
        return None
    try:
        return ai_client.get_embedding(text)
    except Exception as e:
        print(f"Failed to generate embedding: {e}")
        return None


async def seed():
    """Run the seed script."""
    await connect_db()
    collection = get_collection(PROPERTY_COLLECTION)
    
    # 1. Create Vector Search Indexes for MongoDB Atlas Local
    try:
        # Check existing indexes first
        indexes = []
        async for idx in collection.list_search_indexes():
            indexes.append(idx.get("name"))
            
        print(f"Existing search indexes: {indexes}")
        
        index_definitions = [
            {
                "name": "description_vector_index",
                "type": "vectorSearch",
                "definition": {
                    "fields": [
                        {
                            "type": "vector",
                            "numDimensions": 3072,
                            "path": "description_vector",
                            "similarity": "cosine"
                        },
                        {"type": "filter", "path": "price_start_aed_in_million"},
                        {"type": "filter", "path": "price_end_aed_in_million"}
                    ]
                }
            },
            {
                "name": "amenities_vector_index",
                "type": "vectorSearch",
                "definition": {
                    "fields": [
                        {
                            "type": "vector",
                            "numDimensions": 3072,
                            "path": "amenities_vector",
                            "similarity": "cosine"
                        },
                        {"type": "filter", "path": "price_start_aed_in_million"},
                        {"type": "filter", "path": "price_end_aed_in_million"}
                    ]
                }
            }
        ]

        from pymongo.operations import SearchIndexModel
        
        search_models = []
        for idx_def in index_definitions:
            if idx_def["name"] not in indexes:
                search_models.append(
                    SearchIndexModel(
                        idx_def["definition"], 
                        name=idx_def["name"], 
                        type=idx_def["type"]
                    )
                )
                
        if search_models:
            print(f"Creating {len(search_models)} search indexes...")
            result = await collection.create_search_indexes(search_models)
            print(f"Created indexes: {result}")
            # Give it a moment to initialize
            await asyncio.sleep(2)
    except Exception as e:
        print(f"Failed to create search indexes (Are you running mongodb-atlas-local?): {e}")

    # Load JSON
    json_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "properties.json")
    with open(json_path, 'r', encoding='utf-8') as f:
        properties_data = json.load(f)
        
    for item in properties_data:
        # Extract fields
        name = item.get("name")
        property_id = item.get("property_id")
        
        print(f"Processing {name} ({property_id})...")
        
        # Build assets
        assets = []
        desc_text = ""
        amenity_text = ""
        
        for asset_data in item.get("assets", []):
            asset = PropertyAsset(
                type=asset_data["type"],
                content=asset_data["content"],
                description=asset_data["description"],
                url=asset_data.get("url")
            )
            assets.append(asset)
            
            # Extract text for embeddings
            if asset.type == "text":
                if "Overview" in asset.description:
                    desc_text += asset.content + " "
                elif "Amenities" in asset.description:
                    amenity_text += asset.content + " "
                
        # Fallback if no specific sections found
        if not desc_text:
            desc_text = f"Property {name}. " + " ".join([a.content for a in assets if a.type == "text"])
        if not amenity_text:
            amenity_text = "No specific amenities listed."
            
        print("  Generating embeddings...")
        desc_vector = await get_embedding(desc_text)
        amenities_vector = await get_embedding(amenity_text)
        
        # Build Document
        prop = PropertyDocument(
            property_id=property_id,
            name=name,
            developer=item.get("developer"),
            location=item.get("location"),
            property_type=item.get("property_type", "Apartment"),
            assets=assets,
            usps=item.get("usps", []),
            price_start_aed_in_million=item.get("price_start_aed_in_million"),
            price_end_aed_in_million=item.get("price_end_aed_in_million"),
            payment_plans=item.get("payment_plans"),
            golden_visa_eligible=item.get("golden_visa_eligible", False),
            projected_roi=item.get("projected_roi"),
            broker_name=item.get("broker_name"),
            broker_phone=item.get("broker_phone"),
            broker_email=item.get("broker_email"),
            broker_logo_url=item.get("broker_logo_url"),
            brand_color=item.get("brand_color", "#1a73e8"),
            description_vector=desc_vector,
            amenities_vector=amenities_vector
        )

        # Upsert
        await collection.update_one(
            {"property_id": prop.property_id},
            {"$set": prop.model_dump()},
            upsert=True,
        )
        print(f"✅ Saved property: {prop.name}\n")

    count = await collection.count_documents({})
    print(f"📦 Total properties in database: {count}")

    await close_db()


if __name__ == "__main__":
    asyncio.run(seed())
