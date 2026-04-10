import yt_dlp
import json
import statistics
from flask import Flask, request, jsonify, Response
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

def format_time(seconds):
    seconds = int(seconds)
    h, rem = divmod(seconds, 3600)
    m, s = divmod(rem, 60)
    return f"{h}h {m}m {s}s"

def flatten_entries(entries):
    """Recursively flatten entries from sections/folders."""
    flat = []
    for e in entries:
        if not e: continue
        # Extract direct playlists or urls pointing to playlists
        if e.get('_type') in ('url', 'playlist'):
            flat.append(e)
        # Recurse into folders or sections (found in some YouTube channel layouts)
        elif e.get('entries'):
            flat.extend(flatten_entries(e['entries']))
    return flat

def get_channel_playlists(url):
    ydl_opts = {
        'quiet': True,
        'extract_flat': True,
        'skip_download': True,
        'socket_timeout': 60,
        'no_warnings': True,
        'nocheckcertificate': True,
        'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
    }
    
    # Try multiple common tab URLs to find all content
    base_url = url.rstrip('/')
    urls_to_try = [base_url]
    if '/@' in base_url or '/channel/' in base_url or '/c/' in base_url:
        if not base_url.endswith('/playlists'):
            urls_to_try.append(f"{base_url}/playlists")
            urls_to_try.append(f"{base_url}/playlists?view=1")
        if not base_url.endswith('/podcasts'):
            urls_to_try.append(f"{base_url}/podcasts")

    all_found = []
    seen_ids = set()

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        for target_url in urls_to_try:
            try:
                info = ydl.extract_info(target_url, download=False)
                if not info: continue
                
                # If the URL itself is a playlist, return it
                if info.get('_type') == 'playlist' and 'entries' in info and not info.get('webpage_url_basename') == 'playlists':
                    # Check if it contains videos directly
                    first_entry = info['entries'][0] if info['entries'] else {}
                    if first_entry.get('_type') not in ('url', 'playlist'):
                         # It's a direct playlist of videos
                         if info.get('id') not in seen_ids:
                             all_found.append({'url': info.get('webpage_url') or target_url, 'title': info.get('title'), 'id': info.get('id')})
                             seen_ids.add(info.get('id'))
                         continue

                # Otherwise, flatten found entries
                found_entries = flatten_entries(info.get('entries', []))
                for e in found_entries:
                    pid = e.get('id')
                    title = e.get('title', '')
                    
                    # Filter out automatic system "playlists" (Videos, Live, Shorts)
                    # These often have titles ending in " - Videos" or IDs starting with "UU"
                    is_system_tab = any(suffix in title for suffix in [' - Videos', ' - Live', ' - Shorts']) or \
                                   (pid and pid.startswith('UU'))
                    
                    if pid and pid not in seen_ids and not is_system_tab:
                        all_found.append(e)
                        seen_ids.add(pid)
            except Exception as e:
                print(f"Warning: Could not extract from {target_url}: {e}")
                continue

    return all_found

def get_playlist_info_fast(url):
    ydl_opts = {
        'quiet': True,
        'extract_flat': True,
        'skip_download': True,
        'socket_timeout': 60,
        'no_warnings': True,
        'nocheckcertificate': True,
        'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
    }
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
        
        entries = info.get('entries', [])
        # Some flat extractions might not have duration, but if we are here we want the details
        videos = [v for v in entries if v.get('duration') or v.get('_type') != 'url']
        
        # If videos don't have duration in flat mode, we might need a more detailed extraction
        # but for speed we hope for the best or rely on the playlist metadata
        
        durations = [v.get('duration', 0) for v in videos if v.get('duration')]
        num_unavailable = len(entries) - len(videos)
        total_seconds = sum(durations)
        avg_seconds = statistics.mean(durations) if durations else 0
        
        speeds = { str(sp): total_seconds / sp for sp in [1, 1.25, 1.5, 1.75, 2.0] }
        
        return {
            "title": info.get('title'),
            "id": info.get('id'),
            "creator": info.get('uploader') or info.get('channel'),
            "num_videos": len(entries),
            "num_unavailable": num_unavailable,
            "avg_length": avg_seconds,
            "total_length": total_seconds,
            "avg_length_formatted": format_time(avg_seconds),
            "total_length_formatted": format_time(total_seconds),
            "speeds": {k: format_time(v) for k, v in speeds.items()},
            "url": url
        }
    except Exception as e:
        print(f"Error processing {url}: {e}")
        return None

@app.route('/')
def home():
    return """
    <h1>YouTube Playlist Calc API</h1>
    <p>The API is running correctly.</p>
    <p>To view the website, please visit the frontend development server (usually at <a href='http://localhost:5173'>http://localhost:5173</a>).</p>
    """

@app.route('/api/analyze', methods=['POST'])
def analyze():
    data = request.json
    channel_url = data.get('url')
    if not channel_url:
        return jsonify({"error": "No URL provided"}), 400
    
    def generate():
        try:
            playlists = get_channel_playlists(channel_url)
            total = len(playlists)
            
            # Extract channel metadata from the first successful extraction
            channel_metadata = {}
            with yt_dlp.YoutubeDL({
                'quiet': True, 
                'extract_flat': True, 
                'skip_download': True,
                'no_warnings': True,
                'socket_timeout': 60,
                'nocheckcertificate': True,
                'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
            }) as ydl:
                try:
                    c_info = ydl.extract_info(channel_url, download=False)
                    thumb_url = ""
                    if c_info.get('thumbnails'):
                        thumb_url = c_info['thumbnails'][-1]['url']
                    elif c_info.get('thumbnail'):
                        thumb_url = c_info['thumbnail']
                        
                    channel_metadata = {
                        "title": c_info.get('uploader') or c_info.get('title'),
                        "thumbnail": thumb_url,
                        "url": c_info.get('webpage_url') or channel_url
                    }
                except:
                    pass

            # Initial event with total count and channel info
            yield f"data: {json.dumps({'type': 'init', 'total': total, 'channel': channel_metadata})}\n\n"
            
            processed_results = []
            for i, pl in enumerate(playlists):
                info = get_playlist_info_fast(pl.get('url') or pl.get('webpage_url'))
                if info:
                    processed_results.append(info)
                    yield f"data: {json.dumps({'type': 'playlist', 'data': info, 'current': i + 1})}\n\n"
                else:
                    yield f"data: {json.dumps({'type': 'skip', 'current': i + 1})}\n\n"
            
            # Calculate final summary
            total_videos = sum(r['num_videos'] for r in processed_results)
            total_duration = sum(r['total_length'] for r in processed_results)
            
            summary = {
                "total_playlists": len(processed_results),
                "total_videos": total_videos,
                "total_duration_seconds": total_duration,
                "total_duration_formatted": format_time(total_duration)
            }
            
            yield f"data: {json.dumps({'type': 'final', 'summary': summary})}\n\n"
            
        except Exception as e:
            yield f"data: {json.dumps({'type': 'error', 'message': str(e)})}\n\n"

    return Response(generate(), mimetype='text/event-stream')

if __name__ == '__main__':
    app.run(debug=True, port=5000)
