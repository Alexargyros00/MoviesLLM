"""Backend "services" layer.

This module does two things:
1) Uses Groq (OpenAI-compatible API) to turn a free-text mood into structured
   movie query parameters (as JSON).
2) Uses those parameters to query TMDB's /discover endpoint.
"""

import json
import os
from datetime import datetime

import requests
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

GROQ_BASE_URL = "https://api.groq.com/openai/v1"
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
LLM_MODEL = "openai/gpt-oss-120b"

client = OpenAI(
    base_url=GROQ_BASE_URL,
    api_key=GROQ_API_KEY
)

TMDB_API_KEY = os.getenv("TMDB_API_KEY")
TMDB_BASE_URL = "https://api.themoviedb.org/3"

# Keep one trusted map for all allowed TMDB genres.
GENRE_MAP = {
    "Action": 28, "Adventure": 12, "Animation": 16, "Comedy": 35,
    "Crime": 80, "Documentary": 99, "Drama": 18, "Family": 10751,
    "Fantasy": 14, "History": 36, "Horror": 27, "Music": 10402,
    "Mystery": 9648, "Romance": 10749, "Science Fiction": 878,
    "TV Movie": 10770, "Thriller": 53, "War": 10752, "Western": 37
}


def _genre_ids_from_llm_output(genre_names):
    """Map LLM-returned genre names (or safe numeric IDs) to TMDB genre IDs."""
    genre_ids = []

    for name in genre_names:
        clean_name = str(name).strip()

        # Main path: model returns a known genre name.
        if clean_name in GENRE_MAP:
            genre_ids.append(GENRE_MAP[clean_name])
            continue

        # Fallback: model returns a numeric genre ID as text.
        if clean_name.isdigit():
            numeric_id = int(clean_name)
            if numeric_id in GENRE_MAP.values():
                genre_ids.append(numeric_id)

    return genre_ids


def _dedupe_movies_by_id(movies):
    """De-duplicate TMDB results while preserving order."""
    unique_results = []
    seen_ids = set()

    for movie in movies:
        movie_id = movie["id"]
        if movie_id not in seen_ids:
            unique_results.append(movie)
            seen_ids.add(movie_id)

    return unique_results


def get_movie_parameters(mood_text):
    """Ask the LLM for structured TMDB query params, returned as a JSON string."""
    if not GROQ_API_KEY:
        print("Error: GROQ_API_KEY is not set.")
        return None

    today = datetime.now().strftime("%Y-%m-%d")
    allowed_genres = ", ".join(GENRE_MAP.keys())

    # Ask for genre names first, then map to IDs in Python for safer requests.
    system_prompt = f"""
    You are a movie recommendation assistant.
    Analyze the user's mood and return a JSON object with:
    - genres: list of strings (Genre Names from the provided list). Max 2 genres.
    - start_year: string "yyyy-01-01" (optional)
    - end_year: string "yyyy-mm-dd" (optional)
    - vote_gt: float (optional, default 7.0)
    - vote_lt: float (optional)

    Allowed Genres:
    {allowed_genres}

    Example JSON Response:
    {{
        "genres": ["Drama", "Family"],
        "start_year": "1990-01-01",
        "vote_gt": 7.5
    }}

    Rules:
    - Return ONLY the JSON object.
    - Today is {today}. 'end_year' cannot be in the future.
    - If no relevant genres match the mood, return an empty list for genres.
    """

    try:
        response = client.chat.completions.create(
            model=LLM_MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": mood_text}
            ],
            response_format={"type": "json_object"}
        )
        content = response.choices[0].message.content
        print(f"User mood: {mood_text}")
        print(f"AI response: {content}")
        return content
    except Exception as e:
        print(f"Error calling OpenAI: {e}")
        return None


def fetch_movies_from_tmdb(params):
    """Fetch TMDB /discover results from the JSON params string produced by the LLM."""
    try:
        data = json.loads(params)

        # Translate model output into valid TMDB IDs before the API call.
        genre_names = data.get("genres", [])
        genre_ids = _genre_ids_from_llm_output(genre_names)

        genres_str = ",".join(map(str, genre_ids))
        print(f"Searching TMDB with genre IDs: {genres_str}")

        url = f"{TMDB_BASE_URL}/discover/movie"
        query_params = {
            "api_key": TMDB_API_KEY,
            "sort_by": "popularity.desc",
            "language": "en-US",
            "page": 1,
            "with_release_type": "2|3|4",
            "region": "US"
        }

        if genres_str:
            query_params["with_genres"] = genres_str

        if data.get("start_year"):
            query_params["primary_release_date.gte"] = f"{data.get('start_year')}"
        if data.get("end_year"):
            query_params["primary_release_date.lte"] = f"{data.get('end_year')}"
        if data.get("vote_gt"):
            query_params["vote_average.gte"] = data["vote_gt"]
        if data.get("vote_lt"):
            query_params["vote_average.lte"] = data["vote_lt"]

        # Pull two pages to broaden results, then de-duplicate.
        response_p1 = requests.get(url, params=query_params, timeout=30)
        response_p1.raise_for_status()
        results_p1 = response_p1.json().get("results", [])

        query_params["page"] = 2
        response_p2 = requests.get(url, params=query_params, timeout=30)
        if response_p2.status_code == 200:
            results_p2 = response_p2.json().get("results", [])
        else:
            results_p2 = []

        all_results = results_p1 + results_p2
        unique_results = _dedupe_movies_by_id(all_results)
        return unique_results[:40]

    except Exception as e:
        print(f"Error fetching from TMDB: {e}")
        import traceback
        traceback.print_exc()
        return []
