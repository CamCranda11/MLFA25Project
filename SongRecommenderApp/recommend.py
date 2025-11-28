# === WEB APP VERSION: This is the version implemented in my web app, it expands upon the notebook and optimizes structure to fit the web app. ===

# Import statement for my necessary tools.
import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
import json
import sys
import requests
from io import StringIO
import re

DATA_URL = 'https://drive.google.com/uc?export=download&id=1B3OF34i5t-bASvkROB0b-OSmKNkF-Khv' # URL so the web app can access the dataset, saved to my Google Drive.
OPTIMAL_K = 50 # K Constant to define the number of clusters.
FEATURES_TO_CLUSTER = ['danceability', 'energy', 'mode', 'speechiness', 'acousticness', 'instrumentalness', 'valence'] # List of audio features to cluster on.

# Function to load the data into a pandas Dataframe.
def load_data():
    try:
        # Initialize session and request the dataset.
        session = requests.Session()
        response = session.get(DATA_URL, stream=True)

        # Check for a Google Drive Virus Scan Warning.
        if "virus scan warning" in response.text.lower():
            
            token = None
            # Check cookies for a download warning token.
            for key, value in session.cookies.items():
                if key.startswith('download_warning'):
                    token = value
                    break

            # If the token is not in cookies, try parsing the warning page for requirements.
            if not token:
                uuid_match = re.search(r'name="uuid" value="([^"]+)"', response.text) # Find UUID parameter.
                confirm_match = re.search(r'name="confirm" value="([^"]+)"', response.text) # Find confiration token.
                action_match = re.search(r'action="([^"]+)"', response.text) # Find the action URL.

                # If all requirements are met, perform the download request.
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

            # If the token was found in cookies, us it for the confirmed download.
            elif token:
                params = {'confirm': token}
                response = session.get(DATA_URL, params=params, stream=True)

        response.raise_for_status() # Raise an exception for bad status codes.
        content = response.content.decode('utf-8') # Decode to a UTF-8 string.

        # Read the CSV data from the string.
        song_data = pd.read_csv(StringIO(content), sep=',', engine='python', on_bad_lines='skip')

        # Clean and normalize column names.
        song_data.columns = song_data.columns.str.strip().str.lower()
        
        return song_data

    # Error handling.
    except requests.exceptions.RequestException as e:
        print(json.dumps({"error": f"Failed to download data: {e}"}))
        sys.exit(1)
    except Exception as e:
        print(json.dumps({"error": f"Failed to load data: {e}"}))
        sys.exit(1)

# Function to search the dataset for matches based on the data entered by the user on the search bar.
def search_song_matches(input_song_name, input_artist_name, data_df):
    # Copy the main dataset to avoid changing the original Dataframe.
    matches = data_df.copy()

    if input_song_name:
        input_song_lower = input_song_name.lower().strip() # Normalize input song name.
        matches = matches[matches['track_name'].astype(str).str.lower().str.contains(input_song_lower, na=False)] # Filter the Dataframe to show matches.

    if input_artist_name:
        input_artist_lower = input_artist_name.lower().strip() # Normalize input artist name.
        matches = matches[matches['artist_name'].astype(str).str.lower().str.contains(input_artist_lower, na=False)] # Filter the Datafram to show matches.
    
    if matches.empty:
        return {"error": "No matches found."} # Handle an instance where none of the search data matches in the dataset.
    
    if input_song_name:
        # Prioritize exact matches for song names, then for starting matches, then length matches.
        matches['is_exact'] = matches['track_name'].str.lower() == input_song_name.lower().strip()
        matches['starts_with'] = matches['track_name'].str.lower().str.startswith(input_song_name.lower().strip())
        matches['title_len'] = matches['track_name'].str.len()
        # Sort matches.
        matches = matches.sort_values(by=['is_exact', 'starts_with', 'title_len'], ascending=[False, False, True])
        
    else:
        matches = matches.sort_values(by=['track_name'], ascending=[True]) # If only the artist field has a value, sort alphabetically.

    # Define columns displayed on web app after searching
    columns_to_keep = ['track_name', 'artist_name', 'genre']
    final_columns = [col for col in columns_to_keep if col in matches.columns]

    # Return the top 50 matches
    return matches[final_columns].head(50).to_dict(orient='records')

