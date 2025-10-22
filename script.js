document.addEventListener('DOMContentLoaded', () => {
    const recommendBtn = document.getElementById('recommend-btn');
    const songInput = document.getElementById('song-input');
    const moodSelect = document.getElementById('mood-select');
    const resultsList = document.getElementById('results-list');
    const tabButtons = document.querySelectorAll('.tab-btn');
    const tabContents = document.querySelectorAll('.tab-content');

    // --- Tab Switching Logic ---
    tabButtons.forEach(button => {
        button.addEventListener('click', () => {
            // Deactivate all buttons and content
            tabButtons.forEach(btn => btn.classList.remove('active'));
            tabContents.forEach(content => content.classList.remove('active'));

            // Activate the clicked button and corresponding content
            button.classList.add('active');
            document.getElementById(button.dataset.tab).classList.add('active');
        });
    });

    // --- Main Button Logic ---
    recommendBtn.addEventListener('click', async () => {
        const activeTab = document.querySelector('.tab-btn.active').dataset.tab;
        let url = '';
        
        // Determine which API endpoint to call
        if (activeTab === 'song') {
            const songTitle = songInput.value;
            if (songTitle.trim() === '') {
                alert('Please enter a song title.');
                return;
            }
            url = `http://127.0.0.1:5000/recommend?song_title=${encodeURIComponent(songTitle)}`;
        } else { // activeTab is 'mood'
            const selectedMood = moodSelect.value;
            url = `http://127.0.0.1:5000/mood?mood=${selectedMood}`;
        }
        
        // Show loader and disable button
        recommendBtn.disabled = true;
        recommendBtn.innerHTML = '<div class="loader"></div>';

        try {
            const response = await fetch(url);
            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.error || 'Failed to get recommendations');
            }
            const recommendations = await response.json();
            displayRecommendations(recommendations, activeTab);
        } catch (error) {
            resultsList.innerHTML = `<li class="result-card" style="color: red;">Error: ${error.message}</li>`;
        } finally {
            recommendBtn.disabled = false;
            recommendBtn.innerHTML = 'Get Recommendations';
        }
    });

    function displayRecommendations(recommendations, activeTab) {
        resultsList.innerHTML = '';
        if (recommendations.length === 0) {
            resultsList.innerHTML = '<li class="result-card">No songs found. Try something else!</li>';
            return;
        }

        recommendations.forEach((song, index) => {
            const listItem = document.createElement('li');
            listItem.className = 'result-card';
            
            // Highlight the original song only if in "By Song" mode
            if (activeTab === 'song' && index === 0) {
                listItem.classList.add('original-song');
            }

            const artistsArray = JSON.parse(song.artists);
            const artistsText = artistsArray.join(', ');
            const searchQuery = encodeURIComponent(`${song.name} ${artistsText}`);
            const youtubeLink = `https://www.youtube.com/results?search_query=${searchQuery}`;

            listItem.innerHTML = `
                <div class="song-details">
                    <strong>${song.name}</strong><br>
                    <span class="artist">by ${artistsText}</span>
                </div>
                <a href="${youtubeLink}" target="_blank" class="play-btn">Listen ➔</a>
            `;
            resultsList.appendChild(listItem);
        });
    }
});