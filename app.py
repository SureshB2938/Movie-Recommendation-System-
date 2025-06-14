from flask import Flask, render_template, request, jsonify
import requests
from deepface import DeepFace  # Make sure DeepFace is installed
from textblob import TextBlob  # For text sentiment analysis
from datetime import datetime
app = Flask(__name__)



TMDB_API_KEY = ''
TMDB_API_URL = 'https://api.themoviedb.org/3'
TMDB_BASE_URL = 'https://api.themoviedb.org/3'  # Added missing base URL

# Function to get all genres from TMDB
def get_genres():
    url = f'{TMDB_API_URL}/genre/movie/list'
    params = {
        'api_key': TMDB_API_KEY,
        'language': 'en-US'
    }
    response = requests.get(url, params=params)
    data = response.json()
    if data.get('genres'):
        return data['genres']
    else:
        return []

# Function to get movie details including director, screenplay, reviews, and trailer
def get_movie_details(movie_id):
    url = f'{TMDB_API_URL}/movie/{movie_id}'
    params = {
        'api_key': TMDB_API_KEY,
        'language': 'en-US'
    }
    response = requests.get(url, params=params)
    data = response.json()

    # Fetch the movie credits (director, screenplay)
    credits_url = f'{TMDB_API_URL}/movie/{movie_id}/credits'
    credits_response = requests.get(credits_url, params={'api_key': TMDB_API_KEY})
    credits_data = credits_response.json()

    director = next((person['name'] for person in credits_data.get('crew', []) if person['job'] == 'Director'), 'Unknown')
    screenplay_writer = next((person['name'] for person in credits_data.get('crew', []) if person['job'] == 'Screenplay'), 'Unknown')

    # Fetch reviews for the movie
    reviews_url = f'{TMDB_API_URL}/movie/{movie_id}/reviews'
    reviews_response = requests.get(reviews_url, params={'api_key': TMDB_API_KEY})
    reviews_data = reviews_response.json()
    reviews = reviews_data.get('results', [])

    # Fetch the movie trailer (YouTube link)
    videos_url = f'{TMDB_API_URL}/movie/{movie_id}/videos'
    videos_response = requests.get(videos_url, params={'api_key': TMDB_API_KEY})
    videos_data = videos_response.json()
    youtube_trailer = None
    for video in videos_data.get('results', []):
        if video['site'] == 'YouTube' and video['type'] == 'Trailer':
            youtube_trailer = f"https://www.youtube.com/watch?v={video['key']}"
            break

    return {
        'title': data.get('title'),
        'poster_path': data.get('poster_path'),
        'rating': data.get('vote_average'),
        'release_date': data.get('release_date'),
        'overview': data.get('overview'),
        'director': director,
        'screenplay': screenplay_writer,
        'reviews': reviews,
        'trailer_link': youtube_trailer,
    }


# Function to get trending movies
def get_trending_movies():
    url = f'{TMDB_API_URL}/trending/movie/day?api_key={TMDB_API_KEY}'
    response = requests.get(url)
    return response.json()['results']

# Function to get trending TV shows
def get_trending_series():
    url = f'{TMDB_API_URL}/trending/tv/day?api_key={TMDB_API_KEY}'
    response = requests.get(url)
    return response.json()['results']

# Function to search for movies
def search_movies(query):
    url = f'{TMDB_API_URL}/search/movie?api_key={TMDB_API_KEY}&query={query}'
    response = requests.get(url)
    return response.json()['results']

@app.route('/')
def index():
    trending_movies = get_trending_movies()
    trending_series = get_trending_series()
    return render_template('index.html', trending_movies=trending_movies, trending_series=trending_series)

@app.route('/search', methods=['GET'])
def search():
    query = request.args.get('query')
    if query:
        search_results = search_movies(query)
    else:
        search_results = []
    trending_movies = get_trending_movies()
    trending_series = get_trending_series()
    return render_template('index.html', trending_movies=trending_movies, trending_series=trending_series, search_results=search_results)


def get_filtered_movies(filters):
    """Fetch filtered movies from TMDB API based on the provided filters."""
    url = f"{TMDB_API_URL}/discover/movie?api_key={TMDB_API_KEY}&language=en-US"
    
    # Applying filters to the URL
    if filters.get('genre'):
        url += f"&with_genres={filters['genre']}"
    if filters.get('certificate'):
        url += f"&certification={filters['certificate']}"
    if filters.get('language'):
        url += f"&language={filters['language']}"
    if filters.get('year'):
        url += f"&primary_release_year={filters['year']}"
    if filters.get('month'):
        url += f"&release_date.gte={filters['year']}-{filters['month']}-01&release_date.lte={filters['year']}-{filters['month']}-31"

    response = requests.get(url)
    if response.status_code == 200:
        return response.json().get('results', [])
    else:
        return []

