import yt_dlp
import ffmpeg
import os


def readable_size(size_bytes):
    if not size_bytes:
        return "Unknown"
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if size_bytes < 1024:
            return f"{size_bytes:.2f} {unit}"
        size_bytes /= 1024
    return f"{size_bytes:.2f} PB"


def is_reasonable(filesize, height):
    if not filesize or not height:
        return False

    expected_min = {
        144: 0.5, 240: 1, 360: 2, 480: 3,
        720: 5, 1080: 8, 1440: 12, 2160: 20
    }

    resolution_keys = sorted(expected_min.keys())
    for res in reversed(resolution_keys):
        if height >= res:
            return filesize >= expected_min[res] * 1024 * 1024
    return filesize >= 2 * 1024 * 1024


def sort_and_print_formats(formats):
    allowed_video_audio = []
    blocked_video_audio = []
    video_only_all = {}
    audio_only_all = []

    for f in formats:
        fmt_id = f.get("format_id")
        vcodec = f.get("vcodec")
        acodec = f.get("acodec")
        width = f.get("width") or 0
        height = f.get("height") or 0
        filesize = f.get("filesize") or f.get("filesize_approx")
        ext = f.get("ext", "unknown")
        format_note = f.get("format_note", "").lower()

        if not fmt_id or not filesize:
            continue

        info = {
            "id": fmt_id,
            "ext": ext,
            "res": f"{width}x{height}" if width and height else format_note,
            "height": height,
            "width": width,
            "filesize": filesize,
            "size_str": readable_size(filesize),
            "format_note": format_note
        }

        if vcodec != "none" and acodec != "none":
            if is_reasonable(filesize, height):
                allowed_video_audio.append(info)
            else:
                blocked_video_audio.append(info)
        elif vcodec != "none":
            resolution_key = f"{width}x{height}"
            prev = video_only_all.get(resolution_key)
            if not prev or filesize > prev["filesize"]:
                video_only_all[resolution_key] = info
        elif acodec != "none":
            if "low" in format_note or "tiny" in format_note:
                continue
            audio_only_all.append(info)

    allowed_video_audio.sort(key=lambda x: x["height"], reverse=True)
    blocked_video_audio.sort(key=lambda x: x["height"], reverse=True)
    video_only = list(video_only_all.values())
    video_only.sort(key=lambda x: x["height"], reverse=True)
    audio_only_all.sort(key=lambda x: x["filesize"], reverse=True)

    def printer(title, lst, blocked=False):
        status = " (Not downloadable)" if blocked else ""
        print(f"\n🔹 {title}{status} ({len(lst)} formats):")
        for f in lst:
            print(f"[{f['id']}] {f['res']} - {f['ext']} - {f['size_str']}")

    printer("Video + Audio (Allowed)", allowed_video_audio)
    printer("Video + Audio (Blocked)", blocked_video_audio, blocked=True)
    printer("Video Only", video_only)
    printer("Audio Only", audio_only_all)

    return [f["id"] for f in allowed_video_audio + video_only + audio_only_all]


def downloader(link):
    try:
        with yt_dlp.YoutubeDL({'cookiefile': 'youtube_cookies.txt'}) as ydl_info:
            vid_info = ydl_info.extract_info(link, download=False)
    except Exception as e:
        print("❌ Error during info extraction:", e)
        return

    fvalid_ids = sort_and_print_formats(vid_info.get("formats", []))

    choice = input("\nEnter format ID(s) (comma-separated): ").strip()
    selected_ids = [x.strip() for x in choice.split(',') if x.strip()]
    invalid_ids = [x for x in selected_ids if x not in fvalid_ids]

    if invalid_ids:
        print(f"❌ Invalid format IDs: {', '.join(invalid_ids)}")
        return

    for fmt in selected_ids:
        print(f"\n⬇ Downloading format [{fmt}]...")
        ydl_opts = {
            'format': fmt,
            'outtmpl': f'%(title)s_{fmt}.%(ext)s',
            'merge_output_format': 'mp4',
            'cookiefile': 'youtube_cookies.txt'
        }
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([link])
        except Exception as e:
            print(f"❌ Error downloading format {fmt}:", e)


def download_yt_short(link):
    try:
        ydl_opts = {
            'format': 'bestvideo+bestaudio/best',
            'outtmpl': '%(title)s_short.%(ext)s',
            'merge_output_format': 'mp4',
            'noplaylist': True,
            'cookiefile': 'youtube_cookies.txt'
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([link])
        print("✅ Short downloaded successfully.")
    except Exception as e:
        print("❌ Failed to download Short:", e)


def download_instagram_reel(link):
    try:
        ydl_opts = {
            'format': 'best',
            'outtmpl': '%(title)s_reel.%(ext)s',
            'merge_output_format': 'mp4',
            'cookiefile': 'instagram_cookies.txt'
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([link])
        print("✅ Reel downloaded successfully.")
    except Exception as e:
        print("❌ Failed to download Reel:", e)


def merge_video_audio():
    video_file = input("Enter video file name (without .mp4): ").strip()
    if not video_file.lower().endswith('.mp4'):
        video_file += '.mp4'

    audio_file = input("Enter audio file name (without .mp3): ").strip()
    if not audio_file.lower().endswith('.mp3'):
        audio_file += '.mp3'

    output_file = input("Enter name for merged file (without extension): ").strip()
    if not output_file.lower().endswith('.mp4'):
        output_file += '.mp4'

    try:
        ffmpeg.input(video_file).output(
            audio_file, output_file, vcodec='copy', acodec='aac', strict='experimental'
        ).run(overwrite_output=True)
        print(f"✅ Merged file saved as: {output_file}")
    except Exception as e:
        print(f"❌ Error during merging: {e}")


if __name__ == "__main__":
    while True:
        print("\nSelect an operation:")
        print("1. Download video/audio from YouTube")
        print("2. Download YouTube Short")
        print("3. Download Instagram Reel")
        print("4. Merge video and audio files")
        print("5. Exit")

        choice = input("Enter your choice (1-5): ").strip()

        if choice == '1':
            link = input("🔗 Enter YouTube URL: ").strip()
            if link:
                confirm = input("✅ Is this the correct link? (y/n): ").lower()
                if confirm == 'y':
                    downloader(link)

        elif choice == '2':
            link = input("🔗 Enter YouTube Shorts URL: ").strip()
            if link:
                download_yt_short(link)

        elif choice == '3':
            link = input("🔗 Enter Instagram Reel URL: ").strip()
            if link:
                download_instagram_reel(link)

        elif choice == '4':
            merge_video_audio()

        elif choice == '5':
            print("👋 Exiting...")
            break

        else:
            print("❌ Invalid choice. Please select between 1 to 5.")
