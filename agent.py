import sys
import os
# This ensures the ADK can find tools.py even when running from a subfolder
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from google.adk.agents.llm_agent import Agent
from tools import save_assets_to_mongodb, queue_video_crop

# ---------------------------------------------------------
# SUB-AGENT 1: The Blog Writer
# ---------------------------------------------------------
summary_blog_agent = Agent(
    name='summary_blog_of_the_football_game',
    model='gemini-2.5-flash',
    description='Takes the timeline from the Video Analyzer and writes an engaging match report blog.',
    instruction="""
    You are an expert sports journalist.
    You will receive a chronological timeline of a football match.
    
    Your task:
    1. Write a highly engaging Markdown blog post summarizing the game.
    2. Use exciting headers (e.g., 'First Half Thrills', 'The Winning Goal').
    3. Include placeholder image tags where timestamps are mentioned so we can insert video stills later. Example: `![Match Still MM:SS](placeholder.jpg)`
    4. Keep the tone professional but energetic, suitable for World Cup fans.
    """,
    tools=[]
)

# ---------------------------------------------------------
# SUB-AGENT 2: The Highlights Editor
# ---------------------------------------------------------
highlights_maker_agent = Agent(
    name='highlights_maker_of_the_match',
    model='gemini-2.5-flash',
    description='Takes the timeline from the Video Analyzer and formats it into a cropping JSON, then triggers the crop tool and database tool.',
    instruction="""
    You are the Lead Video Editor for World Cup social media.
    You will receive a chronological timeline of a football match.
    
    Your tasks:
    1. Identify the most critical moments (goals, red cards, close misses).
    2. Generate a valid JSON array detailing these cuts. The format MUST be:
       [
         {"start_time": "MM:SS", "end_time": "MM:SS", "platform": "tiktok", "description": "Neymar goal"},
         {"start_time": "MM:SS", "end_time": "MM:SS", "platform": "youtube", "description": "Germany miss"}
       ]
    3. MUST DO: Call the 'queue_video_crop' tool using your generated JSON to start rendering.
    4. MUST DO: You will also receive the Blog Content from the parent agent. You must call the 'save_assets_to_mongodb' tool to save the blog content and your JSON plan to the database.
    """,
    tools=[queue_video_crop, save_assets_to_mongodb]
)

# ---------------------------------------------------------
# ROOT AGENT: The Video Analyzer (Orchestrator)
# ---------------------------------------------------------
root_agent = Agent(
    name='Football_Video_Analyzer',
    model='gemini-2.5-flash',
    description='Master Orchestrator: Analyzes a football match video link and coordinates the blog writing and highlight generation.',
    sub_agents=[summary_blog_agent, highlights_maker_agent],
    instruction="""
    You are the AI Match Director for the 2026 World Cup.
    You will be given a link to a football match video.
    
    STEP 1: Analyze the match and extract the timeline.
    You MUST output the timeline in exactly this format:
    [MM:SS] - [MM:SS]: [Detailed description of event]
    
    Example:
    00:00 - 01:03: Initial Commentary and teams walking out.
    05:03 - 08:00: First goal for Brazil by Neymar and replay from multiple angles.
    15:00 - 16:00: Missed opportunity for Germany. Replay shown.
    
    STEP 2: Pass this extracted timeline to the 'summary_blog_of_the_football_game' agent and ask it to write the blog.
    
    STEP 3: Once the blog is written, pass BOTH the timeline AND the written blog content to the 'highlights_maker_of_the_match' agent. 
    Instruct the highlights agent to build the JSON, queue the crops, and save EVERYTHING to MongoDB.
    
    Do not finish until the database save is confirmed.
    """,
    tools=[]
)