@app.route('/recommendations', methods=['GET', 'POST'])
def recommendations():
    """Handle recommendations page with filters."""
    filters = {}
    if request.method == 'POST':
        filters['genre'] = request.form.get('genre')
        filters['certificate'] = request.form.get('certificate')
        filters['language'] = request.form.get('language')
        filters['year'] = request.form.get('year')
        filters['month'] = request.form.get('month')

    # Fetch filtered movies based on the selected filters
    movies = get_filtered_movies(filters)
    
    # Fetch all genres for filter options (this could be static or dynamic from TMDB)
    genre_response = requests.get(f"{TMDB_API_URL}/genre/movie/list?api_key={TMDB_API_KEY}&language=en-US")
    genres = genre_response.json().get('genres', [])

    return render_template('recommendations.html', movies=movies, genres=genres, filters=filters)

@app.route("/details/<item_type>/<int:item_id>")
def more_details(item_type, item_id):
    """Fetch detailed information about a movie or TV series."""
    
    # TMDB API URL for fetching detailed information
    url = f"{TMDB_API_URL}/{item_type}/{item_id}?api_key={TMDB_API_KEY}&language=en-US&append_to_response=credits,images,reviews,videos,watch/providers"
    response = requests.get(url)
    
    if response.status_code == 200:
        details = response.json()
        print(details)  # Debugging - Print full API response

        # Fetch similar movies/TV series
        similar_url = f"{TMDB_API_URL}/{item_type}/{item_id}/similar?api_key={TMDB_API_KEY}&language=en-US"
        similar_response = requests.get(similar_url)
        similar_movies = similar_response.json().get('results', [])

        # Fetch crew members (limit to top 5)
        crew = details.get("credits", {}).get("crew", [])[:5] 

        # Fetch trailers from YouTube
        videos = details.get("videos", {}).get("results", [])
        trailer = next((video for video in videos if video.get("type") == "Trailer" and video.get("site") == "YouTube"), None)

        # Fetch watch providers
        watch_providers = details.get("watch/providers", {}).get("results", {}).get("US", {}).get("flatrate", [])
        print("Watch Providers:", watch_providers)  # Debugging


        # Fetch reviews (limit to top 5)
        reviews = details.get("reviews", {}).get("results", [])
        for review in reviews:
            review["created_at"] = review["created_at"].split("T")[0] 

        return render_template("moredetails.html", details=details, item_type=item_type, 
                               similar_movies=similar_movies, trailer=trailer, crew=crew, 
                               watch_providers=watch_providers, posters=posters, reviews=reviews)

    else:
        return f"Error fetching data: {response.status_code}", 404

def get_movie_data(endpoint, params={}):
    params['api_key'] = TMDB_API_KEY
    url = f"{TMDB_BASE_URL}/{endpoint}"
    response = requests.get(url, params=params)
    return response.json()

# Route for movie_chat.html
@app.route('/movie_chat')
def movie_chat():
    return render_template('movie_chat.html')

@app.route('/underrated', methods=['GET'])
def underrated():
    genre = request.args.get('genre')
    search_query = request.args.get('search')  # User's search query
    sort_by = request.args.get('sort_by', 'popularity.asc')  # Default sort by popularity
    page = int(request.args.get('page', 1))  # Default to page 1

    # Get all genres for filtering
    genres = get_genres()

    url = f'{TMDB_API_URL}/discover/movie'
    params = {
        'api_key': TMDB_API_KEY,
        'language': 'en-US',
        'sort_by': sort_by,
        'page': page,
        'vote_average.gte': 6,  # Underrated movies have a minimum rating of 6
        'vote_count.gte': 50,  # At least 50 votes to avoid too few reviews
    }

    # Apply genre filter
    if genre:
        params['with_genres'] = genre

    # Apply search query filter
    if search_query:
        params['query'] = search_query

    # Fetch the movies
    response = requests.get(url, params=params)
    data = response.json()

    # Handle the response
    if data.get('results'):
        movies = data['results']
        total_pages = data.get('total_pages', 1)
    else:
        movies = []
        total_pages = 1

    return render_template('underrated.html', 
                           movies=movies, 
                           genres=genres, 
                           selected_genre=genre, 
                           search_query=search_query,
                           total_pages=total_pages, 
                           current_page=page, 
                           sort_by=sort_by)


