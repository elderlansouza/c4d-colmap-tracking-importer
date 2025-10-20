# COLMAP Tracking Importer C4D V1.3 — Readme

## Need help?
- Found a bug or have a feature request? Please open an **Issue** using the **Issues** tab.
- For quick questions or suggestions, you can also email me: **elderlan.design@gmail.com**.
- When filing an issue, include: Cinema 4D version, Redshift version, OS, a short repro, and any console errors.

## Tutorial
- Installing and using COLMAP on Windows: [How to use COLMAP](https://www.youtube.com/watch?v=PhdEk_RxkGQ)
- Installing COLMAP on macOS: https://gist.github.com/celestial-33/07438792a11964ee5f6f02847b6dbb03 and https://gist.github.com/celestial-33/a016465fd854d79a1b93458f167baa6a

## Required Tools & Links
1️⃣ **COLMAP (v3.12.3)**: Required for its libraries, which GLOMAP utilises.  
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
- Building a Redshift-compatible camera with correctly baked PSR and focal keyframes.
- Handling axis conversion automatically (COLMAP → Cinema 4D).
- Importing sparse point clouds and setting up Matrix objects.
- Creating a constrained duplicate camera for flexible workflows.
- Automatically configuring scene FPS, timeline ranges, and render resolution.

⚠️ **Note**: To visualise the point cloud in the Cinema 4D viewport, you must manually set the **Matrix object Distribution to Vertex**.

## Free Tool & Acknowledgment
This tool is completely **free**. If you use it in your projects, acknowledging **Elderlan Souza** as the creator of the Cinema 4D importer is greatly appreciated (but not compulsory).

Looking forward to seeing what you’ll create using it! ✨

For **bugs, suggestions, or any other queries**, please feel free to contact me at:  
📧 **elderlan.design@gmail.com**

---

## How to Use the Importer in Cinema 4D
1. Launch **Cinema 4D**.
2. Go to **Extensions → Script Manager → File → Load Script…** and load the Python script `colmap_importer.py`.
3. Run the script from the **Script Manager** or assign it to a shortcut/menu.
<img width="378" height="268" alt="image" src="https://github.com/user-attachments/assets/4b1aed7d-17e3-442b-90ff-e246bc0254e4" />

4. In the importer dialog:
   - Select your **Scene Folder** (the one containing the `SPARSE` folder and `IMAGES`).
   - Set **Sensor Width (mm)** (typically 36 mm for full-frame cameras).
   - Enter your **video FPS**.
   <img width="392" height="455" alt="image" src="https://github.com/user-attachments/assets/0720a868-9572-4ebb-ad22-e5da7bc4dab6" />

   - Adjust **Global Scale** if needed (default: 100).
   - Optionally, check **Import Sparse Point Cloud**.
6. Click **OK** to import.
7. The script will automatically:
<img width="362" height="256" alt="image" src="https://github.com/user-attachments/assets/f0e7ac7c-ec1d-4129-88d1-996dd7fe9966" />

   - Create a **Redshift Camera** with baked animation.
   - Duplicate it and add a **constraint** for flexibility.
   - Import the **sparse point cloud**.
   - Set **scene FPS, timeline, and render resolution**.
8. ⚠️ Remember:
   - To **see the point cloud in the viewport**, set the **Matrix object Distribution → Vertex** manually.
   <img width="515" height="500" alt="image" src="https://github.com/user-attachments/assets/894a681f-b2eb-48de-aad0-7e4f397afe3d" />

   <img width="1806" height="1108" alt="image" src="https://github.com/user-attachments/assets/9f4ddc66-deff-41bd-840d-4efe7dd9f200" />

   - To **configure the camera background**, do the following manually:
   <img width="519" height="1041" alt="image" src="https://github.com/user-attachments/assets/cd5abde5-c264-4206-9ef8-91749640ff1c" />

     - Set **Background → Override** on the RS Camera.
     - Select the first frame from the project’s `IMAGES` folder.
     - Change mode from **Image** to **Animation**.
     - Set **Animation Mode** to **Simple**.
     - Set **Timing** to **Frame**.
     - Press **Detect Frames** to load the sequence.
     <img width="266" height="40" alt="image" src="https://github.com/user-attachments/assets/76b34607-e983-452e-bca4-c10038fa9359" />
     <img width="1101" height="662" alt="image" src="https://github.com/user-attachments/assets/550135a1-72da-45b6-8468-52b4d6be3a49" />


   - To **adjust the ground plane alignment**, move the **`GLoMap_Scene_Orient` group**.
   <img width="1804" height="1130" alt="image" src="https://github.com/user-attachments/assets/ecfb99b1-6d36-407c-ad96-c24de36bdf60" />
   <img width="1589" height="1105" alt="image" src="https://github.com/user-attachments/assets/e822fe67-5417-4c6e-94cc-fc4300b0c811" />


   - The **RS_GLoMap_Render_Camera** uses a constraint to follow this transform.
   <img width="460" height="600" alt="image" src="https://github.com/user-attachments/assets/93e1bc9c-676a-430e-b804-0416ca79683e" />

   - If you need to export to other applications, you can bake the Render Camera’s final transform after alignment.

### Known Bug: Resolution & Background Distortion
- The scene resolution from COLMAP/GLOMAP isn’t always applied correctly. This causes the background image on the RS Camera to look distorted.
- **Fix**: Open **Render Settings → Output**, and re-type the output width or height. This forces Cinema 4D to update the film aspect ratio and restores the correct background image proportions.

---

## Fixing the framerate mismatch in After Effects

If the video **framerate is 23.98 or 29.97 FPS**, you will likely experience a mismatch when compositing because Cinema 4D can’t export at these framerates.  
To demonstrate the issue, we can composite the image sequence generated by GLOMAP with the original footage. The fix also works for 3D sequences rendered from Cinema 4D.

1. Launch **After Effects**.
2. Import the **original footage** into After Effects and create a **new composition**.
<img width="706" height="648" alt="image" src="https://github.com/user-attachments/assets/fa71c957-223a-4e2f-87a1-f17c036a02e1" />

3. Import the **rendered sequence** from GLOMAP (or Cinema 4D).
<img width="714" height="650" alt="image" src="https://github.com/user-attachments/assets/184d40f8-a8b9-4d37-8df5-dee5191bbe18" />

4. Select the **original footage**, right-click, **Interpret Footage → Remember Interpretation** (or **Ctrl+Alt+C** on Windows, **Cmd+Option+C** on Mac).
<img width="768" height="614" alt="image" src="https://github.com/user-attachments/assets/df7849fc-435a-4fda-997e-24da1a654854" />

5. Select the **image sequence**, right-click, **Interpret Footage → Apply Interpretation** (or **Ctrl+Alt+V** on Windows, **Cmd+Option+V** on Mac).
<img width="751" height="628" alt="image" src="https://github.com/user-attachments/assets/72f77a3b-a296-4ece-ac5c-682b0ca9e148" />

6. To visualise the frame mismatch, add the **image sequence** layer **on top of the original image** and change the mode to **Difference**.
<img width="772" height="132" alt="image" src="https://github.com/user-attachments/assets/c6fab1db-db0c-47b4-ad60-b5753fef63b9" />

7. You can now see where the pixels mismatch (inverted colour).
<img width="1703" height="970" alt="image" src="https://github.com/user-attachments/assets/528be034-bd47-4fe5-a8dd-df2775d82f97" />

8. To fix it, **stretch the duration by 0.01%** for the image sequence. Right-click the layer, **Time → Time Stretch**.
<img width="561" height="683" alt="image" src="https://github.com/user-attachments/assets/fe12fcca-9bc9-4a58-972a-fab9d633108a" />

9. Change the **stretch factor to 100.01%** and click **OK**.
<img width="800" height="402" alt="image" src="https://github.com/user-attachments/assets/963eac91-ba2e-4ad2-910a-ec860ada70d2" />

10. If all the pixels match, the frame will turn black.

This method, using the GLOMAP image sequence, works to visualise the fix. It can be applied to any 3D sequence rendered from Cinema 4D, except for the **Difference** blend mode, which is used only to visualise the mismatch in this tutorial.

---

## Setup & Use: AutoTracker v1.4 (.bat)
Follow these steps, extracted from the video transcript, to configure and run the batch script on Windows (CPU-only, no CUDA required):

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
   - (From the video: disabling in-camera stabilisation and using a 180° shutter—e.g., **1/60** at 30 fps—can help produce better motion blur for tracking.)

5. **Unpack FFMPEG**
   - Extract the FFMPEG archive and move **its contents** into `03 FFMPEG` (you should see `BIN/` and related files inside `03 FFMPEG`).

6. **Add the batch script**
   - Save **`AUTOTRACKER 1.4.BAT`** into `05 SCRIPT`.
   - Important: when downloading from the browser’s **RAW** view, some browsers append `.TXT`. Save as **ALL FILES** and make sure the filename **ends with `.BAT`** only.

7. **Run the script**
   - Double-click `05 SCRIPT/AUTOTRACKER 1.4.BAT`.
   - The first Windows security prompt may appear; allow it to run.
   - The script will:
     - Use **FFMPEG** to **extract frames** from your video (CPU).
     - Run **COLMAP feature extraction** over the frames.
     - Run **GLOMAP** to reconstruct and produce a track.
   - For faster processing, you can work with **1080p** footage instead of 4K.

8. **Outputs**
   - The script will populate your **`04 SCENES`** folder with the reconstructed project files (per the referenced script’s defaults).

### Troubleshooting (from the video)
- If the `.BAT` won’t run, confirm the extension isn’t `.BAT.TXT` and that SmartScreen isn’t blocking it.
- CUDA isn’t required here; the demonstrated workflow runs **CPU-only** and is still ~4× faster than the older COLMAP-only setup.

---

## License
This importer is released as **free to use and modify**.  
Credit to **Elderlan Souza** is appreciated but not compulsory when used in projects.
