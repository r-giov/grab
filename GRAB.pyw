"""
GRAB - YouTube Beat Downloader
Matrix Edition // Built for TRG Sensei
"""

import tkinter as tk
from tkinter import filedialog
import threading
import subprocess
import json
import re
import os
import glob
import random

import librosa
import numpy as np

# ── Config ──────────────────────────────────────────────
DEFAULT_DIR = r"M:\Youtube Beats\March Beats"
ICON_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "grab.ico")

# ── Matrix Colors ───────────────────────────────────────
BG = "#000000"
BG2 = "#0a0a0a"
BG_PANEL = "#050505"
MATRIX_GREEN = "#00ff41"
MATRIX_DIM = "#0d6b1e"
MATRIX_BRIGHT = "#39ff14"
MATRIX_DARK = "#003b00"
RED = "#ff0040"
AMBER = "#ffb000"
CYAN = "#00e5ff"
BORDER_COLOR = "#003b00"

FONT = "Consolas"


class MatrixRain:
    def __init__(self, canvas, width, height):
        self.canvas = canvas
        self.width = width
        self.height = height
        self.columns = width // 14
        self.drops = [random.randint(-20, 0) for _ in range(self.columns)]
        self.chars = "01アイウエオカキクケコサシスセソタチツテトナニヌネノハヒフヘホマミムメモヤユヨラリルレロワヲン"
        self.running = True

    def animate(self):
        if not self.running:
            return
        self.canvas.delete("rain")
        for i, drop in enumerate(self.drops):
            if drop >= 0:
                x = i * 14
                y = drop * 16
                char = random.choice(self.chars)
                if y < self.height:
                    self.canvas.create_text(x, y, text=char, fill=MATRIX_GREEN,
                                           font=(FONT, 9), anchor="nw", tags="rain")
                    if y - 16 >= 0:
                        self.canvas.create_text(x, y - 16, text=random.choice(self.chars),
                                               fill=MATRIX_DIM, font=(FONT, 8),
                                               anchor="nw", tags="rain")
            self.drops[i] += 1
            if self.drops[i] * 16 > self.height + 100:
                self.drops[i] = random.randint(-15, -1)
        self.canvas.after(120, self.animate)


