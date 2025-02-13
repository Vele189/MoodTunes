import MoodTunesAPI from './api.js';
console.log('Mood.js is loading...');

class MoodSelector {
    constructor() {
        console.log('MoodSelector initializing...'); 
        this.moods = {
            happy: '#FFD700',
            sad: '#808080',
            energetic: '#FF4500',
            calm: '#4682B4',
            angry: '#8B0000'
        };

        this.moodButtons = document.querySelectorAll('.mood-button');
        console.log('Found mood buttons:', this.moodButtons.length); 
        this.currentMood = null;
        this.initializeEventListeners();
        MoodTunesAPI.initWeather();
    }

    initializeEventListeners() {
        console.log('Setting up event listeners...');
        this.moodButtons.forEach(button => {
            button.addEventListener('click', () => {
                this.handleMoodSelection(button);
            });
        });
    }

    handleMoodSelection(selectedButton) {
        console.log('Mood clicked:', selectedButton.textContent);
    
        this.moodButtons.forEach(button => {
            button.classList.remove('active');
        });
    
        selectedButton.classList.add('active');
        this.currentMood = selectedButton.textContent.toLowerCase();
        console.log('Current mood:', this.currentMood);
    
        this.updatePlaylist();
    }

    async updatePlaylist() {
        try {
            console.log('Fetching playlist for mood:', this.currentMood);
            this.setLoadingState(true);
            const playlistData = await MoodTunesAPI.getSongsByMood(this.currentMood);
            console.log('Playlist data received:', playlistData);
            
            if (playlistData) {
                this.renderPlaylist(playlistData);
                
                // Update playlist title
                const playlistTitle = document.querySelector('.player-info h2');
                if (playlistTitle) {
                    playlistTitle.textContent = `${this.currentMood.charAt(0).toUpperCase() + this.currentMood.slice(1)} Vibes`;
                }
            }
        } catch (error) {
            console.error('Error updating playlist:', error);
        } finally {
            this.setLoadingState(false);
        }
    }

    renderPlaylist(data) {
        const playlistContainer = document.querySelector('.playlist-tracks');
        if (!playlistContainer) return;
    
        playlistContainer.innerHTML = data.songs.map(song => `
            <div class="track-item">
                <div class="track-info">
                    <h3 class="track-title">${song.title}</h3>
                    <p class="track-artist">${song.artist}</p>
                </div>
            </div>
        `).join('');
    }

    setLoadingState(isLoading) {
        this.moodButtons.forEach(button => {
            button.disabled = isLoading;
        });
    }
}

document.addEventListener('DOMContentLoaded', () => {
    console.log('DOM Content Loaded - creating MoodSelector');
    const moodSelector = new MoodSelector();
});