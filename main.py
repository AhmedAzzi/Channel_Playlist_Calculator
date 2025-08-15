import yt_dlp
import statistics

channel_url = "https://www.youtube.com/@HeshamAsem/playlists"
output_file = "playlists_info.txt"

def format_time(seconds):
    seconds = int(seconds)
    h, rem = divmod(seconds, 3600)
    m, s = divmod(rem, 60)
    return f"{h} hours, {m} minutes, {s} seconds"

def get_channel_playlists(channel_url):
    ydl_opts = {
        'quiet': True,
        'extract_flat': True,
        'skip_download': True,
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(channel_url, download=False)
    return [e for e in info.get('entries', []) if e.get('_type') == 'url']

def get_playlist_info_fast(url):
    ydl_opts = {
        'quiet': True,
        'extract_flat': True,
        'skip_download': True,
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)
    videos = [v for v in info.get('entries', []) if v.get('duration')]
    durations = [v['duration'] for v in videos]
    num_unavailable = len(info['entries']) - len(videos)
    total_seconds = sum(durations)
    avg_seconds = statistics.mean(durations) if durations else 0
    speeds = { sp: total_seconds / sp for sp in [1.25, 1.5, 1.75, 2.0] }
    return {
        "title": info.get('title'),
        "id": info.get('id'),
        "creator": info.get('uploader'),
        "num_videos": len(info['entries']),
        "num_unavailable": num_unavailable,
        "avg_length": avg_seconds,
        "total_length": total_seconds,
        "speeds": speeds
    }

def main():
    playlists = get_channel_playlists(channel_url)
    print(f"Total playlists found: {len(playlists)}\n")

    with open(output_file, "w", encoding="utf-8") as f:
        f.write(f"Total playlists found: {len(playlists)}\n\n")
        for idx, pl in enumerate(playlists, 1):
            info = get_playlist_info_fast(pl['url'])
            f.write(f"Playlist {idx}: {info['title']}\n")
            f.write(f"ID: {info['id']}\n")
            f.write(f"Creator: {info['creator']}\n")
            f.write(f"Video count: {info['num_videos']} (from 1 to {info['num_videos']}) ({info['num_unavailable']} unavailable)\n")
            f.write(f"Average video length: {format_time(info['avg_length'])}\n")
            f.write(f"Total length: {format_time(info['total_length'])}\n")
            for spd, secs in info['speeds'].items():
                f.write(f"At {spd}x: {format_time(secs)}\n")
            f.write("\n")

    print(f"✅ Data saved to {output_file}")

if __name__ == "__main__":
    main()
