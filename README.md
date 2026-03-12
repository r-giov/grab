# GRAB

**YouTube Beat & Sample Downloader — Matrix Edition**

A sleek, Matrix-themed desktop GUI for downloading YouTube audio as 320kbps MP3 files. Built for producers and artists who need a fast, organized workflow for grabbing beats and samples.

![Python](https://img.shields.io/badge/Python-3.10+-green?style=flat-square&logo=python)
![Platform](https://img.shields.io/badge/Platform-Windows-blue?style=flat-square)
![License](https://img.shields.io/badge/License-MIT-brightgreen?style=flat-square)

## Features

- **Matrix-themed GUI** with animated rain effect
- **320kbps MP3** downloads with embedded thumbnails & metadata
- **Beat or Sample** categorization
- **Genre tags** — boom-bap, trap, lo-fi, soul, jazz, drill, r&b, experimental, and more
- **Custom naming** or auto-clean YouTube titles
- **Folder picker** — save anywhere you want
- **Auto-paste** — copies YouTube URL from clipboard on launch
- **Terminal-style status log** with color-coded output

## Requirements

- Python 3.10+
- [yt-dlp](https://github.com/yt-dlp/yt-dlp) — `pip install yt-dlp`
- [FFmpeg](https://ffmpeg.org/download.html) — must be on PATH

## Install

```bash
git clone https://github.com/r-giov/grab.git
cd grab
pip install yt-dlp
```

## Usage

**Double-click** `GRAB.pyw` or `GRAB.bat` on Windows.

Or from terminal:
```bash
python GRAB.pyw
```

### Workflow
1. Copy a YouTube URL
2. Open GRAB (it auto-pastes the URL)
3. Select **Beat** or **Sample**
4. Pick a genre tag
5. Hit **DOWNLOAD**

Files save as: `[tag] Clean Title.mp3`

## Configuration

Edit the `DEFAULT_DIR` variable at the top of `GRAB.pyw` to change the default save location:

```python
DEFAULT_DIR = r"M:\Youtube Beats\March Beats"
```

Or just use the **[ BROWSE ]** button in the app.

## License

MIT
