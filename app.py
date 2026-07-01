import os
from flask import Flask, render_template, request, redirect, url_for, flash, abort
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from database import db, User, Photo, Person, Face
import uuid
import threading
import time
import logging
import warnings

# Suppress the pkg_resources warning caused by face_recognition_models
warnings.filterwarnings("ignore", category=UserWarning, message=".*pkg_resources is deprecated as an API.*")

from ml_utils import process_uploaded_image

logging.basicConfig(
    filename='app.log',
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
# Suppress werkzeug default logger to avoid duplicate logs
logging.getLogger('werkzeug').setLevel(logging.WARNING)

gateway_logger = logging.getLogger('com.api.gateway.filters.PreAuthFilter')
login_logger = logging.getLogger('com.iam.engine.auth.LoginController')

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_super_secret_key_change_in_production'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db' # Use SQLite for local development, can be changed to mysql://user:pass@localhost/db
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = os.path.join('static', 'uploads')
app.config['FACES_FOLDER'] = os.path.join('static', 'faces')

# Ensure upload directories exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['FACES_FOLDER'], exist_ok=True)

db.init_app(app)

login_manager = LoginManager()
login_manager.login_view = 'login'
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Initialize database tables
with app.app_context():
    db.create_all()

@app.before_request
def before_request():
    request.start_time = time.time()
    gateway_logger.info(f"Request received URI={request.path} method={request.method} client_ip={request.remote_addr}")

@app.after_request
def after_request(response):
    if hasattr(request, 'start_time'):
        duration = int((time.time() - request.start_time) * 1000)
        gateway_logger.info(f"Request completed status={response.status_code} duration={duration}ms")
    return response

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/contact', methods=['POST'])
def contact():
    name = request.form.get('name')
    email = request.form.get('email')
    message = request.form.get('message')
    
    # In a real app, you would send an email or save to a database here.
    flash(f"Thank you {name}, your message has been received! We'll get back to you shortly.", "success")
    return redirect(url_for('index') + '#contact')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        
        user = User.query.filter_by(email=email).first()
        if user:
            flash('Email address already exists')
            return redirect(url_for('register'))
            
        user = User.query.filter_by(username=username).first()
        if user:
            flash('Username already exists')
            return redirect(url_for('register'))
            
        new_user = User(
            username=username,
            email=email,
            password_hash=generate_password_hash(password, method='scrypt')
        )
        
        db.session.add(new_user)
        db.session.commit()
        
        flash('Registration successful. Please log in.')
        return redirect(url_for('login'))
        
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
        
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        remember = True if request.form.get('remember') else False
        
        user = User.query.filter_by(email=email).first()
        
        if not user or not check_password_hash(user.password_hash, password):
            login_logger.error(f"AUTH_FAILURE method=PASSWORD user={email} status=INVALID_CREDENTIALS client_ip={request.remote_addr}")
            flash('Please check your login details and try again.')
            return redirect(url_for('login'))
            
        login_user(user, remember=remember)
        return redirect(url_for('dashboard'))
        
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/dashboard')
@login_required
def dashboard():
    persons = Person.query.filter_by(user_id=current_user.id).all()
    # Get one representative face for each person
    for person in persons:
        first_face = Face.query.filter_by(person_id=person.id).first()
        person.thumbnail = first_face.face_filename if first_face else None
        
    return render_template('dashboard.html', name=current_user.username, persons=persons)

@app.route('/upload', methods=['POST'])
@login_required
def upload():
    if 'photos' not in request.files:
        flash('No file part')
        return redirect(url_for('dashboard'))
        
    files = request.files.getlist('photos')
    
    if not files or files[0].filename == '':
        flash('No selected file')
        return redirect(url_for('dashboard'))
        
    for file in files:
        if file:
            filename = secure_filename(f"{uuid.uuid4().hex}_{file.filename}")
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            
            # Create Photo record
            new_photo = Photo(user_id=current_user.id, filename=filename)
            db.session.add(new_photo)
            db.session.commit()
            
            # Process in background or synchronously (sync for now to keep it simple, though background is better for multiple large files)
            # We'll do it sync for simplicity, but print a message.
            process_uploaded_image(new_photo, app)
            
    flash('Photos uploaded and processed successfully.')
    return redirect(url_for('dashboard'))

@app.route('/person/<int:person_id>')
@login_required
def view_person(person_id):
    person = Person.query.get_or_404(person_id)
    if person.user_id != current_user.id:
        abort(403)
        
    return render_template('folder.html', person=person, shared=False)

@app.route('/person/<int:person_id>/rename', methods=['POST'])
@login_required
def rename_person(person_id):
    person = Person.query.get_or_404(person_id)
    if person.user_id != current_user.id:
        abort(403)
        
    new_name = request.form.get('new_name')
    if new_name:
        person.name = new_name
        db.session.commit()
        flash('Folder renamed successfully.')
        
    return redirect(url_for('dashboard'))

@app.route('/share/<token>')
def shared_folder(token):
    person = Person.query.filter_by(share_token=token).first_or_404()
    return render_template('folder.html', person=person, shared=True)

@app.route('/person/<int:person_id>/delete', methods=['POST'])
@login_required
def delete_person(person_id):
    person = Person.query.get_or_404(person_id)
    if person.user_id != current_user.id:
        abort(403)
        
    # Get all photos this person appears in
    photo_ids = [face.photo_id for face in person.faces]
    
    # Delete the Person (which deletes their Faces via cascade)
    db.session.delete(person)
    
    # Now, find all those Photos and delete them completely
    if photo_ids:
        photos_to_delete = Photo.query.filter(Photo.id.in_(photo_ids)).all()
        for photo in photos_to_delete:
            # Remove original uploaded image
            photo_path = os.path.join(app.config['UPLOAD_FOLDER'], photo.filename)
            if os.path.exists(photo_path):
                try:
                    os.remove(photo_path)
                except Exception as e:
                    print(f"Error removing file {photo_path}: {e}")
                    
            # Delete face thumbnails for ALL faces in this photo (since the photo is being deleted)
            for face in photo.faces:
                face_path = os.path.join(app.config['FACES_FOLDER'], face.face_filename)
                if os.path.exists(face_path):
                    try:
                        os.remove(face_path)
                    except Exception as e:
                        print(f"Error removing face file {face_path}: {e}")
                        
            db.session.delete(photo)
            
    db.session.commit()
    flash('Folder and all associated original photos deleted completely.')
    
    return redirect(url_for('dashboard'))

@app.route('/photo/<int:photo_id>/delete', methods=['POST'])
@login_required
def delete_photo(photo_id):
    photo = Photo.query.get_or_404(photo_id)
    if photo.user_id != current_user.id:
        abort(403)
        
    # Remove original uploaded image
    photo_path = os.path.join(app.config['UPLOAD_FOLDER'], photo.filename)
    if os.path.exists(photo_path):
        try:
            os.remove(photo_path)
        except Exception as e:
            print(f"Error removing file {photo_path}: {e}")
            
    # Delete face thumbnails for ALL faces in this photo
    for face in photo.faces:
        face_path = os.path.join(app.config['FACES_FOLDER'], face.face_filename)
        if os.path.exists(face_path):
            try:
                os.remove(face_path)
            except Exception as e:
                print(f"Error removing face file {face_path}: {e}")
                
    db.session.delete(photo)
    db.session.commit()
    flash('Photo deleted successfully.')
    
    return redirect(request.referrer or url_for('dashboard'))

if __name__ == '__main__':
    print("\n" + "=" * 50)
    print(" Server is successfully running!")
    print(" Open your browser and go to: http://127.0.0.1:5000/")
    print("=" * 50 + "\n")
    app.run(debug=True)