# Route to fetch detailed movie information
@app.route('/movie_details/<int:movie_id>', methods=['GET'])
def movie_details(movie_id):
    movie_details = get_movie_details(movie_id)
    return jsonify(movie_details)

@app.route('/scene_search', methods=['GET'])
def scene_search():
    query = request.args.get('query', '').lower()
    
    # Check if the user entered multiple keywords (separated by commas)
    if query:
        # Split the query into a list of keywords, allowing commas as the separator
        scene_keywords = [keyword.strip() for keyword in query.split(',')]

        # Initialize an empty list to hold matched movies
        matched_movies = []

        # Search movies by title using TMDB API
        movie_url = f'{TMDB_API_URL}/search/movie'
        params = {
            'api_key': TMDB_API_KEY,
            'query': query,
            'language': 'en-US'
        }
        movie_response = requests.get(movie_url, params=params)
        movies = movie_response.json().get('results', [])

        for movie in movies:
            # Search for relevant keywords within the movie's overview
            overview = movie.get('overview', '').lower()
            
            # Check if any of the user's keywords are found in the movie's overview
            if any(keyword in overview for keyword in scene_keywords):
                matched_movies.append({
                    'title': movie['title'],
                    'overview': movie['overview'],
                    'release_date': movie['release_date'],
                    'poster_path': movie.get('poster_path', '')
                })

        return jsonify({'scenes': matched_movies})

    return jsonify({'scenes': []})

# Route for the movie search page
@app.route('/movie_search', methods=['GET'])
def movie_search():
    query = request.args.get('query', '')
    scenes = []

    if query:
        # Search movies using TMDB API
        url = f'{TMDB_API_URL}/search/movie'
        params = {
            'api_key': TMDB_API_KEY,
            'query': query,
            'language': 'en-US'
        }
        response = requests.get(url, params=params)
        movies = response.json().get('results', [])

        # For each movie, simulate scene data by using the movie overview and title
        for movie in movies:
            overview = movie.get('overview', '').lower()
            if any(keyword in overview for keyword in ['battle', 'fight', 'war', 'duel', 'heroes']):
                scenes.append({
                    'title': movie['title'],
                    'overview': movie['overview'],
                    'release_date': movie['release_date'],
                    'poster_path': movie.get('poster_path', '')
                })

    return render_template('sbs.html', scenes=scenes)

@app.route('/emotion_recommendations')
def emotion_recommendations():
    return render_template('emotion_recommendation.html')

@app.route('/recommend', methods=['GET'])
def recommend():
    emotion = request.args.get('emotion')

    genre_map = {
        "happy": 35,     # Comedy
        "sad": 18,       # Drama
        "angry": 28,     # Action
        "fearful": 27,   # Horror
        "neutral": 10749 # Romance
    }
    genre_id = genre_map.get(emotion, 35)  # Default to comedy if emotion not found

    # Fetch movies based on genre
    try:
        response = requests.get(f"{TMDB_API_URL}/discover/movie", params={
            "api_key": TMDB_API_KEY,
            "with_genres": genre_id,
            "sort_by": "popularity.desc",
            "language": "en-US",
            "page": 1
        })

        if response.status_code == 200:
            movies = response.json().get('results', [])
            return jsonify({"movies": movies})  # Return as JSON to be consumed by JS

        else:
            return jsonify({"error": "Failed to fetch movie recommendations"}), 500

    except Exception as e:
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500

@app.route('/movie/<int:movie_id>', methods=['GET'])
def movie_details_view(movie_id):
    # Fetch movie details from TMDB API
    response = requests.get(f"{TMDB_API_URL}/movie/{movie_id}", params={"api_key": TMDB_API_KEY})
    movie = response.json()

    # Fetch trailer link
    videos = requests.get(f"{TMDB_API_URL}/movie/{movie_id}/videos", params={"api_key": TMDB_API_KEY}).json()
    trailer_key = next(
        (video['key'] for video in videos.get('results', []) if video['type'] == "Trailer"), None
    )
    trailer_url = f"https://www.youtube.com/watch?v={trailer_key}" if trailer_key else None

    return jsonify({
        "title": movie.get("title"),
        "poster_path": f"https://image.tmdb.org/t/p/w500{movie.get('poster_path')}",
        "vote_average": movie.get("vote_average"),
        "genres": [genre['name'] for genre in movie.get("genres", [])],
        "overview": movie.get("overview"),  # Include the overview field here
        "trailer_url": trailer_url
    })




if __name__ == '__main__':
    app.run(debug=True)
