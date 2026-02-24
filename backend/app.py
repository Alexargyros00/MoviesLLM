from flask import Flask, jsonify, request
from dotenv import load_dotenv
from services import get_movie_parameters, fetch_movies_from_tmdb

load_dotenv()

app = Flask(__name__)

@app.get('/health')
def health_check():
    return jsonify({"status": "healthy"}), 200

@app.post('/movies')
def recommend():
    data = request.json
    mood = data.get('mood')
    
    if not mood:
        return jsonify({"error": "No mood provided"}), 400
        
    params = get_movie_parameters(mood)
    if not params:
        return jsonify({"error": "Failed to analyze mood"}), 500
        
    movies = fetch_movies_from_tmdb(params)
    return jsonify({"movies": movies})

if __name__ == "__main__":
    app.run(port=5000, debug=False)
