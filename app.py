import streamlit as st
from recommender import get_recommendations, get_processed_data, get_movie_poster

# 1. Page Setup
st.set_page_config(page_title="CineMatch AI", layout="wide")

# 2. Advanced UI Styling (CSS)
st.markdown("""
    <style>
    .main { background-color: #0b0e14; }
    .stApp { background: linear-gradient(135deg, #0f172a 0%, #000000 100%); }
    
    /* Movie Card Container */
    .movie-card {
        background: rgba(255, 255, 255, 0.03);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 12px;
        padding: 12px;
        text-align: center;
        transition: all 0.4s ease;
    }
    .movie-card:hover {
        transform: translateY(-10px);
        background: rgba(255, 255, 255, 0.08);
        border-color: #3b82f6;
        box-shadow: 0 10px 20px rgba(0,0,0,0.5);
    }
    .movie-title {
        font-weight: 600;
        color: #f8fafc;
        margin-top: 10px;
        height: 45px;
        overflow: hidden;
    }
    .movie-genre {
        color: #94a3b8;
        font-size: 0.8rem;
    }
    .match-score {
        color: #10b981;
        font-weight: bold;
        font-size: 0.9rem;
        margin-top: 5px;
    }
    </style>
    """, unsafe_allow_html=True)

# 3. Sidebar Navigation
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/2503/2503508.png", width=100)
    st.title("Settings")
    st.write("Adjust engine parameters:")
    threshold = st.slider("Min Match Percentage", 10, 90, 30)
    st.markdown("---")
    st.info("Uses Cosine Similarity & TMDB API")

# 4. Main App Logic
st.title("🍿 CineMatch AI")
st.write("Smart movie recommendations powered by Machine Learning.")

try:
    _, movies_df = get_processed_data()
    
    # Search Box
    selection = st.selectbox("Select a movie you've enjoyed:", [""] + list(movies_df['title'].values))

    if selection:
        with st.spinner('Calculating recommendations...'):
            results = get_recommendations(selection)
            
            if results:
                st.markdown(f"### Because you liked **{selection}**")
                
                # Create a 3x2 grid
                idx = 0
                for row in range(2):
                    cols = st.columns(3)
                    for col in cols:
                        if idx < len(results):
                            movie = results[idx]
                            poster = get_movie_poster(movie['title'])
                            match_pct = int(movie['score']*100)
                            
                            # Skip if below threshold
                            if match_pct >= threshold:
                                with col:
                                    st.markdown(f"""
                                        <div class="movie-card">
                                            <img src="{poster}" style="width:100%; border-radius:8px;">
                                            <div class="movie-title">{movie['title']}</div>
                                            <div class="movie-genre">{movie['genre']}</div>
                                            <div class="match-score">{match_pct}% Match</div>
                                        </div>
                                    """, unsafe_allow_html=True)
                                    st.write("") # Margin
                            idx += 1
            else:
                st.warning("We don't have enough data to recommend similar movies for this title.")

except Exception as e:
    st.error("Please ensure movies.csv and ratings.csv are in the project folder.")