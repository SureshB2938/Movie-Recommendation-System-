const API_KEY = "f34718af3ff0279811053f8000eca50d";

// Slideshow Images
const slideshowImages = [
    "/static/media/1.png",
    "/static/media/2.png",
    "/static/media/3.png",
    "/static/media/4.png"
];
let currentImageIndex = 0;

// Change slideshow image every 3 seconds
function changeSlideshowImage() {
    const imageElement = document.getElementById('currentImage');
    currentImageIndex = (currentImageIndex + 1) % slideshowImages.length;
    imageElement.src = slideshowImages[currentImageIndex];
}
setInterval(changeSlideshowImage, 3000);

// Helper function to fetch and display items (movies, TV series, or anime)
function fetchAndDisplay(endpoint, containerId, type) {
    fetch(endpoint)
        .then(response => response.json())
        .then(data => {
            const container = document.getElementById(containerId);
            container.innerHTML = ''; // Clear existing content
            data.results.slice(0, 5).forEach(item => {
                const itemDiv = document.createElement('div');
                itemDiv.classList.add('col-md-2', 'item-container');  // Added item-container class

                const ratingCircle = item.vote_average ? `
                    <div class="rating-circle">${item.vote_average}</div>
                ` : '';

                itemDiv.innerHTML = `
                    ${ratingCircle}
                    <img src="https://image.tmdb.org/t/p/w500/${item.poster_path}" 
                         alt="${item.title || item.name}" 
                         class="item-poster" 
                         data-id="${item.id}" 
                         onclick="showItemDetails('${type}', ${item.id})">
                    <p>${item.title || item.name}</p>
                `;
                container.appendChild(itemDiv);
            });
        });
}

// Fetch and display trending Indian movies
function fetchTrendingIndianMovies() {
    const endpoint = `https://api.themoviedb.org/3/trending/movie/week?api_key=${API_KEY}&language=hi`;
    fetchAndDisplay(endpoint, 'trendingIndianMovies', 'movie');
}

// Fetch and display trending Indian TV series
function fetchTrendingIndianTV() {
    const endpoint = `https://api.themoviedb.org/3/trending/tv/week?api_key=${API_KEY}&language=hi`;
    fetchAndDisplay(endpoint, 'trendingIndianTV', 'tv');
}

// Fetch and display trending Indian anime
function fetchTrendingIndianAnime() {
    const endpoint = `https://api.themoviedb.org/3/discover/tv?api_key=${API_KEY}&with_genres=16&language=hi`;
    fetchAndDisplay(endpoint, 'trendingIndianAnime', 'anime');
}

// Show item details in a modal
function showItemDetails(type, id) {
    const endpoint = `https://api.themoviedb.org/3/${type}/${id}?api_key=${API_KEY}`;
    fetch(endpoint)
        .then(response => response.json())
        .then(data => {
            document.getElementById('itemTitle').textContent = data.title || data.name;
            document.getElementById('itemOverview').textContent = data.overview || "No overview available.";
            document.getElementById('itemReleaseDate').textContent = data.release_date || data.first_air_date || "N/A";
            document.getElementById('itemRating').textContent = data.vote_average || "N/A";
            document.getElementById('itemGenres').textContent = data.genres ? data.genres.map(genre => genre.name).join(', ') : "N/A";
            document.getElementById('itemLanguages').textContent = data.spoken_languages ? data.spoken_languages.map(lang => lang.name).join(', ') : "N/A";
            document.getElementById('itemRuntime').textContent = data.runtime ? `${data.runtime} mins` : "N/A";
            document.getElementById('itemOriginalLanguage').textContent = data.original_language || "N/A";
            document.getElementById('itemPopularity').textContent = data.popularity || "N/A";

            document.getElementById('itemPoster').src = `https://image.tmdb.org/t/p/w500/${data.poster_path}`;

            // Display the modal
            const modal = new bootstrap.Modal(document.getElementById('itemDetailModal'));
            modal.show();
        });
}

// Initialize functions on page load
document.addEventListener('DOMContentLoaded', () => {
    fetchTrendingIndianMovies();
    fetchTrendingIndianTV();
    fetchTrendingIndianAnime();
});
