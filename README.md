# COLMAP Tracking Importer C4D V1.1 — Readme

## Tutorial
- Video Tutorial: [How to use COLMAP](https://www.youtube.com/watch?v=PhdEk_RxkGQ)

## Required Tools & Links
1️⃣ **COLMAP (v3.12.3)**: Required for its libraries, which GLOMAP utilizes.  
👉 https://github.com/colmap/colmap/releases/tag/3.12.0

2️⃣ **GLOMAP (v1.1.0)**: Faster reconstruction tool. Use the `WINDOWS-NOCUDA` version.  
👉 https://github.com/colmap/glomap/releases/tag/v1.1.0

3️⃣ **FFMPEG**: Command-line tool for converting video into an image sequence.  
👉 https://www.gyan.dev/ffmpeg/builds/

4️⃣ **AutoTracker v1.4 Batch Script**: Updated script designed to work with GLOMAP on Windows 11.  
👉 https://gist.github.com/polyfjord/fc213bac33b7eaaef4a80f4b6d9e5823

## Credits
Big thanks to **@Polyfjord**  
YouTube: https://www.youtube.com/polyfjord

In his video, Polyfjord built upon the previous automated 3D tracking photogrammetry workflow by introducing GLOMAP instead of just COLMAP. He explains how to download and prepare the necessary tools to make this workflow 100% open source.

## Where this Script Fits
Polyfjord’s workflow focuses on Blender. However, exporting the tracking from Blender often causes bugs, framerate mismatches, or axis orientation issues when moving into other 3D software.

This Python importer for **Cinema 4D** fills that gap by:
- Building a Redshift-compatible camera with correct baked PSR and focal keyframes.
- Handling axis conversion automatically (COLMAP → Cinema 4D).
- Importing sparse point clouds and setting up Matrix objects.
- Creating a constrained duplicate camera for flexible workflows.
- Automatically configuring scene FPS, timeline ranges, and render resolution.

## Free Tool & Acknowledgment
This tool is completely **free**. If you use it in your projects, you **must give credit** to the author (Elderlan Souza) as the creator of the Cinema 4D importer.

Looking forward to seeing what you’ll create using it! ✨

---

## Setup & Use: AutoTracker v1.4 (.bat)
Follow these steps extracted from the video transcript to configure and run the batch script on Windows (CPU-only, no CUDA required):

1. **Create the project folders**
   - Make a new folder, e.g. `AUTOTRACKER V1.4`.
   - Inside it, create these subfolders (exact names):
     - `01 GLOMAP`
     - `02 VIDEOS`
     - `03 FFMPEG`
     - `04 SCENES`
     - `05 SCRIPT`

2. **Download the tools**
   - COLMAP **v3.12.3** (use this version specifically).
   - GLOMAP **v1.1.0** (`WINDOWS-NOCUDA`).
   - FFMPEG (release essentials build).
   - AutoTracker **v1.4** batch script (save as `.BAT`, not `.TXT`).

3. **Populate `01 GLOMAP` with COLMAP + GLOMAP**
   - Extract the **COLMAP** download and open its `BIN/` folder. Select **all files** in `BIN` and **drag them into** `01 GLOMAP`.
   - Extract the **GLOMAP** download, open its `BIN/` folder, select **all files**, and drag them into `01 GLOMAP` as well. When prompted, **skip identical files**.
   - From the **root** of the extracted COLMAP folder, **copy the entire `PLUGINS/` folder** into `01 GLOMAP` (so `01 GLOMAP/PLUGINS` exists).
   - Result: `01 GLOMAP` should now contain `COLMAP.EXE`, GLOMAP executables, many `.DLL` files, and a `PLUGINS/` folder.

4. **Place your footage**
   - Put your source video file(s) into `02 VIDEOS`.
   - (From the video: disabling in‑camera stabilization and using a 180° shutter—e.g., **1/60** at 30 fps—can help produce better motion blur for tracking.)

5. **Unpack FFMPEG**
   - Extract the FFMPEG archive and move **its contents** into `03 FFMPEG` (you should see `BIN/` and related files inside `03 FFMPEG`).

6. **Add the batch script**
   - Save **`AUTOTRACKER 1.4.BAT`** into `05 SCRIPT`.
   - Important: when downloading from the browser’s **RAW** view, some browsers append `.TXT`. Save as **ALL FILES** and make sure the filename **ends with `.BAT`** only.

7. **Run the script**
   - Double‑click `05 SCRIPT/AUTOTRACKER 1.4.BAT`.
   - The first Windows security prompt may appear; allow it to run.
   - The script will:
     - Use **FFMPEG** to **extract frames** from your video (CPU).
     - Run **COLMAP feature extraction** over the frames.
     - Run **GLOMAP** to reconstruct and produce a track.
   - For faster processing, you can work with **1080P** footage instead of 4K.

8. **Outputs**
   - The script will populate your **`04 SCENES`** folder with the reconstructed project files (per the referenced script’s defaults).

### Troubleshooting (from the video)
- If the `.BAT` won’t run, confirm the extension isn’t `.BAT.TXT` and that SmartScreen isn’t blocking it.
- CUDA isn’t required here; the demonstrated workflow runs **CPU‑only** and is still ~4× faster than the older COLMAP‑only setup.
- If you later import into Blender and see **timing gaps in keyframes**, the video suggests either scaling keyframes by **33%** or importing from `SPARSE/0/` and re‑linking the background image sequence. (Cinema 4D users can skip Blender and use this importer instead.)

---

## License
**Credit is appreciated but not compulsory**: If you use this Software in personal,
   educational, commercial, or non-commercial projects, acknowledging **Elderlan Souza**
   as the creator of the "Cinema 4D COLMAP Importer" would be greatly appreciated.
