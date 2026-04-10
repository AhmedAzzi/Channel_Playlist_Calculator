import React, { useState } from 'react';
import axios from 'axios';
import { Search, Youtube, Clock, Video, List, Play, Award, Loader2, ExternalLink } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';

const API_URL = 'http://localhost:5000/api/analyze';

function App() {
  const [url, setUrl] = useState('');
  const [loading, setLoading] = useState(false);
  const [data, setData] = useState({ playlists: [], summary: null, channel: null });
  const [progress, setProgress] = useState({ current: 0, total: 0 });
  const [error, setError] = useState(null);
  const [isFinished, setIsFinished] = useState(false);

  const handleAnalyze = async (e) => {
    e.preventDefault();
    if (!url) return;

    setLoading(true);
    setError(null);
    setData({ playlists: [], summary: null, channel: null });
    setProgress({ current: 0, total: 0 });
    setIsFinished(false);

    try {
      const response = await fetch(API_URL, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ url })
      });

      if (!response.ok) throw new Error('Failed to start analysis');

      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      let buffer = '';

      while (true) {
        const { value, done } = await reader.read();
        if (done) break;

        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split('\n');
        buffer = lines.pop(); // Keep partial line in buffer

        for (const line of lines) {
          if (line.startsWith('data: ')) {
            const jsonStr = line.replace('data: ', '');
            try {
              const event = JSON.parse(jsonStr);
              
              if (event.type === 'init') {
                setProgress(prev => ({ ...prev, total: event.total }));
                setData(prev => ({ ...prev, channel: event.channel }));
              } else if (event.type === 'playlist') {
                setData(prev => ({
                  ...prev,
                  playlists: [...prev.playlists, event.data]
                }));
                setProgress(prev => ({ ...prev, current: event.current }));
              } else if (event.type === 'skip') {
                setProgress(prev => ({ ...prev, current: event.current }));
              } else if (event.type === 'final') {
                setData(prev => ({ ...prev, summary: event.summary }));
                setIsFinished(true);
                setLoading(false);
              } else if (event.type === 'error') {
                throw new Error(event.message);
              }
            } catch (e) {
              console.error('Error parsing chunk:', e);
            }
          }
        }
      }
    } catch (err) {
      setError(err.message || 'Failed to analyze channel. Please check the URL.');
      setLoading(false);
    }
  };

  return (
    <div className="app-container">
      <div className="ambient-glow-1"></div>
      <div className="ambient-glow-2"></div>

      <header>
        <motion.div 
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
          className="header-content"
        >
          <div className="title-row">
            <Youtube className="text-red-500" size={42} strokeWidth={2} style={{ color: '#ff4d4d' }} />
            <h1>Playlist Calc</h1>
          </div>
          <p>Supercharge your YouTube learning with detailed playlist analytics.</p>
        </motion.div>
      </header>

      <div className="search-container">
        <form onSubmit={handleAnalyze}>
          <div className="input-wrapper">
            <input 
              type="text" 
              placeholder="Enter YouTube Channel URL (e.g., https://www.youtube.com/@channel)"
              value={url}
              onChange={(e) => setUrl(e.target.value)}
              disabled={loading}
            />
            <button type="submit" className="primary" disabled={loading || !url}>
              {loading ? <Loader2 className="spinner" size={20} /> : <Search size={20} />}
              {loading ? 'Analyzing...' : 'Analyze'}
            </button>
          </div>
        </form>
        {error && (
          <motion.div 
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="mt-4 text-center text-red-400 font-medium"
            style={{ color: '#ff4d4d', marginTop: '1rem', textAlign: 'center' }}
          >
            {error}
          </motion.div>
        )}
      </div>

      <AnimatePresence>
        {isFinished && data.summary && (
          <motion.div
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            className="awesome-message"
          >
            <Award size={32} />
            <div>
              <h3>Analysis Complete!</h3>
              <p>Processed {data.summary.total_playlists} curated playlists and podcasts. Happy learning!</p>
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      <AnimatePresence mode="wait">
        {(data.playlists.length > 0 || data.summary || data.channel) && (
          <motion.div
            initial={{ opacity: 0, y: 40 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: 40 }}
            transition={{ duration: 0.5 }}
          >
            {data.channel && (
              <div className="channel-header">
                <div className="channel-avatar-wrapper">
                  <img src={data.channel.thumbnail} alt={data.channel.title} className="channel-avatar" />
                </div>
                <div className="channel-info">
                  <a href={data.channel.url} target="_blank" rel="noopener noreferrer" className="channel-name-link">
                    <h2>{data.channel.title}</h2>
                    <ExternalLink size={16} />
                  </a>
                  <p>Channel Insight View</p>
                </div>
              </div>
            )}

            {data.summary && (
              <div className="summary-grid">
                <div className="stat-card">
                  <h3>Total Playlists</h3>
                  <div className="value">{data.summary.total_playlists}</div>
                  <List className="text-secondary opacity-20" style={{ position: 'absolute', right: '1.5rem', bottom: '1.5rem' }} size={40} />
                </div>
                <div className="stat-card">
                  <h3>Total Videos</h3>
                  <div className="value">{data.summary.total_videos}</div>
                  <Video className="text-secondary opacity-20" style={{ position: 'absolute', right: '1.5rem', bottom: '1.5rem' }} size={40} />
                </div>
                <div className="stat-card">
                  <h3>Total Watch Time</h3>
                  <div className="value">{data.summary.total_duration_formatted}</div>
                  <Clock className="text-secondary opacity-20" style={{ position: 'absolute', right: '1.5rem', bottom: '1.5rem' }} size={40} />
                </div>
              </div>
            )}

            <div className="playlist-grid">
              {data.playlists.map((pl, idx) => (
                <motion.div 
                  key={pl.id || idx}
                  className="playlist-card"
                  initial={{ opacity: 0, scale: 0.95 }}
                  animate={{ opacity: 1, scale: 1 }}
                  transition={{ delay: idx * 0.05 }}
                >
                  <div className="card-content">
                    <div className="card-header">
                      <h2>{pl.title}</h2>
                      <div className="creator">{pl.creator}</div>
                    </div>

                    <div className="card-stats">
                      <div className="mini-stat">
                        <label>Videos</label>
                        <div className="val">{pl.num_videos}</div>
                      </div>
                      <div className="mini-stat">
                        <label>Avg Length</label>
                        <div className="val">{pl.avg_length_formatted}</div>
                      </div>
                    </div>

                    <div className="speed-table">
                      {Object.entries(pl.speeds).map(([speed, time]) => (
                        <div key={speed} className="speed-row">
                          <span>{speed}x Speed</span>
                          <span>{time}</span>
                        </div>
                      ))}
                    </div>

                    <a 
                      href={pl.url} 
                      target="_blank" 
                      rel="noopener noreferrer"
                      style={{ 
                        marginTop: '1.5rem', 
                        display: 'flex', 
                        alignItems: 'center', 
                        gap: '0.5rem', 
                        color: 'var(--text-secondary)',
                        textDecoration: 'none',
                        fontSize: '0.85rem'
                      }}
                      onMouseEnter={(e) => e.target.style.color = 'var(--text-primary)'}
                      onMouseLeave={(e) => e.target.style.color = 'var(--text-secondary)'}
                    >
                      View Playlist <ExternalLink size={14} />
                    </a>
                  </div>
                </motion.div>
              ))}
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {loading && (
        <div className="loading-container">
          <div className="progress-bar">
            <motion.div 
              className="progress-fill"
              initial={{ width: 0 }}
              animate={{ width: `${progress.total > 0 ? (progress.current / progress.total) * 100 : 5}%` }}
            />
          </div>
          <div className="loading-text">
            {progress.total > 0 
              ? `Processing playlist ${progress.current} of ${progress.total}...` 
              : 'Finding channel playlists and podcasts...'}
          </div>
        </div>
      )}

      <footer style={{ marginTop: '8rem', textAlign: 'center', padding: '4rem 0', borderTop: '1px solid var(--border)', color: 'var(--text-secondary)', fontSize: '0.9rem' }}>
        Built with Premium Design & React + Flask
      </footer>
    </div>
  );
}

export default App;
