import streamlit as st
import pandas as pd
import random
df = pd.read_csv('demo_app.csv')
col1, col2, col3 = st.columns(3)
with col2:
    st.image("SpotiMix_logo.png", width=200)
st.markdown("""
    <h1 style='text-align: center; margin-top: 20px; margin-bottom: 20px;'>
        🎧 Custom Your Spotify Playlist
    </h1>
""", unsafe_allow_html=True)
st.markdown(
    """
    <div style="text-align: center; font-size: 14px; color: #555;">
        Generate your perfect vibe-based playlist 🎶
    </div>
    """,
    unsafe_allow_html=True
)
st.markdown(
    """
    <iframe style="border-radius:12px" 
        src="https://open.spotify.com/embed/playlist/4oaf8rsMeLhKmpJFn2iPqy?utm_source=generator" 
        width="100%" height="380" frameBorder="0" 
        allowfullscreen="" allow="autoplay; clipboard-write; encrypted-media; fullscreen; picture-in-picture" 
        loading="lazy">
    </iframe>
    """,
    unsafe_allow_html=True
)
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
playlist_len = st.sidebar.slider("Number of Songs", min_value=1, max_value=100, value=5)
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
    if genre_buckets:  
        playlist = pd.concat(genre_buckets)
        if len(playlist) < playlist_len:
            remaining_needed = playlist_len - len(playlist)
            remaining_pool = filtered_df[~filtered_df.index.isin(playlist.index)]
            if not remaining_pool.empty:
                filler = remaining_pool.sample(n=min(remaining_needed, len(remaining_pool)))
                playlist = pd.concat([playlist, filler])
        playlist = playlist.sample(frac=1).reset_index(drop=True)
    else:
        playlist = pd.DataFrame()  
else:
    playlist = pd.DataFrame()  
if playlist.empty:
    st.warning("😕 No songs found. Maybe you should try different filters?")
else:
    st.write(
        f"Showing {len(playlist)} songs for mood **{selected_mood}** "
        f"from genres: {', '.join(selected_genres)} "
        f"between years {year_range[0]} and {year_range[1]}"
    )
    st.dataframe(playlist[['track_name', 'artist_name', 'cluster', 'genre', 'year']])