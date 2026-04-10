# 📺 YouTube Playlist Dashboard

[![React](https://img.shields.io/badge/React-20232A?style=for-the-badge&logo=react&logoColor=61DAFB)](https://reactjs.org/)
[![Flask](https://img.shields.io/badge/Flask-000000?style=for-the-badge&logo=flask&logoColor=white)](https://flask.palletsprojects.com/)
[![Vite](https://img.shields.io/badge/Vite-646CFF?style=for-the-badge&logo=vite&logoColor=white)](https://vitejs.dev/)
[![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)

A premium, modern web dashboard for analyzing YouTube channel content. It provides deep insights into curated playlists and podcasts, featuring real-time streaming calculations and a stunning glassmorphism interface.

![Project Preview](image.png)

## ✨ Key Features

- **🚀 Real-Time Streaming**: Watch results "pop in" live as the backend processes each playlist.
- **🔍 Deep Content Discovery**: Automatically scans and uncovers curated playlists, "Created Playlists" sections, and Podcasts.
- **⚡ Speed Analysis**: Instant watch-time calculations for multiple playback speeds (1.25x, 1.5x, 1.75x, 2.0x).
- **💎 Premium Aesthetics**: Modern dark-mode UI with glassmorphism, accent glows, and smooth micro-animations.
- **📊 Channel Summary**: Comprehensive overview of total watch time and video counts across all discovered content.

## 🛠️ Tech Stack

- **Frontend**: React 19, Vite, Framer Motion (animations), Lucide React (icons).
- **Backend**: Flask, Flask-CORS, `yt-dlp` (YouTube data extraction).
- **Styling**: Vanilla CSS with a custom design system and modern typography (Inter, Outfit).

## 🚀 Getting Started

### Prerequisites
- Python 3.7+
- Node.js (v18+)

### Installation

1. **Clone the repository**:
   ```bash
   git clone <your-repo-url>
   ```

2. **Run the Automated Startup Script**:
   On Windows, simply run the included batch file to start both the backend and frontend simultaneously:
   ```bash
   .\run_app.bat
   ```

### Manual Setup (Optional)

**Backend**:
```bash
python -m venv venv
.\venv\Scripts\activate
pip install -r requirements.txt
python server.py
```

**Frontend**:
```bash
cd frontend
npm install
npm run dev
```

## 📝 License

This project is licensed under the MIT License. Built with ❤️ for the YouTube learning community.