class GrabApp:
    def __init__(self, root):
        self.root = root
        self.root.title("[ GRAB ]")
        self.root.configure(bg=BG)
        self.root.resizable(False, False)

        # Set icon
        if os.path.exists(ICON_PATH):
            try:
                self.root.iconbitmap(ICON_PATH)
            except:
                pass

        self.save_dir = tk.StringVar(value=DEFAULT_DIR)
        self.is_downloading = False

        self._build_ui()
        self.root.after(100, self._auto_paste)

    def _auto_paste(self):
        try:
            clip = self.root.clipboard_get()
            if any(x in clip for x in ["youtube.com/watch", "youtu.be/", "youtube.com/shorts"]):
                self.url_entry.delete(0, tk.END)
                self.url_entry.insert(0, clip)
                self._log("[SYS] URL detected in clipboard - auto-pasted", "dim")
        except:
            pass

    def _panel(self, parent, **kwargs):
        outer = tk.Frame(parent, bg=BORDER_COLOR, padx=1, pady=1)
        inner = tk.Frame(outer, bg=BG_PANEL, **kwargs)
        inner.pack(fill="both", expand=True)
        return outer, inner

    def _build_ui(self):
        main = tk.Frame(self.root, bg=BG, padx=20, pady=10)
        main.pack(fill="both", expand=True)

        # ── Header ─────────────────────────────────
        header = tk.Frame(main, bg=BG, height=80)
        header.pack(fill="x", pady=(0, 10))
        header.pack_propagate(False)

        self.rain_canvas = tk.Canvas(header, bg=BG, highlightthickness=0,
                                     width=520, height=80)
        self.rain_canvas.pack(fill="both", expand=True)

        self.rain_canvas.create_text(260, 22, text="[ G R A B ]",
                                     font=(FONT, 26, "bold"), fill=MATRIX_GREEN)
        self.rain_canvas.create_text(260, 52, text="YOUTUBE BEAT DOWNLOADER // 320kbps MP3",
                                     font=(FONT, 9), fill=MATRIX_DIM)
        self.rain_canvas.create_text(260, 68, text="< TRG SENSEI EDITION >",
                                     font=(FONT, 8), fill=MATRIX_DARK)

        self.rain = MatrixRain(self.rain_canvas, 520, 80)
        self.rain.animate()

        # ── Save Location ──────────────────────────
        outer, loc = self._panel(main, padx=10, pady=8)
        outer.pack(fill="x", pady=(0, 10))

        loc_row = tk.Frame(loc, bg=BG_PANEL)
        loc_row.pack(fill="x")
        tk.Label(loc_row, text="> SAVE_DIR:", font=(FONT, 9, "bold"),
                 fg=MATRIX_GREEN, bg=BG_PANEL).pack(side="left")
        tk.Label(loc_row, textvariable=self.save_dir, font=(FONT, 9),
                 fg=CYAN, bg=BG_PANEL, anchor="w").pack(side="left", padx=(6, 0), fill="x", expand=True)
        tk.Button(loc_row, text="[ BROWSE ]", font=(FONT, 8, "bold"),
                  fg=MATRIX_GREEN, bg=BG, relief="flat", bd=0, cursor="hand2",
                  activebackground=MATRIX_DARK, activeforeground=MATRIX_BRIGHT,
                  command=self._browse).pack(side="right")

        # ── URL Input ──────────────────────────────
        outer, url_frame = self._panel(main, padx=10, pady=8)
        outer.pack(fill="x", pady=(0, 10))

        tk.Label(url_frame, text="> PASTE_URL (Enter to download):", font=(FONT, 9, "bold"),
                 fg=MATRIX_GREEN, bg=BG_PANEL).pack(anchor="w")

        self.url_entry = tk.Entry(url_frame, font=(FONT, 13),
                                  bg=BG, fg=MATRIX_BRIGHT, insertbackground=MATRIX_GREEN,
                                  relief="flat", bd=8, selectbackground=MATRIX_DARK,
                                  selectforeground=MATRIX_BRIGHT)
        self.url_entry.pack(fill="x", pady=(4, 0))
        self.url_entry.bind("<Return>", lambda e: self._start_download())

        # ── Download Button ────────────────────────
        self.dl_btn = tk.Button(main, text=">>> DOWNLOAD <<<", font=(FONT, 16, "bold"),
                                bg=MATRIX_DARK, fg=MATRIX_GREEN, relief="flat", bd=0,
                                pady=14, cursor="hand2",
                                activebackground=MATRIX_GREEN, activeforeground=BG,
                                command=self._start_download)
        self.dl_btn.pack(fill="x", pady=(0, 10))
        self.dl_btn.bind("<Enter>", lambda e: self.dl_btn.config(bg=MATRIX_GREEN, fg=BG) if not self.is_downloading else None)
        self.dl_btn.bind("<Leave>", lambda e: self.dl_btn.config(bg=MATRIX_DARK, fg=MATRIX_GREEN) if not self.is_downloading else None)

        # ── Terminal Log ───────────────────────────
        outer, log_frame = self._panel(main, padx=6, pady=6)
        outer.pack(fill="both", expand=True)

        self.log_text = tk.Text(log_frame, font=(FONT, 9),
                                bg=BG, fg=MATRIX_GREEN, relief="flat", bd=4,
                                height=10, state="disabled", wrap="word",
                                insertbackground=MATRIX_GREEN, selectbackground=MATRIX_DARK)
        self.log_text.pack(fill="both", expand=True)

        for name, color in [("green", MATRIX_GREEN), ("bright", MATRIX_BRIGHT),
                             ("dim", MATRIX_DIM), ("red", RED),
                             ("amber", AMBER), ("cyan", CYAN),
                             ("bpm", CYAN)]:
            self.log_text.tag_configure(name, foreground=color)
        self.log_text.tag_configure("bpm_big", foreground=CYAN, font=(FONT, 14, "bold"))

        self._log("[SYS] GRAB v3.0 initialized", "dim")
        self._log(f"[SYS] Output: {self.save_dir.get()}", "dim")
        self._log("[SYS] Paste a YouTube URL and hit Enter.", "dim")

    def _browse(self):
        folder = filedialog.askdirectory(initialdir=self.save_dir.get(),
                                         title="Select Download Folder")
        if folder:
            self.save_dir.set(folder)
            self._log(f"[SYS] Folder: {folder}", "cyan")

    def _log(self, msg, tag=None):
        self.log_text.config(state="normal")
        if tag:
            self.log_text.insert("end", msg + "\n", tag)
        else:
            self.log_text.insert("end", msg + "\n")
        self.log_text.see("end")
        self.log_text.config(state="disabled")

    def _clear_log(self):
        self.log_text.config(state="normal")
        self.log_text.delete("1.0", "end")
        self.log_text.config(state="disabled")

    def _start_download(self):
        url = self.url_entry.get().strip()
        if not url:
            self._log("[ERR] No URL entered", "red")
            return
        if not any(x in url for x in ["youtube.com", "youtu.be"]):
            self._log("[ERR] Invalid URL - YouTube only", "red")
            return
        if self.is_downloading:
            self._log("[WARN] Download in progress...", "amber")
            return

        self.is_downloading = True
        self.dl_btn.config(text=">>> DOWNLOADING... <<<", bg=BG, fg=AMBER, state="disabled")
        threading.Thread(target=self._download_thread, args=(url,), daemon=True).start()

    def _download_thread(self, url):
        try:
            self._clear_log()
            self._log("[SYS] Connecting...", "dim")

            flags = subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0

            # Fetch metadata
            cmd = ["yt-dlp", "--dump-json", "--no-download", url]
            result = subprocess.run(cmd, capture_output=True, text=True, creationflags=flags)

            if result.returncode != 0:
                self._log(f"[ERR] {result.stderr.strip()}", "red")
                self._reset_button()
                return

            info = json.loads(result.stdout)
            title = info.get("title", "Unknown")
            duration = info.get("duration", 0)

            self._log(f"[INFO] {title}", "bright")
            self._log(f"[INFO] Channel: {info.get('uploader', '?')}", "dim")
            self._log(f"[INFO] Duration: {duration // 60}:{duration % 60:02d}", "dim")

            # Clean the title for filename
            filename = title
            for junk in ["[FREE]", "(FREE)", "FREE", "[free]", "(free)",
                          "| Type Beat", "type beat", "Type Beat",
                          "(Official Audio)", "(Official Video)",
                          "[Official Audio]", "[Official Video]",
                          "(Prod.", "(prod.", "[Prod.", "[prod."]:
                filename = filename.replace(junk, "")
            filename = re.sub(r'[<>:"/\\|?*]', '', filename)
            filename = re.sub(r'\s+', ' ', filename).strip(" -_|")

            save_path = self.save_dir.get()
            os.makedirs(save_path, exist_ok=True)

            # First download with a temp name, we'll rename after BPM scan
            temp_name = filename
            output_template = os.path.join(save_path, temp_name + ".%(ext)s")

            self._log(f"\n[DL] Downloading 320kbps MP3...", "amber")

            # Download as 320kbps MP3
            cmd = [
                "yt-dlp", "-x",
                "--audio-format", "mp3",
                "--audio-quality", "320K",
                "--embed-thumbnail",
                "--add-metadata",
                "--no-playlist",
                "-o", output_template,
                url,
            ]
            result = subprocess.run(cmd, capture_output=True, text=True, creationflags=flags)

            if result.returncode != 0:
                self._log("[WARN] Retrying without thumbnail...", "amber")
                cmd = [
                    "yt-dlp", "-x",
                    "--audio-format", "mp3",
                    "--audio-quality", "320K",
                    "--add-metadata",
                    "--no-playlist",
                    "-o", output_template,
                    url,
                ]
                result = subprocess.run(cmd, capture_output=True, text=True, creationflags=flags)
                if result.returncode != 0:
                    self._log(f"[ERR] {result.stderr.strip()}", "red")
                    self._reset_button()
                    return

            self._log(f"[OK] Download complete", "green")

            # Find the downloaded file
            mp3_path = os.path.join(save_path, temp_name + ".mp3")
            if not os.path.exists(mp3_path):
                matches = glob.glob(os.path.join(save_path, temp_name + ".*"))
                mp3_path = matches[0] if matches else None

            # BPM Scan
            bpm_str = ""
            if mp3_path and os.path.exists(mp3_path):
                self._log(f"\n[BPM] Scanning tempo...", "amber")
                try:
                    y, sr = librosa.load(mp3_path, sr=None, mono=True)
                    tempo, _ = librosa.beat.beat_track(y=y, sr=sr)
                    bpm = float(np.round(tempo[0] if hasattr(tempo, '__len__') else tempo))
                    bpm_str = f" ({int(bpm)} BPM)"
                    self._log(f"[BPM] >>> {bpm:.0f} BPM <<<", "bpm_big")
                except Exception as e:
                    self._log(f"[BPM] Could not detect: {e}", "amber")

            # Rename file to include BPM
            if bpm_str and mp3_path and os.path.exists(mp3_path):
                ext = os.path.splitext(mp3_path)[1]
                final_name = f"{filename}{bpm_str}{ext}"
                final_path = os.path.join(save_path, final_name)
                try:
                    os.rename(mp3_path, final_path)
                    self._log(f"\n[OK] SAVED: {final_name}", "green")
                except Exception:
                    self._log(f"\n[OK] SAVED: {os.path.basename(mp3_path)}", "green")
            else:
                self._log(f"\n[OK] SAVED: {temp_name}.mp3", "green")

            self._log(f"[OK] Folder: {save_path}", "dim")

            # Clear URL for next download
            self.root.after(0, lambda: self.url_entry.delete(0, tk.END))

        except Exception as e:
            self._log(f"[ERR] {e}", "red")
        finally:
            self._reset_button()

    def _reset_button(self):
        self.is_downloading = False
        self.root.after(0, lambda: self.dl_btn.config(
            text=">>> DOWNLOAD <<<", bg=MATRIX_DARK, fg=MATRIX_GREEN, state="normal"))


# ── Launch ──────────────────────────────────────────────
if __name__ == "__main__":
    os.makedirs(DEFAULT_DIR, exist_ok=True)

    root = tk.Tk()
    w, h = 560, 520
    x = (root.winfo_screenwidth() // 2) - (w // 2)
    y = (root.winfo_screenheight() // 2) - (h // 2)
    root.geometry(f"{w}x{h}+{x}+{y}")

    app = GrabApp(root)
    root.mainloop()
