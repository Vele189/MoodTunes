class MusicPlayer {
    constructor() {
        // Player state
        this.isPlaying = false;
        this.currentTrackIndex = 0;
        this.playlist = [];

        // UI Elements
        this.playButton = document.querySelector('.control-btn.play');
        this.prevButton = document.querySelector('.control-btn:first-child');
        this.nextButton = document.querySelector('.control-btn:last-child');
        this.playlistContainer = document.querySelector('.playlist-tracks');

        // Bind event listeners
        this.initializeEventListeners();

        // Load initial playlist (mockup data for now)
        this.loadPlaylist();
        document.addEventListener('moodChanged', (event) => this.handleMoodChange(event.detail.mood));
    }

    initializeEventListeners() {
        // Player controls
        this.playButton.addEventListener('click', () => this.togglePlay());
        this.prevButton.addEventListener('click', () => this.playPrevious());
        this.nextButton.addEventListener('click', () => this.playNext());
    }

    loadPlaylist() {
        // Mock data - we'll replace this with API data later
        this.playlist = [
            { title: 'Sunshine Melody', artist: 'The Brights', image: 'path/to/image' },
            { title: 'Raindrop Rhythm', artist: 'The Drizzlers', image: 'path/to/image' },
            { title: 'Snowfall Symphony', artist: 'Frosty Tunes', image: 'path/to/image' }
            // Add more songs as needed
        ];

        this.renderPlaylist();
    }

    renderPlaylist() {
        this.playlistContainer.innerHTML = this.playlist.map((track, index) => `
            <div class="track-item ${index === this.currentTrackIndex ? 'playing' : ''}" 
                 data-index="${index}"
                 data-path="${track.file_path}">
                <div class="track-info">
                    <h3 class="track-title">${track.title}</h3>
                    <p class="track-artist">${track.artist}</p>
                </div>
            </div>
        `).join('');
    
        // Add click listeners to tracks
        const tracks = document.querySelectorAll('.track-item');
        tracks.forEach(track => {
            track.addEventListener('click', () => {
                const index = parseInt(track.dataset.index);
                this.playTrack(index);
            });
        });
    }

    togglePlay() {
        this.isPlaying = !this.isPlaying;
        this.updatePlayButton();
        // Here we'll add actual audio playback later
    }

    updatePlayButton() {
        this.playButton.innerHTML = this.isPlaying ? '❚❚' : '▶';
    }

    playTrack(index) {
        this.currentTrackIndex = index;
        this.isPlaying = true;
        this.updatePlayButton();
        this.renderPlaylist(); // Update visual state
        // Here we'll add actual audio playback later
    }

    playNext() {
        this.currentTrackIndex = (this.currentTrackIndex + 1) % this.playlist.length;
        this.playTrack(this.currentTrackIndex);
    }

    playPrevious() {
        this.currentTrackIndex = (this.currentTrackIndex - 1 + this.playlist.length) % this.playlist.length;
        this.playTrack(this.currentTrackIndex);
    }

// Add this method to MusicPlayer class
handleMoodChange(mood) {
    // Mock playlists for different moods
    const moodPlaylists = {
        happy: [
            { title: 'Sunshine Melody', artist: 'The Brights' },
            { title: 'Happy Days', artist: 'Joy Band' }
        ],
        sad: [
            { title: 'Raindrop Rhythm', artist: 'The Drizzlers' },
            { title: 'Melancholy Moon', artist: 'Night Souls' }
        ],
        energetic: [
            { title: 'Power Up', artist: 'Energy Crew' },
            { title: 'Dynamic Drive', artist: 'The Motivators' }
        ],
        calm: [
            { title: 'Peaceful Path', artist: 'Zen Masters' },
            { title: 'Gentle Waves', artist: 'Ocean Sound' }
        ],
        angry: [
            { title: 'Thunder Roll', artist: 'Storm Chasers' },
            { title: 'Lightning Strike', artist: 'Electric Mind' }
        ]
    };

    // Update playlist
    this.playlist = moodPlaylists[mood] || [];
    this.currentTrackIndex = 0;
    this.isPlaying = false;
    this.updatePlayButton();
    this.renderPlaylist();
}
    
}

// Initialize player when document is loaded
document.addEventListener('DOMContentLoaded', () => {
    const player = new MusicPlayer();
});

