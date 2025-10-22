from flask import Flask, request, jsonify
from flask_cors import CORS
import pandas as pd
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics.pairwise import cosine_similarity
import os

# --- INITIALIZATION ---
app = Flask(__name__, static_folder='../frontend', static_url_path='')
CORS(app)

# Declare globals
feature_cols = ['acousticness', 'danceability', 'energy', 'instrumentalness',
                'liveness', 'loudness', 'speechiness', 'tempo', 'valence']
df_model = None

# --- DATA LOADING AND MODEL BUILDING (RUNS ONLY ONCE AT STARTUP) ---
try:
    print("Loading data and building the recommendation model...")
    csv_path = os.path.join(os.path.dirname(__file__), 'tracks_genre.csv')
    df = pd.read_csv(csv_path)

    df.columns = df.columns.str.strip()

    metadata_cols = ['name', 'artists', 'id', 'popularity']
    # Keep original valence and energy for mood filtering
    df_model = df[metadata_cols + feature_cols].copy()
    df_model.dropna(subset=['name'], inplace=True)
    df_model.reset_index(drop=True, inplace=True)

    # Create a scaled version of features for song-based similarity
    scaler = MinMaxScaler()
    df_model_scaled = df_model.copy()
    df_model_scaled[feature_cols] = scaler.fit_transform(df_model_scaled[feature_cols])
    df_model_scaled['popularity_scaled'] = scaler.fit_transform(df_model_scaled[['popularity']])

    print("Model built successfully!")

except Exception as e:
    print(f"An error occurred during model setup: {e}")
    df_model = None

# --- API ENDPOINTS ---
@app.route('/')
def home():
    return app.send_static_file('index.html')

# ENDPOINT 1: FOR SONG-BASED RECOMMENDATIONS
@app.route('/recommend', methods=['GET'])
def get_recommendations_by_song():
    if df_model is None:
        return jsonify({"error": "Model is not available."}), 500

    song_name = request.args.get('song_title')
    if not song_name:
        return jsonify({"error": "A 'song_title' parameter is required."}), 400

    matches = df_model[df_model['name'].str.lower().str.contains(song_name.lower())]
    if matches.empty:
        return jsonify({"error": f"Song containing '{song_name}' not found."}), 404

    first_match = matches.sort_values(by='popularity', ascending=False).iloc[0]
    song_index = first_match.name

    query_vec = df_model_scaled.loc[song_index, feature_cols].values.reshape(1, -1)
    all_vecs = df_model_scaled[feature_cols].values
    sim_scores = cosine_similarity(query_vec, all_vecs).flatten()

    ranked_idx = sim_scores.argsort()[::-1]
    ranked_idx = [i for i in ranked_idx if i != song_index]
    top_idx = ranked_idx[:20]

    top_songs_df = df_model.iloc[top_idx].copy()
    top_songs_df['content_similarity'] = [sim_scores[i] for i in top_idx]
    top_songs_df['hybrid_score'] = (0.6 * top_songs_df['content_similarity']) + (0.4 * df_model_scaled.loc[top_idx, 'popularity_scaled'])
    
    final_recommendations_df = top_songs_df.sort_values(by='hybrid_score', ascending=False).head(10)
    
    found_song_details = first_match.to_frame().T[['name', 'artists', 'popularity']]
    combined_results = pd.concat([found_song_details, final_recommendations_df[['name', 'artists', 'popularity']]])

    recommendations_list = combined_results.to_dict(orient='records')
    for song in recommendations_list:
        song['artists'] = song['artists'].replace("'", '"')

    return jsonify(recommendations_list)

# ENDPOINT 2: FOR MOOD-BASED RECOMMENDATIONS
@app.route('/mood', methods=['GET'])
def get_recommendations_by_mood():
    if df_model is None:
        return jsonify({"error": "Model is not available."}), 500

    mood = request.args.get('mood')
    if not mood:
        return jsonify({"error": "A 'mood' parameter is required."}), 400

    mood_filters = {
        'happy': (df_model['energy'] > 0.7) & (df_model['valence'] > 0.7),
        'sad': (df_model['energy'] < 0.4) & (df_model['valence'] < 0.3),
        'chill': (df_model['energy'] < 0.5) & (df_model['valence'] > 0.4) & (df_model['valence'] < 0.7),
        'energetic': (df_model['energy'] > 0.8) & (df_model['valence'] > 0.5)
    }

    if mood not in mood_filters:
        return jsonify({"error": "Invalid mood selected."}), 400

    mood_playlist = df_model[mood_filters[mood]]
    top_songs = mood_playlist.sort_values(by='popularity', ascending=False).head(15)

    recommendations_list = top_songs.to_dict(orient='records')
    for song in recommendations_list:
        song['artists'] = song['artists'].replace("'", '"')

    return jsonify(recommendations_list)

if __name__ == '__main__':
    app.run(debug=True)