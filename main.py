import os
import shutil
import time
import threading
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# ---------------------------------------------
# CONFIG: File categories
# ---------------------------------------------
FILE_TYPES = {
    "Images": [".jpg", ".png", ".jpeg", ".gif" ,".webp"],
    "Documents": [".pdf", ".docx", ".txt"],
    "Music": [".mp3", ".wav"],
    "Videos": [".mp4", ".mkv"],
    "Archives": [".zip", ".rar"],
    "Programs": [".exe", ".msi"],
    "Powerpoints": [".pptx"],
    "Applications": [".exe", ".apk"],
}

# ---------------------------------------------
# FUNCTION: Organize files
# ---------------------------------------------
def organize_files(folder_path, progress_bar, log_box):
    files = [f for f in os.listdir(folder_path) if os.path.isfile(os.path.join(folder_path, f))]
    total_files = len(files)
    moved = 0

    if total_files == 0:
        messagebox.showinfo("No Files", "No files to organize in this folder.")
        return

    progress_bar["maximum"] = total_files
    log_box.delete(1.0, tk.END)

    for filename in files:
        file_path = os.path.join(folder_path, filename)
        _, ext = os.path.splitext(filename)
        for folder_name, extensions in FILE_TYPES.items():
            if ext.lower() in extensions:
                target_folder = os.path.join(folder_path, folder_name)
                os.makedirs(target_folder, exist_ok=True)
                shutil.move(file_path, os.path.join(target_folder, filename))
                moved += 1
                log_box.insert(tk.END, f"Moved: {filename} → {folder_name}\n")
                log_box.see(tk.END)
                progress_bar["value"] = moved
                progress_bar.update()
                break

    messagebox.showinfo("Success", f"Organized {moved} files successfully!")

# ---------------------------------------------
# WATCHDOG: Auto-organize new files
# ---------------------------------------------
class WatchHandler(FileSystemEventHandler):
    def __init__(self, folder_path, progress_bar, log_box):
        super().__init__()
        self.folder_path = folder_path
        self.progress_bar = progress_bar
        self.log_box = log_box

    def on_created(self, event):
        if not event.is_directory:
            time.sleep(1)  # small delay to ensure file is fully saved
            organize_files(self.folder_path, self.progress_bar, self.log_box)

# ---------------------------------------------
# FUNCTION: Start watching the folder
# ---------------------------------------------
def start_watching(folder_path, progress_bar, log_box):
    event_handler = WatchHandler(folder_path, progress_bar, log_box)
    observer = Observer()
    observer.schedule(event_handler, folder_path, recursive=False)
    observer.start()
    messagebox.showinfo("Auto Mode", f"Watching '{folder_path}' for new files...")
    return observer

# ---------------------------------------------
# GUI LOGIC
# ---------------------------------------------
def select_folder():
    folder_selected = filedialog.askdirectory()
    if folder_selected:
        organize_files(folder_selected, progress_bar, log_box)
        # Start background watcher
        thread = threading.Thread(target=start_watching, args=(folder_selected, progress_bar, log_box))
        thread.daemon = True
        thread.start()
    else:
        messagebox.showwarning("Cancelled", "No folder was selected.")

# ---------------------------------------------
# GUI DESIGN
# ---------------------------------------------
root = tk.Tk()
root.title("🗂️ File Organizer Pro")
root.geometry("500x450")
root.resizable(False, False)

# Title label
title = tk.Label(root, text="File Organizer Pro", font=("Arial", 18, "bold"))
title.pack(pady=15)

# Select button
btn_select = tk.Button(
    root,
    text="Select Folder to Organize",
    command=select_folder,
    font=("Arial", 12),
    bg="#4CAF50",
    fg="white",
    width=30,
)
btn_select.pack(pady=10)

# Progress bar
progress_bar = ttk.Progressbar(root, orient="horizontal", length=400, mode="determinate")
progress_bar.pack(pady=10)

# Log box
log_label = tk.Label(root, text="Activity Log:", font=("Arial", 12, "bold"))
log_label.pack(anchor="w", padx=20)

log_box = tk.Text(root, height=10, width=55, wrap="word", bg="#f5f5f5")
log_box.pack(pady=5)

# Exit button
btn_exit = tk.Button(root, text="Exit", command=root.destroy, font=("Arial", 12), bg="#f44336", fg="white", width=10)
btn_exit.pack(pady=10)

root.mainloop()