# Function to actually run the KMeans Clustering and output recommended songs.
def get_song_recommendations(input_song_name, input_artist_name, data_df):
    # Normalize the input song and artist names to help in matching.
    song_input = input_song_name.lower().strip()
    artist_input = input_artist_name.lower().strip()

    # Create a boolean mask to find the exact song and artist match in the dataset.
    match_mask = (
        data_df['track_name'].astype(str).str.lower().str.strip() == song_input
    ) & (
        data_df['artist_name'].astype(str).str.lower().str.strip() == artist_input
    )

    # Apply the mask to the Dataframe.
    matching_rows = data_df[match_mask]

    # Check if no exact match was found.
    if matching_rows.empty:
        return {"error": f"Song '{input_song_name}' by {input_artist_name} not found."}

    # Identify the first exact match as the seed song and extract the genre.
    seed_song = matching_rows.iloc[0]
    seed_genre = seed_song['genre']

    # Filter data by genre.
    genre_df = data_df[data_df['genre'] == seed_genre].copy()

    # Check to make sure there are enough songs in the genre to perform the clustering task.
    if len(genre_df) < OPTIMAL_K:
        # Fallback method to return a random sample of the same genre without clustering if there are not enough entries in that genre.
        return genre_df.sample(n=min(10, len(genre_df)))[['track_name', 'artist_name', 'genre']].to_dict(orient='records')

    for col in FEATURES_TO_CLUSTER:
        # Convert the feature columns into numeric type for proper handling.
        genre_df[col] = pd.to_numeric(genre_df[col], errors='coerce')

    # Drop any rows with missing data.
    genre_df = genre_df.dropna(subset=FEATURES_TO_CLUSTER)

    # Feature scaling.
    scaler = StandardScaler()
    scaled_data = scaler.fit_transform(genre_df[FEATURES_TO_CLUSTER])

    # Initialize the KMeans model with the predefined number of clusters.
    kmeans = KMeans(n_clusters=OPTIMAL_K, init='k-means++', random_state=42)
    genre_df['cluster'] = kmeans.fit_predict(scaled_data) # Fit model

    # Identify the seed song in the clustered Dataframe.
    seed_in_genre = genre_df[
        (genre_df['track_name'].astype(str).str.lower().str.strip() == song_input) & 
        (genre_df['artist_name'].astype(str).str.lower().str.strip() == artist_input)
    ]

    # Make sure the seed song was not dropped during cleanup.
    if seed_in_genre.empty:
        # Fallback if seed got dropped during cleaning (rare)
        return {"error": "Song data was incomplete and could not be clustered."}
        
    # Extract cluster ID of the seed song.
    current_cluster = seed_in_genre.iloc[0]['cluster']

    # Filter for recommendations and exclude the seed song from the recommendations list.
    recommendations = genre_df[
        (genre_df['cluster'] == current_cluster) & 
        (genre_df['track_name'].astype(str).str.lower().str.strip() != song_input)
    ]

    # Select a random sample of 10 songs.
    recommendations = recommendations.sample(n=min(10, len(recommendations)))

    # Define returned columns.
    columns_to_keep = ['track_name', 'artist_name', 'genre']

    # Return the list of 10 recommendations.
    return recommendations[columns_to_keep].to_dict(orient='records')

if __name__ == "__main__":
    # Load the dataset.
    song_data = load_data()

    # Check to make sure the necessary arguments are present.
    if len(sys.argv) < 2:
        # Print JSON error message.
        print(json.dumps({"error": "Error: Missing arguments. Usage: python recommend.py <mode> <song_name>"}))
        sys.exit(1)

    command = sys.argv[1]

    # Searching.
    if command == "search":
        input_song = sys.argv[2] if len(sys.argv) > 2 else "" # Get song name if present.
        input_artist = sys.argv[3] if len(sys.argv) > 3 else "" # Get artist name is present.
        results = search_song_matches(input_song, input_artist, song_data) # Call search function.
        print(json.dumps(results)) # Output results as JSON.

    # Recommending.
    elif command == "recommend":
        input_song = sys.argv[2] # Get song name from argument 2.
        if len(sys.argv) >= 4: # Get artist name from argument 3, confirm it exists.
            input_artist = sys.argv[3]
        else:
            input_artist = "" # Default to empty if artist name is not provided.

        results = get_song_recommendations(input_song, input_artist, song_data) # Call recommendation function.
        print(json.dumps(results)) # Output results as JSON.
