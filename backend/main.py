from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import sqlite3
from typing import List, Dict, Optional
import os
from dotenv import load_dotenv
from weather import WeatherFetcher
from location import get_current_location

# Load environment variables
load_dotenv()

# Initialize FastAPI app
app = FastAPI(
    title="MoodTunes API",
    description="Weather-aware mood-based music recommendation API",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with actual frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize weather fetcher with error handling
try:
    weather_fetcher = WeatherFetcher()
except ValueError as e:
    print(f"Warning: {e}")
    print("Weather features will be disabled")
    weather_fetcher = None

def get_db_connection():
    """Create database connection with error handling"""
    try:
        conn = sqlite3.connect('music_mood.db')
        conn.row_factory = sqlite3.Row
        return conn
    except sqlite3.Error as e:
        raise HTTPException(status_code=500, detail=f"Database connection error: {str(e)}")

def map_weather_mood_to_db_mood(weather_mood: str) -> str:
    """Map weather service moods to database mood columns"""
    mood_mapping = {
        "mellow": "calm",
        "intense": "energetic",
        "melancholic": "sad",
        "calm": "calm",
        "energetic": "energetic",
        "neutral": "calm"
    }
    return mood_mapping.get(weather_mood, "calm")

@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "message": "MoodTunes API is running"
    }

@app.get("/moods")
async def get_moods():
    """Get list of available moods"""
    return {
        "moods": [
            "happy",
            "sad",
            "energetic",
            "calm",
            "angry"
        ]
    }

@app.get("/weather")
async def get_weather():
    """Get current weather and recommended mood"""
    if weather_fetcher is None:
        raise HTTPException(
            status_code=503,
            detail="Weather service is not available. Check API key configuration."
        )
    
    location = get_current_location()
    if "error" in location:
        raise HTTPException(status_code=500, detail=f"Error getting location: {location['error']}")
    
    weather = weather_fetcher.get_weather(location["latitude"], location["longitude"])
    if not weather:
        raise HTTPException(status_code=500, detail="Error fetching weather data")
    
    mood = weather_fetcher.get_mood_from_weather(weather)
    return {
        "weather": weather,
        "recommended_mood": mood,
        "location": location
    }

@app.get("/songs/{mood}")
async def get_songs_by_mood(mood: str, limit: int = 10):
    """Get songs matching a specific mood"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        mood_column = f"{mood.lower()}_intensity"
        
        # Updated query to use file_path instead of track_id
        query = """
        SELECT s.*, m.*
        FROM songs s
        JOIN mood_analysis m ON s.file_path = m.file_path
        WHERE m.{} > 0.5
        ORDER BY m.{} DESC
        LIMIT ?
        """.format(mood_column, mood_column)
        
        cursor.execute(query, (limit,))
        songs = cursor.fetchall()
        
        result = []
        for song in songs:
            result.append({
                "file_path": song['file_path'],
                "title": song['title'],
                "artist": song['artist'],
                "album": song['album'],
                "mood_intensity": song[mood_column]
            })
        
        return {"songs": result}
        
    except sqlite3.Error as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    finally:
        if 'conn' in locals():
            conn.close()

@app.get("/playlist/{user_mood}")
async def get_weather_aware_playlist(user_mood: str, limit: int = 10):
    try:
        weather_data = await get_weather()
        weather_mood = map_weather_mood_to_db_mood(weather_data["recommended_mood"])
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        user_column = f"{user_mood.lower()}_intensity"
        weather_column = f"{weather_mood.lower()}_intensity"
        
        # Updated query to use file_path
        query = """
        SELECT s.*, m.*
        FROM songs s
        JOIN mood_analysis m ON s.file_path = m.file_path
        WHERE m.{} > 0.3 AND m.{} > 0.3
        ORDER BY (m.{} + m.{})/2 DESC
        LIMIT ?
        """.format(user_column, weather_column, user_column, weather_column)
        
        cursor.execute(query, (limit,))
        songs = cursor.fetchall()
        
        result = []
        for song in songs:
            result.append({
                "file_path": song['file_path'],
                "title": song['title'],
                "artist": song['artist'],
                "album": song['album'],
                "user_mood_intensity": song[user_column],
                "weather_mood_intensity": song[weather_column]
            })
        
        return {
            "weather": weather_data["weather"],
            "user_mood": user_mood,
            "weather_mood": weather_mood,
            "songs": result
        }
        
    except sqlite3.Error as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    finally:
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="localhost", port=8000)