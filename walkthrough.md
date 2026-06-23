# AI-Powered Photo Classification and Management System

I have successfully completed the implementation of the AI-Powered Photo Classification and Management System according to your requirements. 

## What was implemented

### 1. Database & Models
- Built a robust schema using `Flask-SQLAlchemy` comprising four models: `User`, `Photo`, `Person`, and `Face`.
- Created an elegant structure that tracks which users own which photos and which recognized people, with secure one-to-many relationships.

### 2. User Authentication
- Developed secure registration and login systems utilizing `Werkzeug`'s `scrypt` hashing.
- Integrated `Flask-Login` for session management to restrict access to authenticated users.

### 3. Frontend & UI
- Implemented a modern, responsive user interface utilizing Bootstrap 5, custom CSS (`style.css`), and Font Awesome icons.
- Designed a stunning landing page, dashboard, and shared folder views incorporating glassmorphism effects, smooth gradients, and micro-animations for a premium feel.
- Added a drag-and-drop file upload zone enhanced with custom JavaScript (`main.js`).

### 4. Machine Learning Pipeline (`ml_utils.py`)
- Integrated the `face_recognition` library along with OpenCV and Pillow to detect, crop, and encode faces from uploaded images.
- Developed the clustering logic to match new faces against previously encountered individuals, automatically grouping them or creating new `Person` entries as required.
- Stored face encodings as JSON within the database for persistent and scalable matching.

### 5. Folder Management & Sharing
- Enabled the ability to view all images containing a specific person on the `folder.html` page.
- Added the feature to rename AI-generated person folders.
- Implemented unique share URLs using UUID tokens, allowing anyone with the link to view the photos without needing to log in.

## How to Run the Project

1. Ensure you have Python installed.
2. Open a terminal in your project directory (`c:/Users/HP/OneDrive/Desktop/final proj`).
3. Install dependencies: `pip install -r requirements.txt`.
   - **Note:** Installing `face_recognition` and `dlib` on Windows can sometimes require the Visual Studio C++ Build Tools. If you run into issues, make sure you have CMake and the C++ Build tools installed.
4. Run the Flask application: `python app.py`.
5. Open your web browser and navigate to `http://127.0.0.1:5000`.

## Verification Details

- **Database:** Local SQLite database automatically initializes on the first run. (Configured in `app.py`). This can be easily switched to a full MySQL server by updating the `SQLALCHEMY_DATABASE_URI` string.
- **Uploads:** Files are securely saved to `static/uploads`, and cropped thumbnails to `static/faces`.
- **Security:** CSRF protection and secure filename validation were included.

Feel free to try running the application and let me know if you would like to refine any specific feature!
