# 🎬 MovieLLM: Your AI Cinema Concierge 🍿

Ever spent more time *scrolling* for a movie than actually *watching* one? **MovieLLM** is here to fix that. 

Instead of searching by genre or actor, just tell the app how you're feeling. Whether you're "burnt out and need a laugh," "heartbroken and looking for a good cry," or "want to feel like a genius watching a smart thriller," MovieLLM analyzes your mood and delivers a perfect Top 10 list tailored just for you.

## ✨ Features
* **🧠 Vibe-Based Search:** Powered by LLMs (via Groq), the app understands the nuance of your mood and translates it into specific movie parameters.
* **🎞️ Real-Time Movie Data:** Integrated with the TMDB API to pull accurate, up-to-date movie information, posters, and ratings.
* **🎨 Beautiful & Simple UI:** A clean, modern Streamlit interface that feels like a native streaming app.
* **🐳 Fully Dockerized:** Spin up the frontend and backend effortlessly using Docker Compose.

## 🛠️ Tech Stack
* **Frontend:** Streamlit, Requests
* **Backend:** Python, Flask, Gunicorn
* **AI & Data:** Groq API (using the `gpt-oss-120b` model) & TMDB API
* **Infrastructure:** Docker & Docker Compose

---

## 🚀 Getting Started

Want to run this locally? It's super easy. You just need Docker installed and a couple of free API keys.

### 1. Grab your API Keys
You will need two keys to make the magic happen:
1. **Groq API Key:** Get it [here](https://console.groq.com/keys) (Used for the mood analysis).
2. **TMDB API Key:** Get it [here](https://developer.themoviedb.org/docs/getting-started) (Used to fetch the movies).

### 2. Clone and Configure
Clone the repository to your local machine:
```bash
git clone [https://github.com/yourusername/MovieLLM.git](https://github.com/yourusername/MovieLLM.git)
cd MovieLLM
```

Create a `.env` file in the root directory and add your keys:
```env
GROQ_API_KEY=your_groq_api_key_here
TMDB_API_KEY=your_tmdb_api_key_here
```

### 3. Fire it up! 🔥
Make sure Docker is running on your machine, then execute:
```bash
docker-compose up --build
```

That's it! Once the containers are running:
* 🖥️ Open your browser and go to: `http://localhost:8501` to use the app.
* ⚙️ The backend API runs quietly on `http://localhost:5000`.

---

## How it works under the hood
1. **You type your mood:** e.g., *"I've had a long day and need something visually stunning but low-stress."*
2. **The Backend thinks:** Flask sends your prompt to the Groq API with a custom system prompt. The LLM extracts the perfect movie parameters (Genres, Release Years, Minimum Ratings) and returns them as a clean JSON object.
3. **Fetching the films:** The backend takes those parameters and queries the TMDB API, grabbing a broad list of movies, removing duplicates, and sorting them by popularity.
4. **Movie Time:** Streamlit renders the top 10 results in a beautiful grid, complete with posters, ratings, and overviews! Not happy with the first 10? Just hit "Recreate TOP 10" to paginate through more results.

## Contributing
Got ideas to make this even better? Feel free to fork the repo, create a branch, and submit a PR!