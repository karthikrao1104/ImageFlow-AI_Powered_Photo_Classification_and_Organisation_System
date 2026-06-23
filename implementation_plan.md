# AI-Powered Photo Classification and Management System

This document outlines the implementation plan for building a web-based application that helps users organize and manage large collections of photos using Machine Learning for face detection and classification.

## Goal Description

Create a full-stack web application with the following features:
- User Authentication (Register/Login).
- Image uploading (single or bulk).
- Automatic face detection and classification: Identify faces, group them by person, and assign them to specific folders.
- Image/Folder Management: Rename folders, view images, copy folders, share folder URLs.
- Tech Stack: 
  - Frontend: HTML, CSS, Bootstrap, JavaScript.
  - Backend: Python Flask.
  - Database: MySQL.
  - ML/AI: `face_recognition` (Python library based on dlib), OpenCV, Pillow, Pandas.

> [!IMPORTANT]
> ## User Review Required
> Please review this plan to ensure it covers all the necessary requirements for your final project. In particular, check the Open Questions section below.

> [!WARNING]
> ## Open Questions
> 1. **Database:** The requirements mention MySQL. Do you already have a MySQL server running locally that we can connect to, or would you prefer to use SQLite for easier local development without requiring external database setup?
> 2. **Face Recognition Library:** The `face_recognition` Python package (which uses `dlib`) provides high accuracy but can be difficult to install on Windows. Are you okay with using it, or should we use a simpler (though slightly less accurate) alternative like OpenCV's Haar Cascades or Deep Neural Network (DNN) face detector combined with standard clustering?
> 3. **ORM:** Shall we use Flask-SQLAlchemy for database interactions to make the code cleaner, or do you require raw MySQL queries?

## Proposed Architecture & Structure

The project will be organized as follows:

### Backend (Python Flask)
- `app.py`: Main Flask application handling routing, controllers, and business logic.
- `database.py`: Database connection setup and models (Users, Photos, Folders, Faces).
- `ml_utils.py`: Machine Learning pipeline. Functions to load images, detect faces, extract encodings, and cluster them to group the same person across multiple photos.

### Frontend (HTML/CSS/Bootstrap)
- `templates/base.html`: Base layout containing the navigation bar (About, Contact sections) and footer.
- `templates/index.html`: Landing page with About and Contact.
- `templates/login.html` & `templates/register.html`: User authentication pages.
- `templates/dashboard.html`: Main user area showing auto-generated folders for different people.
- `templates/folder.html`: View showing all images of a specific person.
- `static/css/style.css`: Custom premium styling with modern aesthetics, glassmorphism, and responsive design.
- `static/js/main.js`: Frontend logic for uploads, renaming folders, and UI interactions.

### Data Storage
- `static/uploads/`: Directory to store uploaded original images.
- `static/faces/`: Directory to store cropped faces or organized links (symlinks or copies) representing the grouped folders.

## Implementation Steps

1. **Project Setup**: Initialize the Flask project, create directory structure, and set up `requirements.txt`.
2. **Database Setup**: Define the database schema for Users, Photos, Persons (Folders), and the relationship between Photos and Persons.
3. **Authentication**: Implement User Registration and Login using secure password hashing.
4. **Frontend UI Foundation**: Build the base HTML layout and modern styling using Vanilla CSS and Bootstrap.
5. **Upload & Storage**: Implement the photo upload mechanism in Flask.
6. **ML Pipeline Integration**:
   - Process uploaded images using OpenCV and `face_recognition`.
   - Extract face encodings.
   - Compare and cluster encodings to group identical people.
   - Save the results to the database and assign them to folders.
7. **Dashboard & Management**:
   - Display classified folders.
   - Allow users to rename person folders.
   - Implement folder copying and unique URL generation for sharing.
8. **Refinement & Testing**: Polish the UI aesthetics and test the end-to-end flow.

## Verification Plan

### Automated/Manual Testing
- Create a user account and log in.
- Upload a batch of mixed photos containing different people.
- Verify that the system correctly identifies and groups the same people into distinct folders.
- Verify that the user can rename folders.
- Test the share URL to ensure it correctly displays the intended folder's images.
