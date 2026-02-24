"""Flask API for mood-based movie recommendations.

Endpoints:
- GET /health -> simple healthcheck (used by Docker Compose)
- POST /movies with JSON {"mood": "<free text>"} -> list of TMDB movies
"""

from flask import Flask, jsonify, request
from dotenv import load_dotenv

from services import fetch_movies_from_tmdb, get_movie_parameters

load_dotenv()

app = Flask(__name__)

# Simple healthcheck endpoint used by `docker-compose.yml`.
@app.get("/health")
def health_check():
    return jsonify({"status": "healthy"}), 200

# Main recommendation endpoint consumed by the Streamlit frontend.
@app.post("/movies")
def recommend():
    # Expected request body: {"mood": "<user text>"}
    data = request.json
    mood = data.get('mood')
    
    if not mood:
        return jsonify({"error": "No mood provided"}), 400
        
    params = get_movie_parameters(mood)
    if not params:
        return jsonify({"error": "Failed to analyze mood"}), 500
        
    movies = fetch_movies_from_tmdb(params)
    return jsonify({"movies": movies})

if __name__ == '__main__':
    app.run(port=5000, debug=False)
