import os
import numpy as np
import librosa
import sqlite3
import logging
from datetime import datetime
import taglib
from pathlib import Path
from tqdm import tqdm

# Set up logging
logging.basicConfig(
    filename=f'music_processing_log_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def get_audio_files(directory):
    """Recursively find all supported audio files in the given directory"""
    supported_extensions = {'.mp3', '.wav', '.flac', '.m4a', '.ogg'}
    audio_files = []
    
    for path in Path(directory).rglob('*'):
        if path.suffix.lower() in supported_extensions:
            audio_files.append(str(path))
    
    logging.info(f"Found {len(audio_files)} audio files in {directory}")
    return audio_files

def extract_metadata(file_path):
    """Extract metadata from audio file using taglib"""
    try:
        audio_file = taglib.File(file_path)
        metadata = {
            'title': audio_file.tags.get('TITLE', ['Unknown Title'])[0],
            'artist': audio_file.tags.get('ARTIST', ['Unknown Artist'])[0],
            'album': audio_file.tags.get('ALBUM', ['Unknown Album'])[0]
        }
        audio_file.close()
        return metadata
    except Exception as e:
        logging.error(f"Error extracting metadata from {file_path}: {str(e)}")
        return {
            'title': os.path.basename(file_path),
            'artist': 'Unknown Artist',
            'album': 'Unknown Album'
        }


def extract_mood_features(file_path):
    try:
        y, sr = librosa.load(file_path)
        
        features = {}
        
        # Tempo and rhythm features
        tempo, _ = librosa.beat.beat_track(y=y, sr=sr)
        features['tempo'] = tempo
        
        # Spectral features
        features['spectral_centroid'] = np.mean(librosa.feature.spectral_centroid(y=y, sr=sr))
        features['spectral_bandwidth'] = np.mean(librosa.feature.spectral_bandwidth(y=y, sr=sr))
        
        # Energy features
        features['rms_energy'] = np.mean(librosa.feature.rms(y=y))
        features['zero_crossing_rate'] = np.mean(librosa.feature.zero_crossing_rate(y))
        
        # Tonal features
        chroma = librosa.feature.chroma_stft(y=y, sr=sr)
        features['chroma_mean'] = np.mean(chroma)
        
        # MFCCs
        mfccs = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=13)
        for i in range(13):
            features[f'mfcc_{i}'] = np.mean(mfccs[i])
        
        return features
        
    except Exception as e:
        logging.error(f"Error processing {file_path}: {str(e)}")
        return None

def analyze_mood(features):
    """Convert audio features to mood intensities"""
    try:
        moods = {
            'happy_intensity': 0.0,
            'sad_intensity': 0.0,
            'energetic_intensity': 0.0,
            'calm_intensity': 0.0,
            'angry_intensity': 0.0
        }
        
        # High tempo and energy -> energetic/happy
        tempo_factor = min(features['tempo'] / 180.0, 1.0)
        energy_factor = features['rms_energy'] * 10
        
        # Spectral features -> mood mapping
        brightness = features['spectral_centroid'] / 4000
        
        # Calculate intensities
        moods['energetic_intensity'] = min(1.0, (tempo_factor + energy_factor) / 2)
        moods['happy_intensity'] = min(1.0, (brightness + tempo_factor) / 2)
        moods['angry_intensity'] = min(1.0, energy_factor * features['zero_crossing_rate'])
        moods['calm_intensity'] = 1.0 - moods['energetic_intensity']
        moods['sad_intensity'] = 1.0 - moods['happy_intensity']
        
        return moods
        
    except Exception as e:
        logging.error(f"Error analyzing mood: {str(e)}")
        return None

def create_tables(cursor):
    """Create necessary database tables if they don't exist"""
    # Drop existing tables if they exist (to avoid schema conflicts)
    cursor.execute('DROP TABLE IF EXISTS songs')
    cursor.execute('DROP TABLE IF EXISTS mood_analysis')
    
    # Create the songs table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS songs (
            file_path TEXT PRIMARY KEY,
            title TEXT,
            artist TEXT,
            album TEXT
        )
    ''')
    
    # Create the mood_analysis table with the correct schema
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS mood_analysis (
            file_path TEXT PRIMARY KEY,
            happy_intensity REAL,
            sad_intensity REAL,
            energetic_intensity REAL,
            calm_intensity REAL,
            angry_intensity REAL,
            FOREIGN KEY (file_path) REFERENCES songs (file_path)
        )
    ''')

def process_local_music(music_directory):
    """Main function to process local music files and store in database"""
    conn = sqlite3.connect('music_mood.db')
    cursor = conn.cursor()
    
    # Create tables if they don't exist
    create_tables(cursor)
    conn.commit()
    
    processed_count = 0
    error_count = 0
    
    try:
        # Get list of audio files
        audio_files = get_audio_files(music_directory)
        total_files = len(audio_files)
        
        print(f"Processing {total_files} audio files from {music_directory}...")
        
        for file_path in tqdm(audio_files):
            try:
                # Extract metadata
                metadata = extract_metadata(file_path)
                
                # Extract features
                features = extract_mood_features(file_path)
                
                if features is not None:
                    # Analyze mood
                    moods = analyze_mood(features)
                    
                    if moods is not None:
                        # Store track info
                        cursor.execute('''
                            INSERT OR REPLACE INTO songs 
                            (file_path, title, artist, album)
                            VALUES (?, ?, ?, ?)
                        ''', (
                            file_path,
                            metadata['title'],
                            metadata['artist'],
                            metadata['album']
                        ))
                        
                        # Store mood analysis
                        cursor.execute('''
                            INSERT OR REPLACE INTO mood_analysis 
                            (file_path, happy_intensity, sad_intensity, 
                            energetic_intensity, calm_intensity, angry_intensity)
                            VALUES (?, ?, ?, ?, ?, ?)
                        ''', (
                            file_path,
                            float(moods['happy_intensity']),
                            float(moods['sad_intensity']),
                            float(moods['energetic_intensity']),
                            float(moods['calm_intensity']),
                            float(moods['angry_intensity'])
                        ))
                        
                        processed_count += 1
                        
                        # Commit every 10 files
                        if processed_count % 10 == 0:
                            conn.commit()
                    else:
                        error_count += 1
                else:
                    error_count += 1
                    
            except Exception as e:
                error_count += 1
                logging.error(f"Error processing file {file_path}: {str(e)}")
        
        # Final commit
        conn.commit()
        
    finally:
        # Clean up
        conn.close()
        
        print(f"\nProcessing complete!")
        print(f"Successfully processed: {processed_count} files")
        print(f"Errors: {error_count} files")
        print("Check the log file for details about any errors.")

if __name__ == "__main__":
    music_dir = input("Enter the path to your music directory: ")
    print("Starting local music processing...")
    process_local_music(music_dir)