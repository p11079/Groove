import streamlit as st
import pandas as pd
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics.pairwise import cosine_similarity
import os

# --- PAGE CONFIG ---
st.set_page_config(page_title="Groove Music Recommender", layout="centered")
st.title("🎵 Groove Music Recommender")

# --- INITIALIZATION & CACHING ---
feature_cols = ['acousticness', 'danceability', 'energy', 'instrumentalness',
                'liveness', 'loudness', 'speechiness', 'tempo', 'valence']

@st.cache_data
def load_data():
    try:
        # Resolve path safely for Streamlit Cloud
        base_path = os.path.dirname(__file__)
        csv_path = os.path.join(base_path, 'tracks_genre.csv')
        
        df = pd.read_csv(csv_path)
        df.columns = df.columns.str.strip()
        
        metadata_cols = ['name', 'artists', 'id', 'popularity']
        df_model = df[metadata_cols + feature_cols].copy()
        df_model.dropna(subset=['name'], inplace=True)
        df_model.reset_index(drop=True, inplace=True)
        
        # Scaling
        scaler = MinMaxScaler()
        df_scaled = df_model.copy()
        df_scaled[feature_cols] = scaler.fit_transform(df_scaled[feature_cols])
        df_scaled['popularity_scaled'] = scaler.fit_transform(df_scaled[['popularity']])
        
        return df_model, df_scaled
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return None, None

df_model, df_model_scaled = load_data()

# --- RECOMMENDATION LOGIC ---
def get_recommendations_by_song(song_name):
    matches = df_model[df_model['name'].str.lower().str.contains(song_name.lower())]
    if matches.empty:
        return None, f"Song containing '{song_name}' not found."

    first_match = matches.sort_values(by='popularity', ascending=False).iloc[0]
    song_index = first_match.name

    query_vec = df_model_scaled.loc[song_index, feature_cols].values.reshape(1, -1)
    all_vecs = df_model_scaled[feature_cols].values
    sim_scores = cosine_similarity(query_vec, all_vecs).flatten()

    ranked_idx = [i for i in sim_scores.argsort()[::-1] if i != song_index][:20]

    top_songs_df = df_model.iloc[ranked_idx].copy()
    top_songs_df['content_similarity'] = [sim_scores[i] for i in ranked_idx]
    top_songs_df['hybrid_score'] = (0.6 * top_songs_df['content_similarity']) + (0.4 * df_model_scaled.loc[ranked_idx, 'popularity_scaled'])
    
    return top_songs_df.sort_values(by='hybrid_score', ascending=False).head(10), first_match

# --- USER INTERFACE ---
tab1, tab2 = st.tabs(["Search by Song", "Search by Mood"])

with tab1:
    song_input = st.text_input("Enter a song name:")
    if song_input:
        recs, original = get_recommendations_by_song(song_input)
        if recs is not None:
            st.write(f"Showing results based on: **{original['name']}** by {original['artists']}")
            st.table(recs[['name', 'artists', 'popularity']])
        else:
            st.warning(original)

with tab2:
    mood = st.selectbox("How are you feeling?", ["happy", "sad", "chill", "energetic"])
    if st.button("Get Mood Playlist"):
        mood_filters = {
            'happy': (df_model['energy'] > 0.7) & (df_model['valence'] > 0.7),
            'sad': (df_model['energy'] < 0.4) & (df_model['valence'] < 0.3),
            'chill': (df_model['energy'] < 0.5) & (df_model['valence'] > 0.4) & (df_model['valence'] < 0.7),
            'energetic': (df_model['energy'] > 0.8) & (df_model['valence'] > 0.5)
        }
        mood_playlist = df_model[mood_filters[mood]].sort_values(by='popularity', ascending=False).head(15)
        st.table(mood_playlist[['name', 'artists', 'popularity']])
