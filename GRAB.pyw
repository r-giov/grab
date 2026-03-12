"""
GRAB - YouTube Beat & Sample Downloader
Matrix Edition // Built for TRG Sensei
"""

import tkinter as tk
from tkinter import filedialog
import threading
import subprocess
import json
import re
import os
import random

# ── Config ──────────────────────────────────────────────
DEFAULT_DIR = r"M:\Youtube Beats\March Beats"

# ── Matrix Colors ───────────────────────────────────────
BG = "#000000"
BG2 = "#0a0a0a"
BG_PANEL = "#050505"
MATRIX_GREEN = "#00ff41"
MATRIX_DIM = "#0d6b1e"
MATRIX_BRIGHT = "#39ff14"
MATRIX_DARK = "#003b00"
FG = "#00ff41"
FG_DIM = "#0d6b1e"
RED = "#ff0040"
AMBER = "#ffb000"
CYAN = "#00e5ff"
WHITE = "#c0ffc0"
BORDER_COLOR = "#003b00"

BEAT_TAGS = ["boom-bap", "trap", "lo-fi", "soul", "jazz", "drill", "r&b", "experimental", "other"]
SAMPLE_TAGS = ["soul", "jazz", "funk", "gospel", "classical", "world", "vinyl-rip", "movie-dialogue", "other"]

FONT_MONO = "Consolas"
FONT_UI = "Consolas"


