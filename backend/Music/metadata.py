import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import pandas as pd
from datetime import datetime

def fetch_playlist_metadata(playlist_url):
    """
    Fetch metadata for all tracks in a Spotify playlist.
    
    Parameters:
    playlist_url (str): The Spotify playlist URL or URI
    
    Returns:
    pandas.DataFrame: DataFrame containing track metadata
    """
    try:
        # Initialize Spotify client
        client_credentials_manager = SpotifyClientCredentials(
            client_id='8c0b14d11dce48d7903746efb3dd7220',
            client_secret='b22b8d63c1ef4472a82b253687049d05'
        )
        sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)
        
        # Extract playlist ID from URL
        if 'spotify.com' in playlist_url:
            playlist_id = playlist_url.split('/')[-1].split('?')[0]
        else:
            playlist_id = playlist_url
        
        # Get playlist tracks
        results = sp.playlist_tracks(playlist_id)
        tracks = results['items']
        
        # Get all tracks if playlist has more than 100 songs
        while results['next']:
            results = sp.next(results)
            tracks.extend(results['items'])
        
        # Extract metadata for each track
        metadata = []
        for track in tracks:
            track_info = track['track']
            
            # Extract artist information
            artists = [artist['name'] for artist in track_info['artists']]
            
            # Create metadata dictionary
            track_metadata = {
                'name': track_info['name'],
                'artists': ', '.join(artists),
                'album': track_info['album']['name'],
                'release_date': track_info['album']['release_date'],
                'duration_ms': track_info['duration_ms'],
                'popularity': track_info['popularity'],
                'explicit': track_info['explicit'],
                'preview_url': track_info['preview_url'],
                'external_url': track_info['external_urls']['spotify'],
                'track_number': track_info['track_number'],
                'disc_number': track_info['disc_number'],
                'uri': track_info['uri'],
                'added_at': track['added_at']
            }
            metadata.append(track_metadata)
        
        # Convert to DataFrame
        df = pd.DataFrame(metadata)
        
        # Add some derived columns
        df['duration_min'] = df['duration_ms'] / 60000
        df['added_date'] = pd.to_datetime(df['added_at']).dt.date
        
        return df
    
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        return None

def export_metadata(df, output_format='csv'):
    """
    Export the metadata DataFrame to a file.
    
    Parameters:
    df (pandas.DataFrame): DataFrame containing track metadata
    output_format (str): Format to export ('csv' or 'excel')
    """
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    if output_format == 'csv':
        filename = f'spotify_playlist_metadata_{timestamp}.csv'
        df.to_csv(filename, index=False)
    elif output_format == 'excel':
        filename = f'spotify_playlist_metadata_{timestamp}.xlsx'
        df.to_excel(filename, index=False)
    
    print(f"Metadata exported to {filename}")

# Example usage
if __name__ == "__main__":
    playlist_url = "https://open.spotify.com/playlist/36aumcTLRU3URTh6Mr4ygT?si=f169d9cfda0644a4"
    metadata_df = fetch_playlist_metadata(playlist_url)
    
    if metadata_df is not None:
        print(f"Found {len(metadata_df)} tracks")
        export_metadata(metadata_df, 'csv')