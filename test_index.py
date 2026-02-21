import asyncio
import json
from datetime import datetime
from pathlib import Path
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo.operations import SearchIndexModel
from settings import settings


async def index_properties_json():
    """Load properties from properties.json, clear collection, and insert with embeddings."""
    client = AsyncIOMotorClient(settings.MONGODB_URI, directConnection=True)
    db = client[settings.MONGODB_DB_NAME]
    coll = db["properties"]

    # Load properties.json
    json_path = Path(__file__).parent / "properties.json"
    if not json_path.exists():
        print(f"Error: {json_path} not found")
        return

    with open(json_path, "r") as f:
        properties = json.load(f)

    print(f"Loaded {len(properties)} properties from {json_path}")

    # Clear existing collection
    result = await coll.delete_many({})
    print(f"Cleared collection: deleted {result.deleted_count} documents")

    # Process and insert properties
    for prop in properties:
        # Convert MongoDB extended JSON datetime format to Python datetime
        if "created_at" in prop and isinstance(prop["created_at"], dict):
            if "$date" in prop["created_at"]:
                prop["created_at"] = datetime.fromisoformat(
                    prop["created_at"]["$date"].replace("Z", "+00:00")
                )

        if "updated_at" in prop and isinstance(prop["updated_at"], dict):
            if "$date" in prop["updated_at"]:
                prop["updated_at"] = datetime.fromisoformat(
                    prop["updated_at"]["$date"].replace("Z", "+00:00")
                )

        # Generate description for embedding
        description_parts = []
        description_parts.append(prop.get("name", ""))
        description_parts.append(prop.get("location", ""))
        description_parts.append(prop.get("developer", ""))

        # Add USPs
        if prop.get("usps"):
            description_parts.extend(prop["usps"])

        # Add text content from assets
        for asset in prop.get("assets", []):
            if asset.get("type") == "text" and asset.get("content"):
                description_parts.append(asset["content"])

        description_text = " ".join(description_parts)

        # Generate embedding using AI client
        try:
            from services.ai_client import ai_client
            embedding = ai_client.get_embedding(description_text)
            prop["description_vector"] = embedding
            print(f"Generated embedding for {prop['property_id']} (dim: {len(embedding)})")
        except Exception as e:
            print(f"Warning: Could not generate embedding for {prop['property_id']}: {e}")
            # Set empty vector as fallback
            prop["description_vector"] = [0.0] * 3072

    # Insert all properties
    if properties:
        result = await coll.insert_many(properties)
        print(f"Inserted {len(result.inserted_ids)} properties into MongoDB")

    await client.close()


async def create_index():
    """Create vector search index on the properties collection."""
    client = AsyncIOMotorClient(settings.MONGODB_URI, directConnection=True)
    db = client[settings.MONGODB_DB_NAME]
    coll = db["properties"]

    idx = SearchIndexModel(
        {
            "fields": [
                {
                    "type": "vector",
                    "numDimensions": 3072,
                    "path": "description_vector",
                    "similarity": "cosine"
                },
                {
                    "type": "filter",
                    "path": "price_start_aed_in_million"
                },
                {
                    "type": "filter",
                    "path": "price_end_aed_in_million"
                }
            ]
        },
        name="description_vector_index",
        type="vectorSearch"
    )

    print("Creating vector search index...")
    try:
        res = await coll.create_search_indexes([idx])
        print("Index created:", res)
    except Exception as e:
        print("Error creating index:", e)

    await client.close()


if __name__ == "__main__":
    print("=== Step 1: Load and Index Properties ===")
    asyncio.run(index_properties_json())

    # print("\n=== Step 2: Create Vector Search Index ===")
    # asyncio.run(create_index())