class MatrixRain:
    """Subtle matrix rain effect in the background."""
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
                    # Bright head
                    self.canvas.create_text(x, y, text=char, fill=MATRIX_GREEN,
                                           font=(FONT_MONO, 9), anchor="nw", tags="rain")
                    # Dimmer trail
                    if y - 16 >= 0:
                        self.canvas.create_text(x, y - 16, text=random.choice(self.chars),
                                               fill=MATRIX_DIM, font=(FONT_MONO, 8),
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

        self.save_dir = tk.StringVar(value=DEFAULT_DIR)
        self.category = tk.StringVar(value="beat")
        self.selected_tag = tk.StringVar(value="boom-bap")
        self.is_downloading = False

        self._build_ui()
        self.root.after(100, self._auto_paste)

    def _auto_paste(self):
        try:
            clip = self.root.clipboard_get()
            if any(x in clip for x in ["youtube.com/watch", "youtu.be/", "youtube.com/shorts"]):
                self.url_entry.delete(0, tk.END)
                self.url_entry.insert(0, clip)
                self._log("[SYS] URL detected in clipboard - auto-pasted", FG_DIM)
        except:
            pass

    def _make_bordered_frame(self, parent, **kwargs):
        outer = tk.Frame(parent, bg=BORDER_COLOR, padx=1, pady=1)
        inner = tk.Frame(outer, bg=BG_PANEL, **kwargs)
        inner.pack(fill="both", expand=True)
        return outer, inner

    def _build_ui(self):
        main = tk.Frame(self.root, bg=BG, padx=20, pady=10)
        main.pack(fill="both", expand=True)

        # ── Header with Matrix Rain Canvas ──────────
        header_frame = tk.Frame(main, bg=BG, height=80)
        header_frame.pack(fill="x", pady=(0, 8))
        header_frame.pack_propagate(False)

        self.rain_canvas = tk.Canvas(header_frame, bg=BG, highlightthickness=0,
                                     width=520, height=80)
        self.rain_canvas.pack(fill="both", expand=True)

        # Title overlay
        self.rain_canvas.create_text(260, 22, text="[ G R A B ]",
                                     font=(FONT_MONO, 26, "bold"), fill=MATRIX_GREEN)
        self.rain_canvas.create_text(260, 52, text="BEAT & SAMPLE DOWNLOADER // 320kbps",
                                     font=(FONT_MONO, 9), fill=MATRIX_DIM)
        self.rain_canvas.create_text(260, 68, text="< TRG SENSEI EDITION >",
                                     font=(FONT_MONO, 8), fill=MATRIX_DARK)

        # Start rain
        self.rain = MatrixRain(self.rain_canvas, 520, 80)
        self.rain.animate()

        # ── Save Location ──────────────────────────
        outer, loc_frame = self._make_bordered_frame(main, padx=10, pady=8)
        outer.pack(fill="x", pady=(0, 8))

        loc_top = tk.Frame(loc_frame, bg=BG_PANEL)
        loc_top.pack(fill="x")
        tk.Label(loc_top, text="> SAVE_DIR:", font=(FONT_MONO, 9, "bold"),
                 fg=MATRIX_GREEN, bg=BG_PANEL).pack(side="left")

        self.dir_label = tk.Label(loc_top, textvariable=self.save_dir,
                                  font=(FONT_MONO, 9), fg=CYAN, bg=BG_PANEL, anchor="w")
        self.dir_label.pack(side="left", padx=(6, 0), fill="x", expand=True)

        browse_btn = tk.Button(loc_top, text="[ BROWSE ]", font=(FONT_MONO, 8, "bold"),
                               fg=MATRIX_GREEN, bg=BG, relief="flat", bd=0,
                               activebackground=MATRIX_DARK, activeforeground=MATRIX_BRIGHT,
                               cursor="hand2", command=self._browse_folder)
        browse_btn.pack(side="right")

        # ── URL Input ──────────────────────────────
        outer, url_frame = self._make_bordered_frame(main, padx=10, pady=8)
        outer.pack(fill="x", pady=(0, 8))

        tk.Label(url_frame, text="> PASTE_URL:", font=(FONT_MONO, 9, "bold"),
                 fg=MATRIX_GREEN, bg=BG_PANEL).pack(anchor="w")

        self.url_entry = tk.Entry(url_frame, font=(FONT_MONO, 12),
                                  bg=BG, fg=MATRIX_BRIGHT, insertbackground=MATRIX_GREEN,
                                  relief="flat", bd=6, selectbackground=MATRIX_DARK,
                                  selectforeground=MATRIX_BRIGHT)
        self.url_entry.pack(fill="x", pady=(4, 0))
        self.url_entry.bind("<Return>", lambda e: self._start_download())

        # ── Category ───────────────────────────────
        outer, cat_frame = self._make_bordered_frame(main, padx=10, pady=8)
        outer.pack(fill="x", pady=(0, 8))

        tk.Label(cat_frame, text="> SELECT_TYPE:", font=(FONT_MONO, 9, "bold"),
                 fg=MATRIX_GREEN, bg=BG_PANEL).pack(anchor="w", pady=(0, 6))

        toggle = tk.Frame(cat_frame, bg=BG_PANEL)
        toggle.pack(fill="x")

        self.beat_btn = tk.Button(toggle, text="[ BEAT ]", font=(FONT_MONO, 13, "bold"),
                                  bg=MATRIX_DARK, fg=MATRIX_GREEN, relief="flat", bd=0,
                                  padx=20, pady=8, cursor="hand2",
                                  activebackground=MATRIX_GREEN, activeforeground=BG,
                                  command=lambda: self._set_category("beat"))
        self.beat_btn.pack(side="left", expand=True, fill="x", padx=(0, 4))

        self.sample_btn = tk.Button(toggle, text="[ SAMPLE ]", font=(FONT_MONO, 13, "bold"),
                                    bg=BG, fg=MATRIX_DIM, relief="flat", bd=0,
                                    padx=20, pady=8, cursor="hand2",
                                    activebackground=MATRIX_GREEN, activeforeground=BG,
                                    command=lambda: self._set_category("sample"))
        self.sample_btn.pack(side="left", expand=True, fill="x", padx=(4, 0))

        # ── Tags ───────────────────────────────────
        outer, tag_section = self._make_bordered_frame(main, padx=10, pady=8)
        outer.pack(fill="x", pady=(0, 8))

        tk.Label(tag_section, text="> TAG:", font=(FONT_MONO, 9, "bold"),
                 fg=MATRIX_GREEN, bg=BG_PANEL).pack(anchor="w", pady=(0, 6))

        self.tag_frame = tk.Frame(tag_section, bg=BG_PANEL)
        self.tag_frame.pack(fill="x")
        self._build_tags()

        # ── Custom Name ────────────────────────────
        outer, name_frame = self._make_bordered_frame(main, padx=10, pady=8)
        outer.pack(fill="x", pady=(0, 8))

        tk.Label(name_frame, text="> CUSTOM_NAME (optional):", font=(FONT_MONO, 9, "bold"),
                 fg=MATRIX_GREEN, bg=BG_PANEL).pack(anchor="w")

        self.name_entry = tk.Entry(name_frame, font=(FONT_MONO, 11),
                                   bg=BG, fg=MATRIX_BRIGHT, insertbackground=MATRIX_GREEN,
                                   relief="flat", bd=6, selectbackground=MATRIX_DARK,
                                   selectforeground=MATRIX_BRIGHT)
        self.name_entry.pack(fill="x", pady=(4, 0))

        # ── Download Button ────────────────────────
        self.dl_btn = tk.Button(main, text=">>> DOWNLOAD <<<", font=(FONT_MONO, 15, "bold"),
                                bg=MATRIX_DARK, fg=MATRIX_GREEN, relief="flat", bd=0,
                                pady=12, cursor="hand2",
                                activebackground=MATRIX_GREEN, activeforeground=BG,
                                command=self._start_download)
        self.dl_btn.pack(fill="x", pady=(0, 8))
        self.dl_btn.bind("<Enter>", lambda e: self.dl_btn.config(bg=MATRIX_GREEN, fg=BG) if not self.is_downloading else None)
        self.dl_btn.bind("<Leave>", lambda e: self.dl_btn.config(bg=MATRIX_DARK, fg=MATRIX_GREEN) if not self.is_downloading else None)

        # ── Terminal Log ───────────────────────────
        outer, log_frame = self._make_bordered_frame(main, padx=6, pady=6)
        outer.pack(fill="both", expand=True)

        self.log_text = tk.Text(log_frame, font=(FONT_MONO, 9),
                                bg=BG, fg=MATRIX_GREEN, relief="flat", bd=4,
                                height=7, state="disabled", wrap="word",
                                insertbackground=MATRIX_GREEN,
                                selectbackground=MATRIX_DARK)
        self.log_text.pack(fill="both", expand=True)

        for tag_name, color in [("green", MATRIX_GREEN), ("bright", MATRIX_BRIGHT),
                                 ("dim", MATRIX_DIM), ("red", RED),
                                 ("amber", AMBER), ("cyan", CYAN)]:
            self.log_text.tag_configure(tag_name, foreground=color)

        self._log("[SYS] GRAB v2.0 initialized", "dim")
        self._log(f"[SYS] Output: {self.save_dir.get()}", "dim")
        self._log("[SYS] Awaiting input...", "dim")

    def _browse_folder(self):
        folder = filedialog.askdirectory(initialdir=self.save_dir.get(),
                                         title="Select Download Folder")
        if folder:
            self.save_dir.set(folder)
            self._log(f"[SYS] Save dir changed: {folder}", "cyan")

    def _build_tags(self):
        for w in self.tag_frame.winfo_children():
            w.destroy()
        tags = BEAT_TAGS if self.category.get() == "beat" else SAMPLE_TAGS
        if self.selected_tag.get() not in tags:
            self.selected_tag.set(tags[0])

        row = tk.Frame(self.tag_frame, bg=BG_PANEL)
        row.pack(fill="x")
        for i, tag in enumerate(tags):
            if i > 0 and i % 5 == 0:
                row = tk.Frame(self.tag_frame, bg=BG_PANEL)
                row.pack(fill="x", pady=(3, 0))
            sel = (tag == self.selected_tag.get())
            btn = tk.Button(row, text=tag, font=(FONT_MONO, 9),
                            bg=MATRIX_DARK if sel else BG,
                            fg=MATRIX_GREEN if sel else MATRIX_DIM,
                            relief="flat", bd=0, padx=8, pady=4, cursor="hand2",
                            activebackground=MATRIX_DARK, activeforeground=MATRIX_GREEN,
                            command=lambda t=tag: self._select_tag(t))
            btn.pack(side="left", padx=(0, 3), pady=1)

    def _set_category(self, cat):
        self.category.set(cat)
        if cat == "beat":
            self.beat_btn.config(bg=MATRIX_DARK, fg=MATRIX_GREEN)
            self.sample_btn.config(bg=BG, fg=MATRIX_DIM)
        else:
            self.sample_btn.config(bg=MATRIX_DARK, fg=MATRIX_GREEN)
            self.beat_btn.config(bg=BG, fg=MATRIX_DIM)
        self._build_tags()

    def _select_tag(self, tag):
        self.selected_tag.set(tag)
        self._build_tags()

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

            # Fetch metadata
            cmd = ["yt-dlp", "--dump-json", "--no-download", url]
            flags = subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0
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

            # Build filename
            category = self.category.get()
            tag = self.selected_tag.get()
            custom_name = self.name_entry.get().strip()

            if custom_name:
                filename = custom_name
            else:
                filename = title
                for junk in ["[FREE]", "(FREE)", "FREE", "[free]", "(free)",
                              "| Type Beat", "type beat", "Type Beat",
                              "(Official Audio)", "(Official Video)",
                              "[Official Audio]", "[Official Video]"]:
                    filename = filename.replace(junk, "")
                filename = re.sub(r'[<>:"/\\|?*]', '', filename)
                filename = re.sub(r'\s+', ' ', filename).strip(" -_|")

            final_name = f"[{tag}] {filename}"
            save_path = self.save_dir.get()
            os.makedirs(save_path, exist_ok=True)
            output_template = os.path.join(save_path, final_name + ".%(ext)s")

            self._log(f"\n[DL] Downloading 320kbps MP3...", "amber")
            self._log(f"[DL] Type: {category} / {tag}", "dim")

            # Download as 320kbps MP3
            cmd = [
                "yt-dlp",
                "-x",
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
                # Retry without thumbnail if that failed
                self._log("[WARN] Retrying without thumbnail...", "amber")
                cmd_retry = [
                    "yt-dlp", "-x",
                    "--audio-format", "mp3",
                    "--audio-quality", "320K",
                    "--add-metadata",
                    "--no-playlist",
                    "-o", output_template,
                    url,
                ]
                result = subprocess.run(cmd_retry, capture_output=True, text=True, creationflags=flags)
                if result.returncode != 0:
                    self._log(f"[ERR] {result.stderr.strip()}", "red")
                    self._reset_button()
                    return

            self._log(f"\n[OK] DOWNLOAD COMPLETE", "green")
            self._log(f"[OK] {final_name}.mp3", "bright")
            self._log(f"[OK] Saved to: {save_path}", "dim")

            # Clear inputs for next download
            self.root.after(0, lambda: self.url_entry.delete(0, tk.END))
            self.root.after(0, lambda: self.name_entry.delete(0, tk.END))

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
    w, h = 560, 780
    x = (root.winfo_screenwidth() // 2) - (w // 2)
    y = (root.winfo_screenheight() // 2) - (h // 2)
    root.geometry(f"{w}x{h}+{x}+{y}")

    app = GrabApp(root)
    root.mainloop()
