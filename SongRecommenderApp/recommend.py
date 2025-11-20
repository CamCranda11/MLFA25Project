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

def search_song_matches(input_song_name, data_df):
    input_lower = input_song_name.lower()
    mask = data_df['track_name'].astype(str).str.lower().str.contains(input_lower, na=False)
    matches = data_df[mask].copy()
    
    if matches.empty:
        return {"error": f"No songs matching '{input_song_name}' found in the dataset."}
    
    matches['is_exact'] = matches['track_name'].str.lower() == input_lower
    matches['starts_with'] = matches['track_name'].str.lower().str.startswith(input_lower)
    matches['title_len'] = matches['track_name'].str.len()
    matches = matches.sort_values(
        by=['is_exact', 'starts_with', 'title_len'], 
        ascending=[False, False, True]
    )
    
    columns_to_keep = ['track_id', 'track_name', 'artist_name', 'genre']
    
    final_columns = [col for col in columns_to_keep if col in matches.columns]
    
    final_results = matches[final_columns].head(50)
    
    return final_results.to_dict(orient='records')

def get_song_recommendations(input_song_name, input_artist_name, data_df, num_recs=5):
    try:
        input_song_name = input_song_name.lower()
        input_artist_name = input_artist_name.lower()

        song_row = data_df[
            (data_df['track_name'] == input_song_name) &
            (data_df['artist_name'] == input_artist_name)
        ]
        if song_row.empty:
            return {"error": f"Song '{input_song_name}' by {input_artist_name} not found in the dataset."}
        
        song_row = song_row.iloc[0]
        song_genre = song_row['genre']
        
        genre_df = data_df[data_df['genre'] == song_genre].copy()
        
        if len(genre_df) < OPTIMAL_K:
            return {"error": f"Not enough songs ({len(genre_df)}) in the genre '{song_genre}' to perform clustering."}

        genre_features_df = genre_df[FEATURES_TO_CLUSTER].copy()
        genre_features_df = genre_features_df.fillna(genre_features_df.mean())

        genre_scaler = StandardScaler()
        scaled_genre_features_df = genre_scaler.fit_transform(genre_features_df)

        genre_kmeans_model = KMeans(n_clusters=OPTIMAL_K, init='k-means++', n_init=10, random_state=42)
        genre_cluster_labels = genre_kmeans_model.fit_predict(scaled_genre_features_df)

        genre_df_clustered = genre_df.copy()
        genre_df_clustered['genre_cluster_id'] = genre_cluster_labels

        input_song_genre_cluster = genre_df_clustered[
            (genre_df_clustered['track_name'] == input_song_name) &
            (genre_df_clustered['artist_name'] == input_artist_name)
        ].iloc[0]['genre_cluster_id']

        recommendations = genre_df_clustered[
            (genre_df_clustered['genre_cluster_id'] == input_song_genre_cluster) &
            ((genre_df_clustered['track_name'] != input_song_name) | (genre_df_clustered['artist_name'] != input_artist_name))
        ]
        
        if len(recommendations) == 0:
            return {"error": f"No similar songs found in the cluster for '{input_song_name}'."}

        final_recs = recommendations.sample(min(num_recs, len(recommendations)))
        
        output_columns = ['track_name', 'artist_name', 'genre', 'danceability', 'energy', 'valence']
        
        return final_recs[output_columns].to_dict('records')

    except Exception as e:
        return {"error": f"An unexpected error occurred during recommendation: {e}"}

if __name__ == "__main__":
    song_data = load_data()

    if len(sys.argv) < 2:
        print(json.dumps({"error": "Missing arguments. Usage: python recommend.py <song_name> <artist_name>"}))
        sys.exit(1)
    
    song = sys.argv[1]
    
    results = search_song_matches(song, song_data)
    print(json.dumps(results))
