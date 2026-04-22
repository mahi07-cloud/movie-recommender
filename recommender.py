import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity
import streamlit as st
import requests

# This keeps the heavy matrix in RAM so the app is instant after the first load
@st.cache_resource
def get_processed_data():
    movies = pd.read_csv('movies.csv')
    ratings = pd.read_csv('ratings.csv')
    
    # Filter: Only keep movies with more than 50 ratings to reduce noise
    movie_counts = ratings.groupby('movieId').count()['rating']
    popular_movies = movie_counts[movie_counts > 50].index
    filtered_ratings = ratings[ratings['movieId'].isin(popular_movies)]
    
    # Create the Pivot Table
    movie_ratings = pd.merge(filtered_ratings, movies, on='movieId')
    pivot = movie_ratings.pivot_table(index='userId', columns='title', values='rating').fillna(0)
    
    # Calculate Similarity Matrix
    similarity = cosine_similarity(pivot.T)
    sim_df = pd.DataFrame(similarity, index=pivot.columns, columns=pivot.columns)
    
    return sim_df, movies

def get_movie_poster(movie_title):
    clean_title = movie_title.split('(')[0].strip()
    api_key = "b17f6cced99a5787641ef5b049a76752" 
    url = f"https://api.themoviedb.org/3/search/movie?api_key={api_key}&query={clean_title}"
    
    try:
        response = requests.get(url).json()
        if response['results'] and 'poster_path' in response['results'][0]:
            path = response['results'][0]['poster_path']
            return f"https://image.tmdb.org/t/p/w500{path}"
        return "https://via.placeholder.com/500x750?text=No+Poster"
    except Exception:
        return "https://via.placeholder.com/500x750?text=Error"

def get_recommendations(target_movie):
    sim_df, movies_df = get_processed_data()
    if target_movie not in sim_df.columns:
        return None
    
    # Get top 6 similar movies
    scores = sim_df[target_movie].sort_values(ascending=False)[1:7]
    
    recommendations = []
    for title in scores.index:
        genre = movies_df[movies_df['title'] == title]['genres'].values[0]
        recommendations.append({
            "title": title, 
            "score": scores[title], 
            "genre": genre.replace('|', ' • ')
        })
    return recommendations