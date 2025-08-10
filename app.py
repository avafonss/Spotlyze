import streamlit as st
from main import get_token, search_for_artist, get_songs_by_artist
from requests import get

# Set page configurations
st.set_page_config(page_title="Spotlyze", page_icon="🎵")


# Title
st.title("Spotlyze: Catch Up with Your Favorite Artists")
st.markdown("Enter any artist’s name and find out what listeners are loving **right now**")

# Search input
artist_name = st.text_input("Enter artist name:", placeholder="e.g., Tame Impala, The Beatles, Clairo")


if st.button("Search Artist"):
    st.markdown("---")
    if artist_name:
        with st.spinner("Searching for artist..."):
            try:
                # Get token and search for artist
                token = get_token()
                artist = search_for_artist(token, artist_name)
                
                if artist:
                    st.success(f"✅ **Found artist:** {artist['name']}")

                    # Get headers for API calls
                    headers = {"Authorization": f"Bearer {token}"}
                    # Get most recent release
                    recent_url = f"https://api.spotify.com/v1/artists/{artist['id']}/albums?limit=1&include_groups=album,single"
                    recent_result = get(recent_url, headers=headers)
                    if recent_result.status_code == 200:
                        recent_albums = recent_result.json()["items"]
                        if recent_albums:
                            latest = recent_albums[0]
                            st.info(f"🎵 **Latest Release:** {latest['name']} ({latest['release_date']})")
                    
                    # extra space
                    st.write("")
                    st.write("")

                    # Display artist photo and info
                    col1, col2 = st.columns([1, 2])
                    with col1:
                        if artist['images']:
                            st.image(artist['images'][0]['url'], width=200, caption=artist['name'])
                        else:
                            st.info("No image available for this artist")

                    with col2:
                        # Display artist stats
                        st.metric("Popularity Score", f"{artist['popularity']}/100")
                        st.metric("Current Follower Count", f"{artist['followers']['total']:,}")

                        # Display genres
                        if artist['genres']:
                            st.write("**Genres:** " + ", ".join(artist['genres']))

                        # Display Spotify profile link
                        spotify_url = artist['external_urls']['spotify']
                        st.markdown(f"**Spotify Profile:** [Open in Spotify]({spotify_url})")

                    # Get top songs
                    songs = get_songs_by_artist(token, artist['id'])

                    if songs:
                        st.subheader(f"📈 Top {len(songs)} Songs:")

                        # Display songs in a nice format
                        for i, song in enumerate(songs):
                            col1, col2 = st.columns([0.1, 0.9])
                            with col1:
                                st.markdown(f"**{i + 1}.**")
                            with col2:
                                st.markdown(f"**{song['name']}**")
                                if song['album']['name']:
                                    st.caption(f"Album: {song['album']['name']}")
                    else:
                        st.warning("No top tracks found for this artist.")
                        
                else:
                    st.error("Artist not found. Please try a different name.")
                    
            except Exception as e:
                st.error(f"An error occurred: {str(e)}")
    else:
        st.warning("Please enter an artist name.")

# Bottom of page (additional info)
st.markdown("---")
st.markdown("**Note:** Spotlyze uses the Spotify API to find artists and their top tracks.")
