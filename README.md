# Blurrify

**Blurrify** is a Python script that automates the process of **blurring license plates** in videos. It splits the video into smaller clips, extracts frames, detects plates using a Haar Cascade model, applies blur, then reassembles everything with the original audio.

Ideal for protecting identities or anonymizing vehicles in driving videos, car meets, road footage, etc.

---

## 🔧 Requirements

- Python 3.8+
- FFmpeg
- OpenCV
- [`pymediainfo`](https://pypi.org/project/pymediainfo/)
- [`tqdm`](https://pypi.org/project/tqdm/)
- MediaInfo (system dependency, not Python-only)
- A trained Haar Cascade model for license plate detection (e.g. `haarcascade_russian_plate_number.xml`)

### Install Python dependencies:

```bash
pip install opencv-python tqdm pymediainfo
