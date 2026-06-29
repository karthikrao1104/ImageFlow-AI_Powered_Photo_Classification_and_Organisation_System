import os
import face_recognition
import numpy as np
import uuid
from PIL import Image
from database import db, Person, Face

def process_uploaded_image(photo, app):
    """
    Process an uploaded image to detect and classify faces.
    
    :param photo: The Photo model instance
    :param app: The Flask app instance (to access config)
    """
    image_path = os.path.join(app.config['UPLOAD_FOLDER'], photo.filename)
    
    try:
        # Load the image
        image = face_recognition.load_image_file(image_path)
    except Exception as e:
        print(f"Error loading image {image_path}: {e}")
        return
        
    # Find all face locations and encodings in the image
    # Upsample the image 2 times to find smaller faces (increases precision/recall)
    # Note: If accuracy is still an issue and you don't mind slower processing, change model='hog' to model='cnn'
    face_locations = face_recognition.face_locations(image, number_of_times_to_upsample=2, model='cnn')
    
    # Use num_jitters=10 to calculate the face encoding 10 times and average it (significantly increases accuracy at the cost of processing time)
    face_encodings = face_recognition.face_encodings(image, face_locations, num_jitters=10)
    
    # Get all existing persons for this user
    existing_persons = Person.query.filter_by(user_id=photo.user_id).all()
    known_encodings = []
    known_person_ids = []
    
    # We will compare against the first face of each person for simplicity,
    # or better, against all faces. To keep it simple, we'll collect all 
    # face encodings known for this user.
    for person in existing_persons:
        for face in person.faces:
            known_encodings.append(face.get_encoding())
            known_person_ids.append(person.id)
            
    # Convert image to PIL for cropping
    pil_image = Image.fromarray(image)
    
    for i in range(len(face_encodings)):
        face_encoding = face_encodings[i]
        top, right, bottom, left = face_locations[i]
        
        match_found = False
        matched_person_id = None
        
        if len(known_encodings) > 0:
            # Compare face with known encodings using a stricter tolerance (default is 0.6, was 0.55, now 0.48)
            # A lower number makes face comparisons more strict, reducing false positives (mixing up people)
            matches = face_recognition.compare_faces(known_encodings, face_encoding, tolerance=0.48)
            face_distances = face_recognition.face_distance(known_encodings, face_encoding)
            
            if True in matches:
                # Find the best match (smallest distance)
                best_match_index = np.argmin(face_distances)
                if matches[best_match_index]:
                    matched_person_id = known_person_ids[best_match_index]
                    match_found = True
                    
        if not match_found:
            # Create a new person
            person_count = Person.query.filter_by(user_id=photo.user_id).count()
            new_person = Person(
                user_id=photo.user_id,
                name=f"Person {person_count + 1}",
                share_token=str(uuid.uuid4().hex)
            )
            db.session.add(new_person)
            db.session.commit()
            matched_person_id = new_person.id
            
        # Crop and save the face image
        # Add a little padding to the crop
        padding = 20
        c_top = max(0, top - padding)
        c_left = max(0, left - padding)
        c_bottom = min(pil_image.height, bottom + padding)
        c_right = min(pil_image.width, right + padding)
        
        cropped_face = pil_image.crop((c_left, c_top, c_right, c_bottom))
        
        face_filename = f"face_{photo.id}_{i}_{uuid.uuid4().hex[:8]}.jpg"
        face_path = os.path.join(app.config['FACES_FOLDER'], face_filename)
        cropped_face.save(face_path)
        
        # Create Face record
        new_face = Face(
            photo_id=photo.id,
            person_id=matched_person_id,
            face_filename=face_filename
        )
        new_face.set_encoding(face_encoding)
        db.session.add(new_face)
        
        # Add to known encodings so subsequent faces in the same upload batch can match
        known_encodings.append(face_encoding)
        known_person_ids.append(matched_person_id)
        
    db.session.commit()
