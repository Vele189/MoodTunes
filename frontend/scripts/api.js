// api.js
const MoodTunesAPI = {
    baseURL: 'http://localhost:8000',

    // Weather code mappings
    weatherCodes: {
        "0": { condition: "Unknown", description: "Weather information unavailable" },
        "1000": { condition: "Clear", description: "Clear, Sunny" },
        "1100": { condition: "Clear", description: "Mostly Clear" },
        "1101": { condition: "Cloudy", description: "Partly Cloudy" },
        "1102": { condition: "Cloudy", description: "Mostly Cloudy" },
        "1001": { condition: "Cloudy", description: "Cloudy" },
        "2000": { condition: "Foggy", description: "Fog" },
        "2100": { condition: "Foggy", description: "Light Fog" },
        "4000": { condition: "Rainy", description: "Drizzle" },
        "4001": { condition: "Rainy", description: "Rain" },
        "4200": { condition: "Rainy", description: "Light Rain" },
        "4201": { condition: "Rainy", description: "Heavy Rain" },
        "5000": { condition: "Snowy", description: "Snow" },
        "5001": { condition: "Snowy", description: "Flurries" },
        "5100": { condition: "Snowy", description: "Light Snow" },
        "5101": { condition: "Snowy", description: "Heavy Snow" },
        "8000": { condition: "Stormy", description: "Thunderstorm" }
    },

    async getWeather() {
        try {
            const response = await fetch(`${this.baseURL}/weather`);
            if (!response.ok) {
                throw new Error('Weather service unavailable');
            }
            const data = await response.json();
            console.log('Weather data received:', data);
            return data;
        } catch (error) {
            console.error('Error fetching weather:', error);
            return null;
        }
    },

    async getSongsByMood(mood, limit = 10) {
        try {
            const response = await fetch(`${this.baseURL}/songs/${mood}?limit=${limit}`);
            if (!response.ok) {
                throw new Error('Failed to fetch songs');
            }
            const data = await response.json();
            // Map the response to include file paths
            return {
                songs: data.songs.map(song => ({
                    ...song,
                    path: song.file_path // Add the file path for audio playback
                }))
            };
        } catch (error) {
            console.error('Error fetching songs:', error);
            return [];
        }
    },

    updateWeatherDisplay(weatherData) {
        const tempCircle = document.querySelector('.temp-circle');
        const weatherTemp = document.querySelector('.weather-temp');
        const weatherCondition = document.querySelector('.weather-condition');

        if (weatherData && tempCircle && weatherTemp && weatherCondition) {
            // Format temperature
            const temperature = Math.round(weatherData.weather.temperature);
            tempCircle.textContent = `${temperature}°`;

            // Get weather info from code
            const weatherCode = weatherData.weather.condition.toString();
            const weatherInfo = this.weatherCodes[weatherCode] || this.weatherCodes["0"];

            // Update display
            weatherTemp.textContent = weatherInfo.condition;
            weatherCondition.textContent = weatherInfo.description;

            // Optional: Update weather icon based on condition
            this.updateWeatherIcon(weatherInfo.condition);
        }
    },

    updateWeatherIcon(condition) {
        const iconContainer = document.querySelector('.mood-icon');
        if (iconContainer) {
            // Here you could add different background colors or icons based on condition
            const colorMap = {
                "Clear": "#FFD700",     // Gold for clear/sunny
                "Cloudy": "#A9A9A9",    // Gray for cloudy
                "Foggy": "#B8B8B8",     // Light gray for foggy
                "Rainy": "#4682B4",     // Steel blue for rain
                "Snowy": "#FFFFFF",     // White for snow
                "Stormy": "#4A4A4A",    // Dark gray for storms
                "Unknown": "#808080"     // Default gray
            };
            iconContainer.style.backgroundColor = colorMap[condition] || colorMap["Unknown"];
        }
    },

    async initWeather() {
        const weatherData = await this.getWeather();
        if (weatherData) {
            this.updateWeatherDisplay(weatherData);
            // Update every 5 minutes
            setInterval(async () => {
                const updatedWeather = await this.getWeather();
                if (updatedWeather) {
                    this.updateWeatherDisplay(updatedWeather);
                }
            }, 5 * 60 * 1000);
        }
    }
};

export default MoodTunesAPI;