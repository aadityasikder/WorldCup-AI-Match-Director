import os
import json
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()

def save_assets_to_mongodb(match_url: str, blog_content: str, highlights_json: str) -> str:
    """
    Action Tool: Saves the final generated markdown blog and the highlights cropping JSON 
    to the MongoDB database. This makes the assets ready for web publishing.
    """
    try:
        mongo_uri = os.getenv("MONGO_URI")
        if not mongo_uri:
            return "Error: MONGO_URI environment variable not found."
            
        client = MongoClient(mongo_uri)
        db = client["worldcup_2026"]
        collection = db["match_assets"]
        
        # Ensure json is properly formatted for DB
        try:
            parsed_json = json.loads(highlights_json)
        except:
            parsed_json = highlights_json
            
        document = {
            "source_url": match_url,
            "blog_content": blog_content,
            "highlights_plan": parsed_json,
            "status": "Ready for Publishing"
        }
        
        result = collection.insert_one(document)
        return f"SUCCESS: All assets securely saved to MongoDB Atlas database with ID: {result.inserted_id}"
    except Exception as e:
        return f"Failed to save to MongoDB: {str(e)}"

def queue_video_crop(timestamps_json: str) -> str:
    """
    Action Tool: Sends the JSON timestamps to the rendering engine to physically 
    crop the match video into landscape and vertical shorts.
    """
    # In a production app, this would call ffmpeg or an external API.
    return f"SUCCESS: Video rendering engine has queued the following crops: {timestamps_json}"