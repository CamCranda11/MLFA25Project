import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
import json
import sys
import requests
from io import StringIO

DATA_URL = 'https://drive.google.com/file/d/1B3OF34i5t-bASvkROB0b-OSmKNkF-Khv/view?usp=drive_link'
OPTIMAL_K = 50
FEATURES_TO_CLUSTER = ['danceability', 'energy', 'mode', 'speechiness', 'acousticness', 'instrumentalness', 'valence']

def load_data():
    try:
        response = requests.get(DATA_URL)
        response.raise_for_status()
        
        # Load the content into a pandas DataFrame (adjust sep if needed, e.g., sep=';')
        song_data = pd.read_csv(StringIO(response.text))
        
        return song_data

    except requests.exceptions.RequestException as e:
        print(json.dumps({"error": f"Failed to download data from URL: {e}. Check DATA_URL or network."}))
        sys.exit(1)
    except Exception as e:
        print(json.dumps({"error": f"Failed to load or clean data: {e}"}))
        sys.exit(1)

def recommend_songs(input_song_name, input_artist_name, data_df, num_recs=5):
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
    if len(sys.argv) < 3:
        print(json.dumps({"error": "Missing arguments. Usage: python recommend.py <song_name> <artist_name>"}))
        sys.exit(1)
        
    song_data = load_data()
    
    song = sys.argv[1]
    artist = sys.argv[2]
    
    results = recommend_songs(song, artist, song_data)
    print(json.dumps(results))
