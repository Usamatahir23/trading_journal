"""
Migration script to copy data from local MongoDB to MongoDB Atlas
"""
import os
import sys
from pathlib import Path
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError
from dotenv import load_dotenv

# Load .env file
env_path = Path(__file__).parent / '.env'
load_dotenv(env_path)

# Connection strings
LOCAL_URI = "mongodb://localhost:27017/"
ATLAS_URI = os.getenv("MONGODB_URI", "")
DATABASE_NAME = os.getenv("MONGODB_DATABASE", "trading_journal")

if not ATLAS_URI:
    print("Error: MONGODB_URI not found in .env file")
    print("Please add your Atlas connection string to .env file")
    sys.exit(1)

print("=" * 60)
print("MongoDB Migration Script: Local → Atlas")
print("=" * 60)
print(f"Source: {LOCAL_URI}")
print(f"Destination: {ATLAS_URI[:50]}...")
print(f"Database: {DATABASE_NAME}")
print("=" * 60)

try:
    # Connect to local MongoDB
    print("\n1. Connecting to local MongoDB...")
    local_client = MongoClient(LOCAL_URI, serverSelectionTimeoutMS=5000)
    local_client.server_info()
    local_db = local_client[DATABASE_NAME]
    print("   ✓ Connected to local MongoDB")
    
    # Connect to Atlas
    print("\n2. Connecting to MongoDB Atlas...")
    atlas_client = MongoClient(ATLAS_URI, serverSelectionTimeoutMS=10000)
    atlas_client.server_info()
    atlas_db = atlas_client[DATABASE_NAME]
    print("   ✓ Connected to MongoDB Atlas")
    
    # Get all collections from local database
    print("\n3. Discovering collections...")
    local_collections = local_db.list_collection_names()
    print(f"   Found collections: {', '.join(local_collections)}")
    
    if not local_collections:
        print("   ⚠ No collections found in local database")
        sys.exit(0)
    
    # Copy each collection
    total_docs = 0
    for collection_name in local_collections:
        print(f"\n4. Copying collection: {collection_name}")
        local_collection = local_db[collection_name]
        atlas_collection = atlas_db[collection_name]
        
        # Count documents
        doc_count = local_collection.count_documents({})
        print(f"   Documents to copy: {doc_count}")
        
        if doc_count == 0:
            print(f"   ⚠ Collection '{collection_name}' is empty, skipping...")
            continue
        
        # Check if collection exists in Atlas and has data
        atlas_count = atlas_collection.count_documents({})
        if atlas_count > 0:
            response = input(f"   ⚠ Atlas '{collection_name}' already has {atlas_count} documents. Overwrite? (y/n): ")
            if response.lower() != 'y':
                print(f"   ⊗ Skipping '{collection_name}'")
                continue
            # Clear existing data
            atlas_collection.delete_many({})
            print(f"   ⊗ Cleared existing data in Atlas")
        
        # Copy all documents
        print(f"   → Copying documents...")
        documents = list(local_collection.find())
        
        if documents:
            # Remove _id to let MongoDB generate new ones (or keep originals)
            for doc in documents:
                doc.pop('_id', None)
            
            result = atlas_collection.insert_many(documents)
            inserted_count = len(result.inserted_ids)
            total_docs += inserted_count
            print(f"   ✓ Successfully copied {inserted_count} documents")
        else:
            print(f"   ⚠ No documents to copy")
    
    print("\n" + "=" * 60)
    print(f"Migration Complete!")
    print(f"Total documents migrated: {total_docs}")
    print("=" * 60)
    
    # Verify migration
    print("\n5. Verifying migration...")
    for collection_name in local_collections:
        local_count = local_db[collection_name].count_documents({})
        atlas_count = atlas_db[collection_name].count_documents({})
        status = "✓" if local_count == atlas_count else "⚠"
        print(f"   {status} {collection_name}: Local={local_count}, Atlas={atlas_count}")
    
    # Close connections
    local_client.close()
    atlas_client.close()
    print("\n✓ Migration completed successfully!")
    
except ConnectionFailure as e:
    print(f"\n✗ Connection Error: {e}")
    print("\nTroubleshooting:")
    print("1. Make sure local MongoDB is running")
    print("2. Check your Atlas connection string in .env file")
    print("3. Verify your Atlas IP whitelist allows connections")
    sys.exit(1)
except Exception as e:
    print(f"\n✗ Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
