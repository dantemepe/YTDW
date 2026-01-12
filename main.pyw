import os
import threading
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import yt_dlp

APP_DIR = os.getcwd()
FFMPEG_DIR = os.path.join(APP_DIR, "ffmpeg_bin")
FFMPEG_EXE = os.path.join(FFMPEG_DIR, "ffmpeg.exe")

def ffmpeg_exists():
    return os.path.isfile(FFMPEG_EXE)

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

def get_format(q, container):
    base = {
        "Best available": "",
        "1080p": "[height<=1080]",
        "720p": "[height<=720]",
        "480p": "[height<=480]"
    }[q]

    if container == "webm":
        return f"bv*{base}[ext=webm]+ba[ext=webm]/b{base}[ext=webm]"

    return f"bv*{base}[ext=mp4]+ba[ext=m4a]/b{base}[ext=mp4]"

def download_worker():
    if not ffmpeg_exists():
        set_status("FFmpeg not found")
        messagebox.showerror(
            "FFmpeg Missing",
            "ffmpeg.exe was not found.\n\n"
            "Place ffmpeg.exe inside the ffmpeg_bin folder."
        )
        return

    try:
        container = container_box.get().lower()

        opts = {
            "outtmpl": os.path.join(out_dir.get(), "%(title)s.%(ext)s"),
            "format": get_format(quality_box.get(), container),
            "merge_output_format": container,
            "ffmpeg_location": FFMPEG_EXE,
            "progress_hooks": [progress_hook],
            "quiet": False,
            "no_color": True
        }

        with yt_dlp.YoutubeDL(opts) as ydl:
            ydl.download([url_entry.get()])

        set_progress(100)
        set_status("Done")
        print("\nDone")

    except Exception as e:
        set_status(str(e))
        print(e)

def start_download():
    if not url_entry.get():
        return
    set_progress(0)
    threading.Thread(target=download_worker, daemon=True).start()

def browse():
    path = filedialog.askdirectory()
    if path:
        out_dir.set(path)

def set_progress(v):
    root.after(0, lambda: (progress_bar.config(value=v), root.update_idletasks()))

def set_status(t):
    root.after(0, lambda: status_label.config(text=t))

root = tk.Tk()
root.title("YouTube Downloader")
root.geometry("520x420")
root.resizable(False, False)

main = ttk.Frame(root, padding=20)
main.pack(expand=True)

ttk.Label(main, text="YouTube Downloader", font=("Segoe UI", 13, "bold")).pack(pady=(0, 14))

ttk.Label(main, text="YouTube URL").pack(anchor="center")
url_entry = ttk.Entry(main, width=60, justify="center")
url_entry.pack(pady=(2, 12))

ttk.Label(main, text="Quality").pack(anchor="center")
quality_box = ttk.Combobox(
    main,
    values=["Best available", "1080p", "720p", "480p"],
    state="readonly",
    width=57,
    justify="center"
)
quality_box.set("Best available")
quality_box.pack(pady=(2, 12))

ttk.Label(main, text="Container").pack(anchor="center")
container_box = ttk.Combobox(
    main,
    values=["MP4", "WEBM"],
    state="readonly",
    width=57,
    justify="center"
)
container_box.set("MP4")
container_box.pack(pady=(2, 12))

ttk.Label(main, text="Output Directory").pack(anchor="center")

dir_frame = ttk.Frame(main)
dir_frame.pack(pady=(2, 12))

out_dir = tk.StringVar(value=os.path.join(os.path.expanduser("~"), "Downloads"))
ttk.Entry(dir_frame, textvariable=out_dir, width=46, justify="center").pack(side="left", padx=(0, 6))
ttk.Button(dir_frame, text="Browse", command=browse).pack(side="left")

progress_bar = ttk.Progressbar(main, length=480, mode="determinate", maximum=100)
progress_bar.pack(pady=(6, 16))

ttk.Button(main, text="Download", width=20, command=start_download).pack()

status_label = ttk.Label(main)
status_label.pack(pady=(8, 0))

root.mainloop()
