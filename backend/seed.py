
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database import Base, Recording, User
from werkzeug.security import generate_password_hash
import datetime

# Database URL
DATABASE_URL = "sqlite:///./vkyc_audit.db"

# Sample data from the BRD
recordings_data = [
    {"lan_id": "C02503254240258405", "call_duration": "0:05:54", "status": "APPROVED", "time": "9:54:45 PM", "date": "25-03-2025", "nfs_upload_time": "2025-03-26"},
    {"lan_id": "C02503250415313063", "call_duration": "0:03:01", "status": "APPROVED", "time": "9:52:23 PM", "date": "25-03-2025", "nfs_upload_time": "2025-03-26"},
    {"lan_id": "C02502242042069761", "call_duration": "0:05:41", "status": "APPROVED", "time": "8:56:52 PM", "date": "25-03-2025", "nfs_upload_time": "2025-03-26"},
    {"lan_id": "C024032025114314", "call_duration": "0:02:20", "status": "APPROVED", "time": "8:52:01 PM", "date": "25-03-2025", "nfs_upload_time": "2025-03-26"},
    {"lan_id": "C02503252120609515", "call_duration": "0:05:20", "status": "APPROVED", "time": "8:44:44 PM", "date": "25-03-2025", "nfs_upload_time": "2025-03-26"},
    {"lan_id": "C02503253141799390", "call_duration": "0:08:00", "status": "APPROVED", "time": "8:38:22 PM", "date": "25-03-2025", "nfs_upload_time": "2025-03-26"},
    {"lan_id": "C02503200607877884", "call_duration": "0:06:51", "status": "APPROVED", "time": "8:34:51 PM", "date": "25-03-2025", "nfs_upload_time": "2025-03-26"},
    {"lan_id": "C02503245213389653", "call_duration": "0:03:03", "status": "APPROVED", "time": "8:34:28 PM", "date": "25-03-2025", "nfs_upload_time": "2025-03-26"},
    {"lan_id": "C02503232234479326", "call_duration": "0:04:43", "status": "APPROVED", "time": "8:30:15 PM", "date": "25-03-2025", "nfs_upload_time": "2025-03-26"},
    {"lan_id": "C024032025113615", "call_duration": "0:05:07", "status": "APPROVED", "time": "9:00:15 PM", "date": "26-03-2025", "nfs_upload_time": "2025-03-27"},
    {"lan_id": "C020032025130759", "call_duration": "0:05:34", "status": "APPROVED", "time": "8:57:53 PM", "date": "26-03-2025", "nfs_upload_time": "2025-03-27"},
    {"lan_id": "C020032025162126", "call_duration": "0:03:57", "status": "APPROVED", "time": "8:56:33 PM", "date": "26-03-2025", "nfs_upload_time": "2025-03-27"},
    {"lan_id": "C02503250173681850", "call_duration": "0:04:10", "status": "APPROVED", "time": "8:53:13 PM", "date": "26-03-2025", "nfs_upload_time": "2025-03-27"},
    {"lan_id": "C02503261737757676", "call_duration": "0:04:57", "status": "APPROVED", "time": "8:52:02 PM", "date": "26-03-2025", "nfs_upload_time": "2025-03-27"},
    {"lan_id": "C02503260118617491", "call_duration": "0:04:16", "status": "APPROVED", "time": "8:47:38 PM", "date": "26-03-2025", "nfs_upload_time": "2025-03-27"},
    {"lan_id": "C024032025160931", "call_duration": "0:02:21", "status": "APPROVED", "time": "8:46:34 PM", "date": "26-03-2025", "nfs_upload_time": "2025-03-27"},
    {"lan_id": "C02503040760787570", "call_duration": "0:06:23", "status": "APPROVED", "time": "8:41:23 PM", "date": "26-03-2025", "nfs_upload_time": "2025-03-27"},
    {"lan_id": "C024032025152946", "call_duration": "0:05:27", "status": "APPROVED", "time": "8:40:29 PM", "date": "26-03-2025", "nfs_upload_time": "2025-03-27"},
    {"lan_id": "C02503253123652728", "call_duration": "0:06:58", "status": "APPROVED", "time": "8:38:32 PM", "date": "26-03-2025", "nfs_upload_time": "2025-03-27"},
    {"lan_id": "C02503263175237197", "call_duration": "0:04:28", "status": "APPROVED", "time": "8:37:01 PM", "date": "26-03-2025", "nfs_upload_time": "2025-03-27"},
    {"lan_id": "C02503264936883686", "call_duration": "0:02:40", "status": "APPROVED", "time": "9:47:04 PM", "date": "27-03-2025", "nfs_upload_time": "2025-03-28"},
    {"lan_id": "C02503182115542422", "call_duration": "0:06:46", "status": "APPROVED", "time": "9:24:53 PM", "date": "27-03-2025", "nfs_upload_time": "2025-03-28"},
    {"lan_id": "C02503272432735191", "call_duration": "0:04:03", "status": "APPROVED", "time": "9:21:13 PM", "date": "27-03-2025", "nfs_upload_time": "2025-03-28"},
]

# Base path for NFS where video files are stored
NFS_BASE_PATH = "/mnt/nfs/vkyc_recordings"

def get_db_session():
    """Creates and returns a new database session."""
    engine = create_engine(DATABASE_URL)
    Base.metadata.bind = engine
    DBSession = sessionmaker(bind=engine)
    return DBSession()

def seed_data():
    """Populates the database with sample recordings and a default user."""
    session = get_db_session()

    # Check if data already exists to avoid duplication
    if session.query(Recording).count() > 0:
        print("Recordings data already exists. Skipping seeding.")
    else:
        print("Seeding recordings data...")
        for record_data in recordings_data:
            # Convert H:M:S duration to total minutes
            try:
                h, m, s = map(int, record_data["call_duration"].split(':'))
                duration_in_minutes = h * 60 + m + s / 60
            except ValueError:
                duration_in_minutes = 0 # Default value if format is unexpected

            # Construct the file path on the NFS server
            # Example path: /mnt/nfs/vkyc_recordings/2025-03-26/C02503254240258405.mp4
            file_name = f"{record_data['lan_id']}.mp4"
            file_path = os.path.join(NFS_BASE_PATH, record_data['nfs_upload_time'], file_name)

            new_record = Recording(
                lan_id=record_data["lan_id"],
                call_duration_minutes=int(round(duration_in_minutes)),
                status=record_data["status"],
                time=record_data["time"],
                date=record_data["date"],
                nfs_upload_time=record_data["nfs_upload_time"],
                nfs_file_path=file_path
            )
            session.add(new_record)
        print(f"{len(recordings_data)} recordings have been added.")

    # Check if the default user already exists
    if session.query(User).filter_by(username="vkyc_lead").count() > 0:
        print("Default user 'vkyc_lead' already exists. Skipping user creation.")
    else:
        print("Creating default user 'vkyc_lead'...")
        # Create a default user for testing
        hashed_password = generate_password_hash("password", method='pbkdf2:sha256')
        default_user = User(
            username="vkyc_lead",
            password_hash=hashed_password,
            role="TL" # Team Lead
        )
        session.add(default_user)
        print("Default user 'vkyc_lead' created with password 'password'.")

    # Commit the changes
    try:
        session.commit()
        print("Data seeding committed successfully.")
    except Exception as e:
        session.rollback()
        print(f"An error occurred during commit: {e}")
    finally:
        session.close()

if __name__ == "__main__":
    # Initialize the database and tables first
    from database import init_db
    init_db()
    
    # Then, seed the data
    seed_data()
