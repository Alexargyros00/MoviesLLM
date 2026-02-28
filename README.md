# MovieLLM

I built MovieLLM because I was spending more time scrolling for movies than actually watching them. 

Instead of searching by genre or actor, just tell the app how you're feeling. Whether you're "burnt out and need a laugh," "heartbroken and looking for a good cry," or "want to watch a smart thriller," MovieLLM analyzes your mood and gives you a Top 10 list that fits what you're looking for.

## What it does
* **Mood-based search:** It uses an LLM (via Groq) to figure out the vibe of your prompt and turn that into specific movie parameters like genres and release years.
* **Live data:** It connects to the TMDB API so all the posters, ratings, and descriptions are accurate and up to date.
* **Clean interface:** The frontend is built with Streamlit, keeping the design simple and easy to use.
* **Docker ready:** You can run both the frontend and backend easily with Docker Compose.

## How it's built
* **Frontend:** Streamlit, Python Requests
* **Backend:** Python, Flask, Gunicorn
* **AI & Data:** Groq API (using the gpt-oss-120b model) and the TMDB API
* **Infrastructure:** Docker and Docker Compose

---

## How to run it

If you want to try it out on your machine, you will need Docker and a couple of free API keys.

### 1. Get your API keys
You will need two of them:
1. **Groq API Key:** Get one from their [console](https://console.groq.com/keys) to handle the AI parsing.
2. **TMDB API Key:** Get one from the [TMDB developer site](https://developer.themoviedb.org/docs/getting-started) to fetch the actual movies.

### 2. Set up the repository
Clone the code to your local machine:
```bash
git clone https://github.com/yourusername/MovieLLM.git
cd MovieLLM
```

Then create a `.env` file in the main folder to hold your keys:
```env
GROQ_API_KEY=your_groq_api_key_here
TMDB_API_KEY=your_tmdb_api_key_here
```

### 3. Start the containers
With Docker running on your machine, just build and start everything:
```bash
docker-compose up --build
```

That's it! Once it's running:
* Go to `http://localhost:8501` in your browser to see the app.
* The backend API runs quietly in the background on `http://localhost:5000`.

---

## How it works under the hood
1. **You enter your mood:** like *"I've had a long day and need something visually stunning but low-stress."*
2. **The backend processes it:** It sends your input to the Groq API. The LLM extracts the perfect movie parameters (Genres, Release Years, Minimum Ratings) and returns them as a clean JSON object.
3. **Fetching from TMDB:** The server uses those parameters to query the TMDB API, grabs a broad list of movies, removes any duplicates, and sorts them by popularity.
4. **Displaying the results:** The Streamlit frontend renders the top 10 movies. If you don't like the first 10, you can just hit "Recreate TOP 10" to paginate through more results.

## Contributing
If you have ideas to make this even better, feel free to fork the repository, make your changes, and submit a pull request!