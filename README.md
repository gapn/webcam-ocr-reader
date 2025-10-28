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

* **Python 3.12**
* **OpenCV (cv2)** – video input, drawing, preprocessing
* **Tesseract OCR** + **pytesseract**
* **NumPy**
* **OpenPyXl** - for writing to Excel files
* **Windows 10/11**

---

## 🧑‍💻 Getting Started

### 1) Prerequisites (Install first!)

Before setting up the project, ensure you have the following installed on your system:
* **Python 3.12:** This project is built and tested on **Python 3.12.10**. Newer versions (3.13+) are known to have compatibility issues (at the moment of creating this project).
* **(Windows) Tesseract-OCR:**
    * Download and install **Tesseract** from [official installers page](https://github.com/UB-Mannheim/tesseract/wiki).
    * Ensure that installer adds `tesseract.exe` to your system's PATH, if not, add it manually.
    * Verify via new terminal: `tesseract --version`

### 2) Project Setup

1. **Clone or download project, `cd` in the folder**

2. **Create virtual environment using Python 3.12 executable:**
```bash
py -3.12 -m venv venv
```

3. **Activate virtual environment:**
```
# PowerShell
.\venv\Scripts\Activate.ps1
# cmd.exe
venv\Scripts\activate.bat
```

4. **Install dependencies**
```bash
pip install -r requirements.txt
```
> If you accidentally installed `opencv-python-headless`, uninstall it and keep `opencv-python` (the GUI/video I/O‑capable wheel).

---

## ▶️ Running

```bash
python main.py
```
- Press **`s`** in the application window to select region to read.
- Press **`w`** to start/stop saving data to Excel file.
- Press **`q`** to quit.

---

## 📦 Creating a Distributable `.exe`

This project uses **PyInstaller** to create a standalone Windows application. Due to an external dependency on Tesseract and potential packaging issues, the process requires a few specific steps.

**Build Steps:**

1.  **Install PyInstaller:**
    ```bash
    pip install pyinstaller
    ```
2.  **Prepare Tesseract Files:**
    - Find your Tesseract installation folder (e.g., `C:\Program Files\Tesseract-OCR`).
    - Copy the entire `Tesseract-OCR` folder and paste it into the root of this project directory, so it sits next to `main.py`.

3.  **Generate the `.spec` File:** Generate a configuration file with the correct application name.
    ```bash
    pyinstaller --name WebcamOCR main.py
    ```
    - This will create a `WebcamOCR.spec` file in your project directory.

4.  **Edit the `.spec` File:** Open `WebcamOCR.spec` and add the `datas` variable to the `Analysis` section to include the Tesseract folder.
    ```python
    a = Analysis(
        ['main.py'],
        ...,
        datas=[('Tesseract-OCR', 'Tesseract-OCR')],  # <-- ADD THIS LINE
        ...
    )
    ```
5.  **Build the Application:** Run PyInstaller using the `.spec` file from a terminal with **Administrator privileges**.
    ```bash
    pyinstaller --clean WebcamOCR.spec
    ```
6.  **Final Manual Step:** After the build is complete, manually **copy** the `Tesseract-OCR` folder from your project root into the final build directory, which will be `dist/WebcamOCR`.

The entire `dist/WebcamOCR` folder is now the complete, distributable application. You can zip it and share it.

---

## 🖥️ Using the Distributed Application

For colleagues running the final `WebcamOCR.exe` on a new computer.

### Prerequisites
Before running the application for the first time, a required system component must be installed.

-   **Microsoft Visual C++ Redistributable**: Download and install the "x64" version from the [official Microsoft website](https://learn.microsoft.com/en-us/cpp/windows/latest-supported-vc-redist).

### Running the Application
1.  Unzip the entire application folder (e.g., `WebcamOCR.zip`) to a location on your computer, like your folder for applications.
2.  Open the `WebcamOCR` folder and double-click `WebcamOCR.exe` to run it.

### Troubleshooting
-   If the application closes immediately or the camera doesn't open, try right-clicking `WebcamOCR.exe` and selecting **"Run as administrator"**.
-   Ensure no other applications (like Microsoft Teams, Zoom, etc.) are using the camera.
-   The application needs permission to write files, so don't run it from a read-only location.

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