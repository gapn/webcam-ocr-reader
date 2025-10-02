# 🎥 Webcam OCR Reader

A step‑by‑step **Python + OpenCV** project that shows a live webcam feed, highlights a configurable **ROI (Region of Interest)**, preprocesses it in real time (grayscale → blur → threshold), and then pipes it to **Tesseract OCR**.

---

## 🚀 Demo (Local)

Run it locally and you’ll see three windows:
- **Webcam OCR – Live**: full camera frame with a green ROI rectangle.
- **Webcam OCR – ROI**: the raw cropped region.
- **Webcam OCR – Preprocessed ROI**: binarized, OCR‑friendly view.

> Click on camera feed window and then press **`q`** to quit.

---

## ⌨️ Controls & Modes

**Windows:**
- `q` — Quit
- `1` — Otsu (binary)
- `2` — Otsu (binary inverse)
- `3` — Adaptive Gaussian (binary)
- `4` — Adaptive Gaussian (binary inverse)
- `5` — Simple fixed threshold (uses the current threshold value)

**Live tuning:**
- `[` / `]` — Decrease/Increase fixed threshold (only used in Mode 5)
- `c` — Toggle CLAHE (local contrast equalization)
- `m` — Toggle morphology (dilation) to thicken thin digits

### Recommended starting point (LCD panels)
1. Try **Mode 5 (Simple)** and tap `]` a few times until digits pop.
2. If the background is uneven or there’s glare, toggle **`c`** (CLAHE) on.
3. If digits look thin/broken, toggle **`m`** to dilate strokes slightly.
4. If lighting is very uneven, try **Mode 3/4 (Adaptive)** and play with CLAHE/morphology.

> Tip: Adjust the ROI (`ROI_X`, `ROI_Y`, `ROI_W`, `ROI_H`) so it tightly bounds the digits to reduce background noise.

---

## ✨ Features

* [x] **Live Webcam Feed:** Opens your default camera and displays frames in real time.
* [x] **Configurable ROI:** Tweak `ROI_X`, `ROI_Y`, `ROI_W`, `ROI_H` to focus on the text area.
* [x] **Realtime Preprocessing:** Grayscale + Gaussian blur + Otsu threshold for cleaner OCR.
* [ ] **OCR Integration:** Use `pytesseract` to extract text from the preprocessed ROI and show it live.
* [ ] **ROI UX:** Move/resize ROI with keyboard and mouse; save/load ROI presets.
* [ ] **FPS & Status Overlay:** Show frame rate and simple diagnostics on the live window.

---

## 🗺️ Roadmap / Future Ideas

* [ ] **Adaptive Threshold or CLAHE** for tricky lighting.
* [ ] **Morphology / Denoise / Deskew** for small fonts or screens.
* [ ] **Multi‑ROI** capture and per‑ROI OCR.
* [ ] **Hotkeys:** arrow keys to nudge ROI, `+/-` to resize, `s` to save config.
* [ ] **Simple UI** (Tkinter/PySide) for non‑technical use.

---

## 🛠️ Tech Stack

* **Python 3.10+**
* **OpenCV (cv2)** – video input, drawing, preprocessing
* **Tesseract OCR** (optional in Phase 3) + **pytesseract**
* **Windows 10/11** focused tips (works cross‑platform with minor tweaks)

---

## 🧑‍💻 Getting Started

### 1) Create & activate a virtual environment
```bash
python -m venv venv
# PowerShell
.\venv\Scripts\Activate.ps1
# cmd.exe
venv\Scripts\activate.bat
```

### 2) Install dependencies
```bash
pip install opencv-python pytesseract
```
> If you accidentally installed `opencv-python-headless`, uninstall it and keep `opencv-python` (the GUI/video I/O‑capable wheel).

### 3) (Windows) Install Tesseract (for Phase 3)
- Download and install **Tesseract** (adds `tesseract.exe` to your PATH).
- Verify via: `tesseract --version`

---

## ▶️ Running

```bash
python main.py
```
- **`q`** quits.
- Tweak the ROI constants at the top of `main.py`:
  ```python
  ROI_X = 100  # px from left
  ROI_Y = 100  # px from top
  ROI_W = 100  # width in px
  ROI_H = 100  # height in px
  ```

---

## 🧯 Windows Camera Troubleshooting

- **Privacy settings:** Settings → Privacy & security → **Camera** → enable both global camera access and **“Let desktop apps access your camera.”**
- **Close camera hogs:** Quit Teams/Zoom/Discord/OBS/Chrome tabs using the cam.
- **Backends & indices:** Try `cv2.CAP_MSMF`, `cv2.CAP_DSHOW`, or `cv2.CAP_ANY`, and indices `0/1/2`. Some cams sit on non‑zero indices.
- **OBS Virtual Camera:** Click **Start Virtual Camera** in OBS if you want that feed.
- **USB tips:** Try another USB port/cable; check Device Manager.

---

## 🔑 Keyboard (planned)

- `q` → Quit
- (Planned) Arrow keys → nudge ROI
- (Planned) +/- → resize ROI
- (Planned) s → save ROI config

---

## 📜 License

This project is licensed under the [MIT License](./LICENSE.txt).

---

## ✅ Commit Suggestions
