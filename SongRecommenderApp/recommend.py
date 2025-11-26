import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
import json
import sys
import requests
from io import StringIO
import re

DATA_URL = 'https://drive.google.com/uc?export=download&id=1B3OF34i5t-bASvkROB0b-OSmKNkF-Khv'
OPTIMAL_K = 50
FEATURES_TO_CLUSTER = ['danceability', 'energy', 'mode', 'speechiness', 'acousticness', 'instrumentalness', 'valence']

def load_data():
    try:
        session = requests.Session()
        response = session.get(DATA_URL, stream=True)
        
        if "virus scan warning" in response.text.lower():
            
            token = None
            for key, value in session.cookies.items():
                if key.startswith('download_warning'):
                    token = value
                    break
            
            if not token:
                uuid_match = re.search(r'name="uuid" value="([^"]+)"', response.text)
                confirm_match = re.search(r'name="confirm" value="([^"]+)"', response.text)
                action_match = re.search(r'action="([^"]+)"', response.text)
                
                if uuid_match and confirm_match and action_match:
                    url = action_match.group(1)
                    file_id = DATA_URL.split('id=')[-1]
                    
                    params = {
                        'id': file_id,
                        'export': 'download',
                        'confirm': confirm_match.group(1),
                        'uuid': uuid_match.group(1)
                    }
                    response = session.get(url, params=params, stream=True)
            
            elif token:
                params = {'confirm': token}
                response = session.get(DATA_URL, params=params, stream=True)

        response.raise_for_status()
        
        content = response.content.decode('utf-8')
        song_data = pd.read_csv(StringIO(content), sep=',', engine='python', on_bad_lines='skip')
        
        song_data.columns = song_data.columns.str.strip().str.lower()
        
        return song_data

    except requests.exceptions.RequestException as e:
        print(json.dumps({"error": f"Failed to download data: {e}"}))
        sys.exit(1)
    except Exception as e:
        print(json.dumps({"error": f"Failed to load data: {e}"}))
        sys.exit(1)

def search_song_matches(input_song_name, input_artist_name, data_df):
    matches = data_df.copy()

    if input_song_name:
        input_song_lower = input_song_name.lower().strip()
        matches = matches[matches['track_name'].astype(str).str.lower().str.contains(input_song_lower, na=False)]

    if input_artist_name:
        input_artist_lower = input_artist_name.lower().strip()
        matches = matches[matches['artist_name'].astype(str).str.lower().str.contains(input_artist_lower, na=False)]
    
    if matches.empty:
        return {"error": "No matches found."}
    
    if input_song_name:
        # If we have a song name, prioritize exact song title matches
        matches['is_exact'] = matches['track_name'].str.lower() == input_song_name.lower().strip()
        matches['starts_with'] = matches['track_name'].str.lower().str.startswith(input_song_name.lower().strip())
        matches['title_len'] = matches['track_name'].str.len()
        
        matches = matches.sort_values(by=['is_exact', 'starts_with', 'title_len'], ascending=[False, False, True])
    else:
        matches = matches.sort_values(by=['track_name'], ascending=[True])

    columns_to_keep = ['track_name', 'artist_name', 'genre']
    final_columns = [col for col in columns_to_keep if col in matches.columns]
    
    return matches[final_columns].head(50).to_dict(orient='records')

def get_song_recommendations(input_song_name, input_artist_name, data_df):
    song_input = input_song_name.lower().strip()
    artist_input = input_artist_name.lower().strip()
    
    match_mask = (
        data_df['track_name'].astype(str).str.lower().str.strip() == song_input
    ) & (
        data_df['artist_name'].astype(str).str.lower().str.strip() == artist_input
    )
    
    matching_rows = data_df[match_mask]
    
    if matching_rows.empty:
        return {"error": f"Song '{input_song_name}' by {input_artist_name} not found in the dataset."}
    
    seed_song = matching_rows.iloc[0]
    seed_genre = seed_song['genre']
    
    recommendations = data_df[
        (data_df['genre'] == seed_genre) & 
        (data_df['track_name'].astype(str).str.lower().str.strip() != song_input)
    ]
    
    recommendations = recommendations.sample(n=min(10, len(recommendations)))
    
    columns_to_keep = ['track_name', 'artist_name', 'genre']
    final_results = recommendations[columns_to_keep].to_dict(orient='records')
    
    return final_results

if __name__ == "__main__":
    song_data = load_data()

    if len(sys.argv) < 2:
        print(json.dumps({"error": "Error: Missing arguments. Usage: python recommend.py <mode> <song_name>"}))
        sys.exit(1)

    command = sys.argv[1]

    if command == "search":
        input_song = sys.argv[2] if len(sys.argv) > 2 else ""
        input_artist = sys.argv[3] if len(sys.argv) > 3 else ""
        
        results = search_song_matches(input_song, input_artist, song_data)
        print(json.dumps(results))
        
    elif command == "recommend":
        input_song = sys.argv[2]
        if len(sys.argv) >= 4:
            input_artist = sys.argv[3]
        else:
            input_artist = ""

        results = get_song_recommendations(input_song, input_artist, song_data)
        print(json.dumps(results))
