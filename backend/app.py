
from flask import Flask, request, jsonify, send_from_directory, abort
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy.orm import sessionmaker
from database import engine, Recording, User, init_db, SessionLocal
import os
import csv
import zipfile
from io import BytesIO

# Configuration
# In a real app, use a config file or environment variables
# This is a placeholder for the actual NFS path
NFS_BASE_PATH = os.environ.get("NFS_BASE_PATH", "/mnt/nfs/vkyc_recordings") 
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'txt', 'csv'}

# Create Flask app
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Ensure upload folder exists
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# --- Database Session ---
def get_db():
    """
    Dependency to get a new database session for each request.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# --- Helper Functions ---
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# --- API Endpoints ---
@app.route("/")
def index():
    return jsonify({"message": "V-KYC Recordings Audit Portal API is running."})

@app.route('/api/recordings', methods=['GET'])
def get_recordings():
    """
    Search and filter recordings.
    Query params: lan_id, date, month, year, page, per_page
    """
    db_gen = get_db()
    db = next(db_gen)
    
    query = db.query(Recording)
    
    # Filtering
    if 'lan_id' in request.args:
        query = query.filter(Recording.lan_id.ilike(f"%{request.args['lan_id']}%"))
    if 'date' in request.args:
        query = query.filter(Recording.date == request.args['date'])
    # Add month/year filtering if needed by parsing the date column
    
    # Pagination
    page = int(request.args.get('page', 1))
    per_page = int(request.args.get('per_page', 10))
    paginated_query = query.limit(per_page).offset((page - 1) * per_page)
    
    results = paginated_query.all()
    total_count = query.count()
    
    return jsonify({
        "total_count": total_count,
        "page": page,
        "per_page": per_page,
        "recordings": [{
            "lan_id": rec.lan_id,
            "date": rec.date,
            "month": rec.date.split('-')[1] if rec.date else '',
            "year": rec.date.split('-')[0] if rec.date else '',
            "call_duration_minutes": rec.call_duration_minutes,
            "status": rec.status,
            "time": rec.time
        } for rec in results]
    })

@app.route('/api/recordings/<string:lan_id>/download', methods=['GET'])
def download_recording(lan_id):
    """
    Download a single video recording.
    This simulates streaming from an NFS path.
    """
    db_gen = get_db()
    db = next(db_gen)
    
    recording = db.query(Recording).filter(Recording.lan_id == lan_id).first()
    
    if not recording:
        abort(404, description="Recording not found.")
        
    # Security: Ensure the path is safe
    # In a real implementation, you must sanitize this to prevent path traversal.
    file_path = os.path.join(NFS_BASE_PATH, recording.nfs_file_path)
    
    if not os.path.exists(file_path):
        abort(404, description="File not found on the storage server.")
        
    directory = os.path.dirname(file_path)
    filename = os.path.basename(file_path)
    
    return send_from_directory(directory, filename, as_attachment=True)

@app.route('/api/bulk-download/upload', methods=['POST'])
def upload_lan_file():
    """
    Upload a CSV/TXT file with LAN IDs for bulk processing.
    """
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400
    
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        lan_ids = []
        try:
            with open(filepath, 'r') as f:
                reader = csv.reader(f)
                for row in reader:
                    if row:
                        lan_ids.append(row[0].strip())
            
            if not (2 <= len(lan_ids) <= 50):
                return jsonify({"error": "File must contain between 2 and 50 LAN IDs."}), 400

            # Query the database for the provided LAN IDs
            db_gen = get_db()
            db = next(db_gen)
            recordings = db.query(Recording).filter(Recording.lan_id.in_(lan_ids)).all()
            
            return jsonify([{
                "lan_id": rec.lan_id,
                "date": rec.date,
                "status": rec.status,
                "file_found": True
            } for rec in recordings])

        except Exception as e:
            return jsonify({"error": f"Failed to process file: {e}"}), 500
        finally:
            os.remove(filepath) # Clean up the uploaded file
    
    return jsonify({"error": "File type not allowed"}), 400

@app.route('/api/bulk-download/initiate', methods=['POST'])
def initiate_bulk_download():
    """
    Initiates the download of multiple recordings as a ZIP file.
    Expects a JSON payload with a list of LAN IDs.
    """
    data = request.get_json()
    if not data or 'lan_ids' not in data:
        return jsonify({"error": "Missing lan_ids in request body"}), 400
        
    lan_ids = data['lan_ids']
    if not isinstance(lan_ids, list) or not (1 <= len(lan_ids) <= 10):
         return jsonify({"error": "A list of 1 to 10 LAN IDs is required."}), 400

    db_gen = get_db()
    db = next(db_gen)
    
    recordings = db.query(Recording).filter(Recording.lan_id.in_(lan_ids)).all()
    
    memory_file = BytesIO()
    with zipfile.ZipFile(memory_file, 'w', zipfile.ZIP_DEFLATED) as zf:
        for rec in recordings:
            file_path = os.path.join(NFS_BASE_PATH, rec.nfs_file_path)
            if os.path.exists(file_path):
                zf.write(file_path, os.path.basename(file_path))

    memory_file.seek(0)
    return send_file(memory_file, download_name='vkyc_recordings.zip', as_attachment=True)

# --- CLI Command to initialize DB ---
@app.cli.command("initdb")
def initdb_command():
    """Creates the database tables."""
    init_db()
    print("Initialized the database.")

@app.cli.command("seeddb")
def seeddb_command():
    """Seeds the database with sample data."""
    db_gen = get_db()
    db = next(db_gen)
    
    # Create a dummy user
    if not db.query(User).filter_by(username="testuser").first():
        hashed_password = generate_password_hash("password", method='pbkdf2:sha256')
        new_user = User(username="testuser", password_hash=hashed_password, role="TL")
        db.add(new_user)

    # Create dummy recordings
    if db.query(Recording).count() == 0:
        sample_recordings = [
            Recording(lan_id='C08383828282882', date='2025-02-23', nfs_file_path='rec1.mp4'),
            Recording(lan_id='C02503254240258405', date='2025-03-25', nfs_file_path='rec2.mp4'),
            # Add more sample data as needed
        ]
        db.bulk_save_objects(sample_recordings)
    
    db.commit()
    print("Database seeded with sample data.")


if __name__ == '__main__':
    # For development server
    app.run(debug=True, port=5001)
