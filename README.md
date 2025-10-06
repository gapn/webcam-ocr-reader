# 🎥 Webcam OCR Reader

A step‑by‑step **Python + OpenCV** project that shows a live webcam feed, highlights an interactive **ROI (Region of Interest)**, preprocesses it in real time using an advanced "scale-first" pipeline (**scale → denoise → sharpen → threshold**), and then pipes it to **Tesseract OCR**.

---

## 🚀 Demo (Local)

Run it locally and you’ll see three windows:
- **Webcam OCR – Live**: full camera frame with a green ROI rectangle.
- **Webcam OCR – ROI**: the raw cropped region.
- **Webcam OCR – Preprocessed ROI**: binarized, OCR‑friendly view.

> Click on camera feed window and then press **`q`** to quit.

---

## ⌨️ Controls & Modes

**Main Interaction**
- `w` — Start/Stop writing OCR results to Excel file
- `q` — Quit
- `s` — Select a Region of Interest (ROI) with the mouse

**Thresholding Modes:**
- `1` — Otsu (binary)
- `2` — Otsu (binary inverse)
- `3` — Adaptive Gaussian (binary)
- `4` — Adaptive Gaussian (binary inverse)
- `5` — Simple fixed threshold (uses the current threshold value)

**Live tuning:**
- `[` / `]` — Decrease/Increase fixed threshold (only used in Mode 5)
- `c` — Toggle CLAHE (local contrast equalization)
- `m` — Toggle morphology (dilation) to thicken thin digits
- `p` — Cycle Tesseract Page Segmentation Mode (PSM)
- `+ / -` — Increase/Decrease processing scale (resolution)
- `, / .` — Decrease/Increase save interval

---

### Recommended Tuning Workflow
1. Run the script and press `s` to draw a tight box around *only* the numbers.
2. Adjust the physical camera **focus** until the "Webcam OCR - ROI" window is perfectly sharp.
3. Use `+/-` to adjust the **Scale**. This is the most important setting.
4. Cycle through **Modes** `1-5` and toggle `c` (CLAHE) to find the cleanest black/white image in the "Preprocessed ROI" window

---

## ✨ Features

* [x] **Live Webcam Feed:** Opens your default camera and displays frames in real time.
* [x] **Interactive ROI:** Press `s` to select a new Region of Interest with the mouse.
* [x] **Advanced Realtime Preprocessing:** A full "scale-first" pipeline including denoising, sharpening, CLAHE, and edge enhancement.
* [x] **Robust OCR Integration:** Uses a multi-configuration `pytesseract` loop to extract text and a regex function to clean the result.
* [x] **Data Logging:** Saves OCR readings with timestamps to an Excel (`.xlsx`) file at a user-configurable interval.
* [x] **Live Tuning & Status Overlay:** Hotkeys to change all major parameters in real-time, with a clean HUD showing the current status.

---

## 🗺️ Roadmap / Future Ideas

* [x] **Adaptive Threshold or CLAHE** for tricky lighting.
* [x] **Morphology / Denoise / Deskew** for small fonts or screens.
* [ ] **Multi‑ROI** capture and per‑ROI OCR.
* [x] **Hotkeys:** `s` to select ROI, `+/-` to adjust scale.
* [ ] **Simple UI** (Tkinter/PySide) for non‑technical use.
* [ ] **Auto-Calibration Mode** to automatically find the best settings.

---

## 🛠️ Tech Stack

* **Python 3.10+**
* **OpenCV (cv2)** – video input, drawing, preprocessing
* **Tesseract OCR** + **pytesseract**
* **NumPy**
* **OpenPyXl** - for writing to Excel files
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
pip install opencv-python pytesseract numpy openpyxl
```
> If you accidentally installed `opencv-python-headless`, uninstall it and keep `opencv-python` (the GUI/video I/O‑capable wheel).

### 3) (Windows) Install Tesseract
- Download and install **Tesseract** (adds `tesseract.exe` to your PATH).
- Verify via: `tesseract --version`

---

## ▶️ Running

```bash
python main.py
```
- Press **`s`** in the application window to select region to read.
- Press **`w`** to start/stop saving data to Excel file.
- Press **`q`** to quit.

---

## 🧯 Windows Camera Troubleshooting

- **Privacy settings:** Settings → Privacy & security → **Camera** → enable both global camera access and **“Let desktop apps access your camera.”**
- **Close camera hogs:** Quit Teams/Zoom/Discord/OBS/Chrome tabs using the cam.
- **Backends & indices:** Try `cv2.CAP_MSMF`, `cv2.CAP_DSHOW`, or `cv2.CAP_ANY`, and indices `0/1/2`. Some cams sit on non‑zero indices.
- **OBS Virtual Camera:** Click **Start Virtual Camera** in OBS if you want that feed.
- **USB tips:** Try another USB port/cable; check Device Manager.

---

## 📜 License

This project is licensed under the [MIT License](./LICENSE.txt).