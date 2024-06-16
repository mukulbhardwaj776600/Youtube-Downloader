import os
import re
import yt_dlp
import tkinter as tk
from tkinter import ttk, filedialog
from pytube import YouTube,Playlist
from threading import Thread


def update_progress_bar(d):
    if d['status'] == 'finished':
        print('Done downloading, now converting ...')
        progress_bar['value'] = 100
    if d['status'] == 'downloading':
        p = d['_percent_str']
        # Remove ANSI escape codes
        p = re.sub(r'\x1b\[.*?m', '', p)
        try:
            progress_value = float(p.replace('%',''))
            progress_bar['value'] = progress_value
        except ValueError as e:
            print(f"Error converting progress to float: {e}")



def start_download_thread(event):
    global download_thread
    download_thread = Thread(target=download_content)
    download_thread.start()

def browse_destination():
    destination_folder = filedialog.askdirectory()
    destination_entry.delete(0, tk.END)
    destination_entry.insert(0, destination_folder)

def download_content():
    youtube_url = url_entry.get()
    destination_path = destination_entry.get()
    resolution = resolution_var.get()
    print(destination_path)

    if 'playlist' in youtube_url:
        destination_path = playlist_creation(youtube_url, destination_path)
    

    if resolution=='Audio':
        quality='bestaudio/best'
        download(destination_path,youtube_url,quality)
    if resolution=='480p':
        quality='bestvideo[height<=480]+bestaudio/best[height<=480]'
        download(destination_path,youtube_url,quality)
    elif resolution=='720p':
        quality='bestvideo[height<=720]+bestaudio/best[height<=720]'
        download(destination_path,youtube_url,quality)
    elif resolution=='1080p':
        quality='bestvideo[height<=1080]+bestaudio/best[height<=1080]'
        download(destination_path,youtube_url,quality)
    elif resolution=='MAXIMUM':
        quality='bestvideo+bestaudio/best'
        download(destination_path,youtube_url,quality)


def playlist_creation(link,destination):
    p = Playlist(link)
    playlist_name = p.title

    # Determine a unique directory name
    unique_name = playlist_name
    unique_path = os.path.join(destination, unique_name)
    counter = 1
    while os.path.exists(unique_path):
        unique_name = f"{playlist_name} ({counter})"
        unique_path = os.path.join(destination, unique_name)
        counter += 1
    os.makedirs(unique_path)
    return unique_path


def get_video_title(url):
    ydl_opts = {
        'quiet': True,
        'no_warnings': True,
        'skip_download': True,
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)
        title = info.get('title', None)
        return title

def download(destination_path, address, quality):
    ydl_opts = {
        'format': quality,
        'merge_output_format': 'mp4',
        'addmetadata': True,
        'outtmpl': f'{destination_path}/%(title)s.%(ext)s',
        'progress_hooks': [update_progress_bar],
    }
    
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([address])


# Create main window
root = tk.Tk()
root.title("YouTube Downloader")

# Create labels and entry widgets for URL and destination address
url_label = tk.Label(root, text="URL:")
url_label.grid(row=0, column=0, padx=5, pady=5, sticky="w")
url_entry = tk.Entry(root, width=50)
url_entry.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
url_entry.insert(0,'')

destination_label = tk.Label(root, text="Destination:")
destination_label.grid(row=1, column=0, padx=5, pady=5, sticky="w")
destination_entry = tk.Entry(root, width=50)
destination_entry.grid(row=1, column=1, padx=5, pady=5, sticky="ew")
destination_entry.insert(0,"")
browse_button = ttk.Button(root, text="Browse", command=browse_destination)
browse_button.grid(row=1, column=2, padx=5, pady=5)

# Create labels and dropdown list for resolution
resolution_label = tk.Label(root, text="Resolution:")
resolution_label.grid(row=2, column=0, padx=5, pady=5, sticky="w")
resolution_var = tk.StringVar()
resolution_dropdown = ttk.Combobox(root, textvariable=resolution_var, values=["Audio","480p","720p", "1080p","MAXIMUM"])
resolution_dropdown.grid(row=2, column=1, padx=5, pady=5, sticky="ew")

resolution_dropdown.current(0)

# Create download button
download_button = ttk.Button(root, text="Download", command=lambda: start_download_thread(None))
download_button.grid(row=3, column=0, columnspan=3, padx=5, pady=5)

progress_bar = ttk.Progressbar(root, orient='horizontal', mode='determinate', length=280)
progress_bar['value'] = 0
progress_bar.grid(row=4, column=0, columnspan=3, padx=5, pady=5, sticky="ew")

root.mainloop()