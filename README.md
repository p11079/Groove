# Groove - A Music Recommendation Engine 🎵

A simple web application that recommends music based on song similarity or user mood. This project uses a Flask backend to serve a machine learning model and a clean, vanilla HTML/CSS/JavaScript frontend.

## ✨ Features

* **Song-based Recommendation:** Enter a song title, and the app will find 10 other songs that are sonically similar.
* **Mood-based Generation:** Get a 15-song playlist by choosing a mood: Happy 😊, Sad 😢, Chill 🧘, or Energetic ⚡.
* **Hybrid Scoring:** The song-based recommendations are a hybrid, blending audio feature similarity (using **Cosine Similarity**) with song popularity.
* **Simple UI:** A clean, dark-mode, tabbed interface to easily switch between recommendation modes.
* **Direct Listen Links:** Each recommendation includes a link to search for the song on YouTube.

## 🛠️ Tech Stack

* **Backend:**
    * **Flask:** For the web server and API endpoints.
    * **Pandas:** For data loading and manipulation.
    * **Scikit-learn:** For scaling audio features and calculating cosine similarity.
* **Frontend:**
    * Vanilla HTML5
    * Vanilla CSS3
    * Vanilla JavaScript (with `fetch` for API calls)
* **Dataset:**
    * Uses a modified Spotify tracks dataset (`tracks_genre.csv`) from Kaggle.

---

## 🚀 Getting Started

Follow these instructions to get a copy of the project up and running on your local machine.

### Prerequisites

You must have the following software installed on your computer:
* [Python 3.x](https://www.python.org/downloads/)
* `pip` (Python package installer)
* [Git](https://git-scm.com/downloads) (for cloning)

### Installation & Setup

1.  **Clone the repository:**
    ```bash
    git clone [https://github.com/your-username/Groove-project.git](https://github.com/your-username/Groove-project.git)
    cd Groove-project
    ```
    *(Replace `your-username` with your actual GitHub username)*

2.  **Add the Dataset (Crucial Step):**
    This project relies on the `tracks_genre.csv` file, which is not included in the repository.
    * You must obtain this file (e.g., from Kaggle).
    * Place the `tracks_genre.csv` file directly inside the **`Backend`** folder.

3.  **Set up the Backend (Python Environment):**
    It is highly recommended to use a Python virtual environment.

    ```bash
    # Navigate into the Backend folder
    cd Backend

    # Create a virtual environment (e.g., named 'venv')
    python -m venv venv

    # Activate the virtual environment
    # On Windows:
    .\venv\Scripts\activate
    # On macOS/Linux:
    source venv/bin/activate
    ```

4.  **Install Dependencies:**
    With your virtual environment active, install all required Python packages from `requirements.txt`.
    ```bash
    pip install -r requirements.txt
    ```

5.  **Frontend Setup:**
    **No setup is needed!** The Flask backend is configured to serve the `Frontend` folder's files automatically.

---

## 🏃 How to Run

1.  Make sure you are in the `Backend` directory and your virtual environment is activated.
2.  Run the Flask application:
    ```bash
    python app.py
    ```
3.  The terminal will show the model loading and then confirm the server is running, typically on `http://127.0.0.1:5000/`.
4.  Open your web browser and go to:
    **[http://127.0.0.1:5000/](http://127.0.0.1:5000/)**

You can now use the application!

---

## 🧠 How It Works

### 1. Song Recommendation (`/recommend`)

When you search for a song, the backend:
1.  Finds the most popular match for your query in the dataset.
2.  Creates a vector of its scaled audio features (`acousticness`, `danceability`, `energy`, etc.).
3.  Calculates the **cosine similarity** between that song's vector and all other songs in the dataset.
4.  Generates a **"hybrid score"** that weights the content similarity (60%) and the song's popularity (40%).
5.  Returns the top 10 songs based on this hybrid score.

### 2. Mood Recommendation (`/mood`)

When you select a mood, the backend:
1.  Applies a pre-defined filter based on the track's `valence` (happiness) and `energy` levels.
2.  Sorts the resulting list of songs by their `popularity` score.
3.  Returns the top 15 most popular songs for that mood.
FYI i got help from Gemini for writing this up as i had never wrote a readme
