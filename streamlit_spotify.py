import streamlit as st
import pandas as pd
import random
df = pd.read_csv('demo_app.csv')
st.image("SpotiMix_logo.png", width=200)
st.markdown("<h1 style='text-align: center;'>🎧 Custom Your Spotify Playlist</h1>", unsafe_allow_html=True)
st.caption("Generate your perfect vibe-based playlist 🎶")
unique_moods = sorted(df['cluster'].unique())
selected_mood = st.sidebar.selectbox("Choose a Mood", unique_moods)
all_genres = sorted(df['genre'].unique())
selected_genres = st.sidebar.multiselect("Choose Genre(s)", options=all_genres, default=[])
year_range = st.sidebar.slider("Choose Year Range", 2000, 2023, (2000, 2023))
popularity_range = st.sidebar.slider(
    "Select Popularity Range:",
    min_value=20,
    max_value=100,
    value=(20, 100)
)
playlist_len = st.sidebar.slider("Number of Songs", min_value=1, max_value=120, value=5)
filtered_df = df[
    (df['cluster'] == selected_mood) &
    (df['genre'].isin(selected_genres)) &
    (df['year'].between(year_range[0], year_range[1])) &
    (df['popularity'].between(popularity_range[0], popularity_range[1]))
]
playlist = pd.DataFrame()
if selected_genres:
    genre_buckets = []
    base_count = playlist_len // len(selected_genres)
    remaining = playlist_len % len(selected_genres)  
    for genre in selected_genres:
        genre_songs = filtered_df[filtered_df['genre'] == genre]
        sample_count = min(base_count, len(genre_songs))
        if sample_count > 0:
            sampled = genre_songs.sample(n=sample_count)
            genre_buckets.append(sampled)
    playlist = pd.concat(genre_buckets)
    if len(playlist) < playlist_len:
        remaining_needed = playlist_len - len(playlist)
        remaining_pool = filtered_df[~filtered_df.index.isin(playlist.index)]
        if not remaining_pool.empty:
            filler = remaining_pool.sample(n=min(remaining_needed, len(remaining_pool)))
            playlist = pd.concat([playlist, filler])  
playlist = playlist.sample(frac=1).reset_index(drop=True)
st.write(f"Showing {len(playlist)} songs for mood **{selected_mood}** From genres: {', '.join(selected_genres)}")
if playlist.empty:
    st.warning("😕 No songs found. Maybe try different filters?")
else:
    st.dataframe(playlist[['track_name', 'artist_name', 'cluster', 'genre']])