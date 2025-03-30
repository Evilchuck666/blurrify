<p align="center">
  <img src="https://github.com/user-attachments/assets/b8502c40-2ce6-48a4-9c47-2b42cd3f1489" alt="Blurrify logo" width="256"/>
</p>

# Blurrify

**Blurrify** is a Python-based automation tool for **blurring license plates** in video footage. It splits videos into segments, extracts frames, applies license plate detection using a Haar Cascade model, blurs detected areas, and rebuilds the final video with synchronized audio.

Perfect for anonymizing driving footage, car meets, or any video where license plates must be censored.

---

## 🔧 Requirements

- Python 3.8+
- FFmpeg
- MediaInfo
- Python packages:
  - `opencv-python`
  - `tqdm`
  - `pymediainfo`

### Install Python dependencies:

```bash
pip install opencv-python tqdm pymediainfo
```

Make sure **FFmpeg** and **MediaInfo** are installed and accessible from the command line:

```bash
ffmpeg -version
mediainfo --version
```

---

## 📁 Folder Structure

- `blurrify.py`: Main pipeline script
- `haar.py`: Script that applies blur using the Haar Cascade model
- `model.xml`: Haar Cascade model for license plate detection
- `input.txt`: Temporary file used for clip concatenation
- `settings.json`: Auto-generated configuration file located in `~/.config/blurrify/`

---

## 🚀 How to Use

1. Place your `.mp4` videos in the input directory (default: `~/Videos`)
2. Run the main script:

```bash
python3 blurrify.py
```

The script will:
- Extract the audio from the original video
- Split the video into 10 segments
- Extract video frames at 60 fps
- Detect and blur license plates in each frame
- Reassemble the processed frames into video clips
- Concatenate clips and mux with the original audio
- Save the final video in the output folder (default: `~/Videos/blurred`)

---

## ⚙️ Configuration

When running **Blurrify** for the first time, you'll be prompted to enter custom paths for:

- Input directory (videos to process)
- Output directory (final videos)
- Temporary working directory
- Assets directory (blur script and model)

These preferences are stored in `~/.config/blurrify/settings.json` and automatically reused in future runs.

You can delete this file anytime to reset the configuration.

---

## 🧪 Example

1. Download or record a video with visible license plates.
2. Place it in your input folder.
3. Run:

```bash
python3 blurrify.py
```

4. Check the blurred result in the output folder.
5. Audio will remain untouched and synced.

---

## 🧠 Notes

- This tool uses a **Haar Cascade XML model**, which can be replaced or trained to improve detection accuracy.
- You can modify the frame rate, video split logic, or blur intensity by editing `blurrify.py` and `haar.py`.
- Performance may vary based on video length, resolution, and hardware.
- This script is **not designed for real-time processing** but for efficient batch automation.
- The default model (`model.xml`) should be replaced if targeting different license plate formats (e.g., EU vs. US plates).

---

## 📜 License

This project is licensed under the **MIT License**.  
You are free to use, modify, and distribute it with proper attribution.  
See the full license in the [`LICENSE`](LICENSE) file.

---

## 🙌 Contributions

Contributions are welcome!

If you want to improve the detection model, optimize frame processing, or suggest enhancements, feel free to:

- Fork the repository
- Open an issue
- Submit a pull request

Let’s make Blurrify better together.

---

## ✨ Author

Created by **Carlos Martínez**  
2025 – Because privacy matters, even on the road.
