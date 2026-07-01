import os
import uuid
import numpy as np
import face_recognition
from PIL import Image
from database import db, Person, Face

# ── Tunable constants ──────────────────────────────────────────────────────────
# Extracting magic numbers to the top makes them easier to tweak later
TOLERANCE          = 0.75   # Face-match threshold (lower = stricter)
NUM_JITTERS        = 1     # Encoding jitters (accuracy vs. speed trade-off)
UPSAMPLE           = 0      # 0 makes CNN much faster by skipping image scaling
DETECTION_MODEL    = "cnn"  # "cnn" provides better accuracy than hog
FACE_PADDING       = 20     # Pixel padding around each cropped face
JPEG_QUALITY       = 85     # Saved face-crop quality (85 is visually lossless)
# ──────────────────────────────────────────────────────────────────────────────


def _load_known_encodings(user_id):
    """
    Pull all face encodings for a user in one DB round-trip and return
    parallel lists ready for face_recognition.compare_faces().
    """
    existing_persons = Person.query.filter_by(user_id=user_id).all()
    known_encodings  = []
    known_person_ids = []
    
    # 1. Reduce database round-trips: Load all persons and faces at once
    for person in existing_persons:
        for face in person.faces:
            enc = face.get_encoding()
            if enc is not None:             # guard against corrupt rows
                known_encodings.append(enc)
                known_person_ids.append(person.id)
    return known_encodings, known_person_ids


def _find_best_match(face_encoding, known_encodings, known_person_ids):
    """
    Return (match_found: bool, person_id: int | None).

    Uses face_distance directly so we pick the single closest match rather
    than relying on the binary matches array (which can have ties).
    """
    if not known_encodings:
        return False, None

    # 2. Use face_distance() directly instead of compare_faces()
    # 5. Use numpy vectorization: face_distance calculates distances for all known encodings optimally
    face_distances  = face_recognition.face_distance(known_encodings, face_encoding)
    best_idx        = int(np.argmin(face_distances))
    best_distance   = face_distances[best_idx]

    if best_distance <= TOLERANCE:
        return True, known_person_ids[best_idx]

    return False, None


def _create_person(user_id):
    """Insert a new unnamed Person and return its id."""
    person_count = Person.query.filter_by(user_id=user_id).count()
    new_person = Person(
        user_id=user_id,
        name=f"Person {person_count + 1}",
        share_token=uuid.uuid4().hex,
    )
    db.session.add(new_person)
    # 3. Batch database writes: use flush() mid-loop to get the ID without a full commit
    db.session.flush()          
    return new_person.id


def _crop_and_save_face(pil_image, location, photo_id, face_index, faces_folder):
    """Crop a face region with padding and persist it as JPEG."""
    top, right, bottom, left = location
    img_w, img_h = pil_image.size

    c_top    = max(0,     top    - FACE_PADDING)
    c_left   = max(0,     left   - FACE_PADDING)
    c_bottom = min(img_h, bottom + FACE_PADDING)
    c_right  = min(img_w, right  + FACE_PADDING)

    cropped      = pil_image.crop((c_left, c_top, c_right, c_bottom))
    face_filename = f"face_{photo_id}_{face_index}_{uuid.uuid4().hex[:8]}.jpg"
    face_path     = os.path.join(faces_folder, face_filename)
    
    # 6. Save face crops with JPEG quality=85 + optimize=True to reduce I/O time
    cropped.save(face_path, format="JPEG", quality=JPEG_QUALITY, optimize=True)
    return face_filename


def process_uploaded_image(photo, app):
    """
    Detect and classify every face in an uploaded photo.
    """
    image_path = os.path.join(app.config["UPLOAD_FOLDER"], photo.filename)

    # ── 1. Load image ──────────────────────────────────────────────────────────
    try:
        image = face_recognition.load_image_file(image_path)
    except Exception as e:
        print(f"[face_processor] Error loading image {image_path}: {e}")
        return

    # ── 2. Detect faces ────────────────────────────────────────────────────────
    face_locations = face_recognition.face_locations(
        image,
        number_of_times_to_upsample=UPSAMPLE,
        model=DETECTION_MODEL,
    )
    
    # 4. Skip processing early if no faces are detected
    if not face_locations:
        return  

    # ── 3. Encode faces ────────────────────────────────────────────────────────
    face_encodings = face_recognition.face_encodings(
        image,
        face_locations,
        num_jitters=NUM_JITTERS,
    )

    # ── 4. Load known encodings (one DB hit) ───────────────────────────────────
    # (Addresses goal #1)
    known_encodings, known_person_ids = _load_known_encodings(photo.user_id)

    pil_image = Image.fromarray(image)

    # ── 5. Match / create persons and persist faces ───────────────────────────
    for i, (face_encoding, location) in enumerate(zip(face_encodings, face_locations)):

        # (Addresses goals #2 and #5)
        match_found, matched_person_id = _find_best_match(
            face_encoding, known_encodings, known_person_ids
        )

        if not match_found:
            # (Addresses goal #3 - uses flush instead of commit)
            matched_person_id = _create_person(photo.user_id)

        # Crop & save face thumbnail
        # (Addresses goal #6)
        face_filename = _crop_and_save_face(
            pil_image, location, photo.id, i, app.config["FACES_FOLDER"]
        )

        # Persist Face record
        new_face = Face(
            photo_id=photo.id,
            person_id=matched_person_id,
            face_filename=face_filename,
        )
        new_face.set_encoding(face_encoding)
        db.session.add(new_face)

        # Update in-memory index so later faces in THIS batch can match
        known_encodings.append(face_encoding)
        known_person_ids.append(matched_person_id)

    # ── 6. Single commit for the whole photo ──────────────────────────────────
    # (Addresses goal #3 - single commit at the end)
    db.session.commit()
