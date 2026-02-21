import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo.operations import SearchIndexModel
from settings import settings

async def create():
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
    
    print("Creating index directly...")
    try:
        res = await coll.create_search_indexes([idx])
        print("Result:", res)
    except Exception as e:
        print("Error:", e)

if __name__ == "__main__":
    asyncio.run(create())
