#Image Flow - AI Powered Photo Classification and Management System

This is a full-stack web application that allows users to upload messy collections of photos, and uses advanced Machine Learning (Face Recognition) to automatically detect, crop, and categorize the photos into individual folders for each person.

## Prerequisites

Before installing the project, you must ensure your system has the necessary build tools to compile C++ code. The core Machine Learning library (`dlib`, which `face_recognition` relies on) is written in C++ and **requires** compilation on Windows.

### 1. Install C++ Build Tools (Windows Only)
If you are on Windows, you **must** install Visual Studio C++ Build Tools before running the `pip install` command.
1. Download **CMake**: [https://cmake.org/download/](https://cmake.org/download/). When installing, make sure to check the box: **"Add CMake to the system PATH"**.
2. Download **Visual Studio Build Tools**: [https://visualstudio.microsoft.com/visual-cpp-build-tools/](https://visualstudio.microsoft.com/visual-cpp-build-tools/).
3. Run the installer, select the **"Desktop development with C++"** workload, and click Install.
4. Once installation is finished, restart your terminal or computer.

*(Note: MacOS and Linux users usually do not need extra steps, as standard C++ compilers are often pre-installed or easily available via `brew` or `apt`.)*

### 2. Python
Ensure you have **Python 3.10, 3.11, or 3.12** installed on your system.
You can download it from [python.org](https://www.python.org/downloads/).

---

## Installation & Setup

Follow these steps to get the project running on any new system:

### 1. Clone the Repository
Open your terminal or command prompt and clone this repository:
```bash
git clone https://github.com/adhisa-bala-rakshana/photoclass.git
cd photoclass
```

### 2. Create a Virtual Environment (Recommended)
It is highly recommended to create a virtual environment to isolate the project dependencies from your global Python installation.
```bash
# Create the virtual environment
python -m venv venv

# Activate it (Windows)
venv\Scripts\activate

# Activate it (Mac/Linux)
source venv/bin/activate
```

### 3. Install Dependencies
With your virtual environment activated, install all required packages using `requirements.txt`:
```bash
pip install -r requirements.txt
```
*(Note: The installation might take a few minutes as `dlib` compiles the C++ code).*

### 4. Run the Application
Start the Flask web server:
```bash
python app.py
```

### 5. Access the Web App
Open your web browser and navigate to:
```text
http://127.0.0.1:5000
```

---

## How to Use

1. **Register/Login:** Create a new account or log in. User data and photos are completely private and sandboxed.
2. **Upload Photos:** Go to the Dashboard and drag-and-drop your images (or select them from your device) into the upload zone.
3. **Wait for AI Processing:** The system will process the images. It upsamples the image to find small faces, extracts mathematically robust encodings using jittering, and strictly matches them to prevent false groupings.
4. **Manage Folders:** You will now see cleanly organized folders for every person found. You can:
   - Click a folder to view all original photos that person appears in.
   - Rename the folder.
   - Click **Share** to generate a public link you can send to others (no login required for them to view).
   - Click the **Delete (Trash)** icon to completely erase the folder, all associated face thumbnails, and the original uploaded photos from the server.
