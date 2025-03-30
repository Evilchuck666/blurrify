# Blurrify

**Blurrify** es un script en Python que automatiza el proceso de desenfocar (blur) vídeos dividiéndolos en clips, extrayendo frames, aplicando detección de rostros, y volviendo a unirlos con el audio original.

Ideal para proteger identidades o censurar contenido sensible en vídeos de forma automatizada.

---

## 🧰 Requisitos

- Python 3.8 o superior
- FFmpeg
- OpenCV
- `pymediainfo`
- `tqdm`
- `MediaInfo` (dependencia de sistema, no solo Python)
- Modelo Haar XML para detección de rostros

Instala los módulos de Python necesarios con:

```bash
pip install opencv-python tqdm pymediainfo
