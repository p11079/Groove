import streamlit as st
import pandas as pd
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics.pairwise import cosine_similarity
import os

# --- PAGE CONFIG ---
st.set_page_config(page_title="Groove Music Recommender", layout="centered")
st.title("🎵 Groove Music Recommender")

# --- FEATURE COLUMNS ---
feature_cols = ['acousticness', 'danceability', 'energy', 'instrumentalness',
                'liveness', 'loudness', 'speechiness', 'tempo', 'valence']

@st.cache_data
def load_data():
    try:
        base_path = os.path.dirname(os.path.abspath(__file__))

        # Possible dataset sources (in priority order)
        split_1 = os.path.join(base_path, 'tracks_genre_1.csv')
        split_2 = os.path.join(base_path, 'tracks_genre_2.csv')
        single  = os.path.join(base_path, 'tracks_genre.csv')
        zip_f   = os.path.join(base_path, 'tracks_genre.zip')

        df = None

        # Strategy 1: Load two split CSVs and concatenate
        if os.path.exists(split_1) and os.path.exists(split_2):
            df1 = pd.read_csv(split_1)
            df2 = pd.read_csv(split_2)
            df  = pd.concat([df1, df2], ignore_index=True)

        # Strategy 2: Single full CSV
        elif os.path.exists(single):
            try:
                df = pd.read_csv(single, encoding='utf-8')
            except UnicodeDecodeError:
                df = pd.read_csv(single, encoding='latin-1')

        # Strategy 3: Read directly from zip (pandas native support)
        elif os.path.exists(zip_f):
            df = pd.read_csv(zip_f, compression='zip')

        else:
            st.error("Dataset not found. Upload 'tracks_genre_1.csv' & 'tracks_genre_2.csv' to the repo.")
            return None, None

        df.columns = df.columns.str.strip()

        metadata_cols = ['name', 'artists', 'id', 'popularity']
        df_model = df[metadata_cols + feature_cols].copy()
        df_model.dropna(subset=['name'], inplace=True)
        df_model.reset_index(drop=True, inplace=True)

        # Scale features
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
    if df_model is None:
        return None, "Data not loaded."

    matches = df_model[df_model['name'].str.lower().str.contains(song_name.lower(), na=False)]
    if matches.empty:
        return None, f"No song containing '{song_name}' was found."

    first_match = matches.sort_values(by='popularity', ascending=False).iloc[0]
    song_index  = first_match.name

    query_vec  = df_model_scaled.loc[song_index, feature_cols].values.reshape(1, -1)
    all_vecs   = df_model_scaled[feature_cols].values
    sim_scores = cosine_similarity(query_vec, all_vecs).flatten()

    ranked_idx = [i for i in sim_scores.argsort()[::-1] if i != song_index][:20]

    top_songs_df = df_model.iloc[ranked_idx].copy()
    top_songs_df['content_similarity'] = [sim_scores[i] for i in ranked_idx]
    top_songs_df['hybrid_score'] = (
        (0.6 * top_songs_df['content_similarity']) +
        (0.4 * df_model_scaled.loc[ranked_idx, 'popularity_scaled'])
    )

    return top_songs_df.sort_values(by='hybrid_score', ascending=False).head(10), first_match

# --- UI ---
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
    if df_model is not None:
        mood = st.selectbox("How are you feeling?", ["happy", "sad", "chill", "energetic"])
        if st.button("Get Mood Playlist"):
            mood_filters = {
                'happy':     (df_model['energy'] > 0.7) & (df_model['valence'] > 0.7),
                'sad':       (df_model['energy'] < 0.4) & (df_model['valence'] < 0.3),
                'chill':     (df_model['energy'] < 0.5) & (df_model['valence'] > 0.4) & (df_model['valence'] < 0.7),
                'energetic': (df_model['energy'] > 0.8) & (df_model['valence'] > 0.5),
            }
            mood_playlist = df_model[mood_filters[mood]].sort_values(by='popularity', ascending=False).head(15)
            st.table(mood_playlist[['name', 'artists', 'popularity']])
    else:
        st.warning("Data not available. Check dataset files.")
