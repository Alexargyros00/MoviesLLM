import json
import os

import requests
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

GROQ_BASE_URL = "https://api.groq.com/openai/v1"
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
LLM_MODEL = "openai/gpt-oss-120b"

client = OpenAI(
    base_url=GROQ_BASE_URL,
    api_key=GROQ_API_KEY,
)

TMDB_API_KEY = os.getenv("TMDB_API_KEY")
TMDB_BASE_URL = "https://api.themoviedb.org/3"


def get_movie_parameters(mood_text):
    if not GROQ_API_KEY:
        print("Error: GROQ_API_KEY is not set.")
        return None

    # Simple prompt (we'll improve it later once the MVP works end-to-end).
    system_prompt = """
    You are a movie recommendation assistant.
    Analyze the user's mood and return a JSON object with:
    - genres: list of TMDB genre IDs (numbers). Max 2.
    - start_year: string "yyyy-01-01" (optional)
    - end_year: string "yyyy-mm-dd" (optional)
    - vote_gt: float (optional)
    - vote_lt: float (optional)

    Rules:
    - Return ONLY the JSON object.
    """

    try:
        response = client.chat.completions.create(
            model=LLM_MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": mood_text},
            ],
            response_format={"type": "json_object"},
        )
        content = response.choices[0].message.content
        print(f"User mood: {mood_text}")
        print(f"AI response: {content}")
        return content
    except Exception as e:
        print(f"Error calling OpenAI: {e}")
        return None


def fetch_movies_from_tmdb(params):
    try:
        data = json.loads(params)

        genre_ids = data.get("genres", [])
        genres_str = ",".join(map(str, genre_ids))

        url = f"{TMDB_BASE_URL}/discover/movie"
        query_params = {
            "api_key": TMDB_API_KEY,
            "sort_by": "popularity.desc",
            "language": "en-US",
            "page": 1,
        }

        if genres_str:
            query_params["with_genres"] = genres_str
        if data.get("start_year"):
            query_params["primary_release_date.gte"] = data["start_year"]
        if data.get("end_year"):
            query_params["primary_release_date.lte"] = data["end_year"]
        if data.get("vote_gt"):
            query_params["vote_average.gte"] = data["vote_gt"]
        if data.get("vote_lt"):
            query_params["vote_average.lte"] = data["vote_lt"]

        response = requests.get(url, params=query_params, timeout=30)
        response.raise_for_status()
        return response.json().get("results", [])

    except Exception as e:
        print(f"Error fetching from TMDB: {e}")
        import traceback

        traceback.print_exc()
        return []
