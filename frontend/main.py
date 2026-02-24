import os

import requests
import streamlit as st

PAGE_SIZE = 10
GRID_COLUMNS = 5
TMDB_POSTER_BASE_URL = "https://image.tmdb.org/t/p/w500"


def _normalize_backend_url(raw_url: str) -> str:
    """Normalize BACKEND_URL so it works for both `localhost:5000` and full URLs."""
    url = raw_url.strip().rstrip("/")
    if "://" not in url:
        url = f"http://{url}"
    return url


# Used by the frontend to call the Flask backend.
BACKEND_URL = _normalize_backend_url(os.getenv("BACKEND_URL", "http://localhost:5000"))


def _configure_page() -> None:
    """Set the Streamlit page config and inject the CSS styling."""
    st.set_page_config(
        page_title="Movie Recommender",
        page_icon="🎬",
        layout="wide",
    )

    # Custom CSS for modern look.
    st.markdown(
        """
    <style>
    .big-font {
        font-size:30px !important;
        font-weight: bold;
    }
    .movie-card {
        background-color: #262730;
        padding: 20px;
        border-radius: 10px;
        margin-bottom: 20px;
    }
    .movie-title {
        font-size: 1.1rem;
        font-weight: bold;
        margin-top: 10px;
        margin-bottom: 5px;
        height: 2.8em;
        line-height: 1.4em;
        overflow: hidden;
        display: -webkit-box;
        -webkit-line-clamp: 2;
        -webkit-box-orient: vertical;
        text-overflow: ellipsis;
    }
    .movie-img {
        width: 100%;
        border-radius: 5px;
        aspect-ratio: 2/3;
        object-fit: cover;
    }
    .movie-placeholder {
        width: 100%;
        border-radius: 5px;
        aspect-ratio: 2/3;
        background-color: #333333;
        display: flex;
        align-items: center;
        justify-content: center;
        color: #666;
    }
    [data-testid="stToolbar"] {
        visibility: hidden !important;
        display: none !important;
    }
    header {
        visibility: hidden !important;
        display: none !important;
    }
    </style>
    """,
        unsafe_allow_html=True,
    )

    st.markdown(
        '<p class="big-font">🎬 TOP 10 movies for you current mood</p>',
        unsafe_allow_html=True,
    )
    st.write("Tell us how you're feeling, and we'll find the perfect movie for you.")


def _init_session_state() -> None:
    """Streamlit reruns the script; keep state in `st.session_state`."""
    if "movies_list" not in st.session_state:
        st.session_state.movies_list = []
    if "current_page" not in st.session_state:
        st.session_state.current_page = 0


def _render_input():
    """Mood input + submit button."""
    with st.container():
        col1, col2 = st.columns([3, 1], vertical_alignment="bottom")
        with col1:
            mood = st.text_input(
                "How are you feeling right now?",
                placeholder="e.g., I'm feeling nostalgic and want something heartwarming from the 90s",
            )
        with col2:
            submit_btn = st.button("Find Movies", type="primary", use_container_width=True)

    return mood, submit_btn


def _fetch_movies_for_mood(mood: str) -> None:
    """Call the backend and store results into session state."""
    with st.spinner("Analyzing your mood and finding movies..."):
        try:
            response = requests.post(
                f"{BACKEND_URL}/movies",
                json={"mood": mood},
                timeout=120,
            )

            if response.status_code == 200:
                data = response.json()
                st.session_state.movies_list = data.get("movies", [])
                st.session_state.current_page = 0

                if not st.session_state.movies_list:
                    st.warning("No movies found. Try a different description!")
            else:
                st.error(f"Error: {response.text}")

        except requests.exceptions.ConnectionError:
            st.error(f"Could not connect to the backend at {BACKEND_URL}.")
        except Exception as e:
            st.error(f"An error occurred: {e}")


def _render_movies_grid() -> None:
    """Render the current page of movies (10 at a time) in a 5-column grid."""
    movies = st.session_state.movies_list
    if not movies:
        return

    start_idx = st.session_state.current_page * PAGE_SIZE
    end_idx = start_idx + PAGE_SIZE
    current_batch = movies[start_idx:end_idx]

    if not current_batch:
        return

    st.success("TOP 10 list created!")

    cols = st.columns(GRID_COLUMNS)
    for idx, movie in enumerate(current_batch):
        with cols[idx % GRID_COLUMNS]:
            poster_path = movie.get("poster_path")
            if poster_path:
                img_url = f"{TMDB_POSTER_BASE_URL}{poster_path}"
                st.markdown(f'<img src="{img_url}" class="movie-img">', unsafe_allow_html=True)
            else:
                st.markdown('<div class="movie-placeholder"></div>', unsafe_allow_html=True)

            title = movie.get("title")
            st.markdown(
                f'<div class="movie-title" title="{title}">{title}</div>',
                unsafe_allow_html=True,
            )
            st.write(f"⭐ {movie.get('vote_average')}/10")
            st.caption(movie.get("release_date", "Unknown Date"))
            with st.expander("Overview"):
                st.write(movie.get("overview"))

    # Pagination: show the button only if there are more movies left.
    if end_idx < len(movies):
        if st.button("Recreate TOP 10", use_container_width=True):
            st.session_state.current_page += 1
            st.rerun()


_configure_page()
_init_session_state()

mood, submit_btn = _render_input()
if submit_btn and mood:
    _fetch_movies_for_mood(mood)

_render_movies_grid()
