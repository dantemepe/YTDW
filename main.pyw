import os
import sys
import threading
import tkinter as tk
from tkinter import ttk, filedialog
import yt_dlp

def app_path():
    if getattr(sys, "frozen", False):
        return sys._MEIPASS
    return os.path.dirname(os.path.abspath(__file__))

APP_DIR = app_path()
FFMPEG_DIR = os.path.join(APP_DIR, "ffmpeg_bin")
FFMPEG_EXE = os.path.join(FFMPEG_DIR, "ffmpeg.exe")

def ffmpeg_exists():
    return os.path.isfile(FFMPEG_EXE)

def set_status(text):
    root.after(0, lambda: status_label.config(text=text))

def set_progress(value):
    root.after(0, lambda: progress_bar.config(value=value))

def progress_hook(d):
    if d["status"] == "downloading":
        total = d.get("total_bytes") or d.get("total_bytes_estimate")
        downloaded = d.get("downloaded_bytes", 0)
        if total:
            percent = downloaded * 100 / total
            set_progress(percent)
            set_status(f"Downloading {percent:.1f}%")
            print(f"\rDownloading {percent:.1f}%", end="", flush=True)
    elif d["status"] == "finished":
        set_status("Processing")
        print("\nProcessing")

def get_video_format(quality, container):
    q = {
        "Best available": "",
        "1080p": "[height<=1080]",
        "720p": "[height<=720]",
        "480p": "[height<=480]",
    }[quality]

    if container == "webm":
        return f"bv*{q}[ext=webm]+ba[ext=webm]/b{q}[ext=webm]"
    return f"bv*{q}[ext=mp4]+ba[ext=m4a]/b{q}[ext=mp4]"

def update_quality_lock(event=None):
    if container_box.get() == "MP3":
        quality_box.set("Best available")
        quality_box.config(state="disabled")
    else:
        quality_box.config(state="readonly")

def download_worker():
    if not ffmpeg_exists():
        set_status("ffmpeg.exe not found")
        print("ffmpeg.exe missing")
        return

    url = url_entry.get().strip()
    if not url:
        set_status("No URL")
        return

    container = container_box.get().lower()
    output = out_dir.get()

    set_progress(0)

    try:
        if container == "mp3":
            opts = {
                "outtmpl": os.path.join(output, "%(title)s.%(ext)s"),
                "format": "bestaudio/best",
                "postprocessors": [
                    {
                        "key": "FFmpegExtractAudio",
                        "preferredcodec": "mp3",
                        "preferredquality": "192",
                    }
                ],
                "ffmpeg_location": FFMPEG_EXE,
                "progress_hooks": [progress_hook],
                "keepvideo": False,
                "quiet": False,
                "no_color": True,
            }
        else:
            opts = {
                "outtmpl": os.path.join(output, "%(title)s.%(ext)s"),
                "format": get_video_format(quality_box.get(), container),
                "merge_output_format": container,
                "ffmpeg_location": FFMPEG_EXE,
                "progress_hooks": [progress_hook],
                "quiet": False,
                "no_color": True,
            }

        with yt_dlp.YoutubeDL(opts) as ydl:
            ydl.download([url])

        set_progress(100)
        set_status("Done")
        print("\nDone")

    except Exception as e:
        set_status(str(e))
        print(e)

def start_download():
    threading.Thread(target=download_worker, daemon=True).start()

def browse():
    path = filedialog.askdirectory()
    if path:
        out_dir.set(path)

root = tk.Tk()
root.title("YouTube Downloader")
root.geometry("520x460")
root.resizable(False, False)

main = ttk.Frame(root, padding=20)
main.pack(expand=True)

ttk.Label(main, text="YouTube Downloader", font=("Segoe UI", 13, "bold")).pack(pady=(0, 14))

ttk.Label(main, text="YouTube URL").pack()
url_entry = ttk.Entry(main, width=60, justify="center")
url_entry.pack(pady=(4, 12))

ttk.Label(main, text="Quality").pack()
quality_box = ttk.Combobox(
    main,
    values=["Best available", "1080p", "720p", "480p"],
    state="readonly",
    width=57,
    justify="center"
)
quality_box.set("Best available")
quality_box.pack(pady=(4, 12))

ttk.Label(main, text="Format").pack()
container_box = ttk.Combobox(
    main,
    values=["MP4", "WEBM", "MP3"],
    state="readonly",
    width=57,
    justify="center"
)
container_box.set("MP4")
container_box.pack(pady=(4, 12))
container_box.bind("<<ComboboxSelected>>", update_quality_lock)

ttk.Label(main, text="Output Folder").pack()

dir_frame = ttk.Frame(main)
dir_frame.pack(pady=(4, 12))

out_dir = tk.StringVar(value=os.path.join(os.path.expanduser("~"), "Downloads"))
ttk.Entry(dir_frame, textvariable=out_dir, width=46, justify="center").pack(side="left", padx=(0, 6))
ttk.Button(dir_frame, text="Browse", command=browse).pack(side="left")

progress_bar = ttk.Progressbar(main, length=480, maximum=100)
progress_bar.pack(pady=(6, 16))

ttk.Button(main, text="Download", width=20, command=start_download).pack()

status_label = ttk.Label(main, text="")
status_label.pack(pady=(10, 0))

root.mainloop()