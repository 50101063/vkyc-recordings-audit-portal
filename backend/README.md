# Backend (Python - Flask)

This folder contains the backend of the V-KYC Recordings Audit Portal, built with Python and the Flask framework. It provides a RESTful API for the frontend to interact with, handling business logic, database operations, and file system access.

## Technologies Used

- **Python Version**: 3.10+
- **Web Framework**: Flask
- **Database**: SQLite
- **ORM**: SQLAlchemy
- **Dependencies**: Listed in `requirements.txt`

## Setup and Execution

To get the backend server up and running, follow these steps.

### Prerequisites

- Python 3.10 or higher installed on your system.
- `pip` for package management.
- Access to the LTF NFS server where V-KYC recordings are stored (the path is configurable in `app.py`).

### 1. Create a Virtual Environment

It is highly recommended to use a virtual environment to manage project dependencies and avoid conflicts with other Python projects.

```bash
# Navigate to the backend directory
cd backend

# Create a virtual environment
python -m venv venv

# Activate the virtual environment
# On macOS and Linux:
source venv/bin/activate
# On Windows:
.\\venv\\Scripts\\activate
```

### 2. Install Dependencies

Install all the required Python packages from the `requirements.txt` file.

```bash
pip install -r requirements.txt
```

### 3. Initialize the Database

Before running the application for the first time, you need to initialize the SQLite database. This will create the `vkyc_audit.db` file and set up the required tables (`recordings` and `users`).

```bash
python database.py
```
You should see a confirmation message: `Database initialized and all tables created.`

### 4. Seed the Database with Sample Data

To populate the database with sample data for testing purposes, run the `seed.py` script. This script inserts the V-KYC recording metadata from the BRD into the `recordings` table and creates a sample user.

```bash
python seed.py
```
You should see a confirmation message: `Database seeded successfully with 35 recordings and 1 user.`

### 5. Run the Flask Application

Now you can start the Flask development server.

```bash
flask run
```

By default, the application will be available at `http://127.0.0.1:5000`.

- **API Base URL**: `http://127.0.0.1:5000/api`
- The server will automatically reload if you make any changes to the code.

## API Endpoints

The backend exposes the following RESTful API endpoints:

- `POST /api/login`: Authenticates a user and returns a JWT.
- `GET /api/recordings`: Fetches a paginated list of V-KYC recordings. Supports filtering by `lan_id`, `date`, `month`, and `year`.
- `GET /api/recordings/<lan_id>/download`: Downloads an individual video recording for the specified `lan_id`.
- `POST /api/bulk-download/upload`: Uploads a `.txt` or `.csv` file with LAN IDs and returns their metadata.
- `POST /api/bulk-download/initiate`: Initiates a bulk download of recordings (up to 10 at a time) and returns them as a ZIP archive.

For detailed information on request/response formats, refer to the source code in `app.py`.

## Project Structure

```
backend/
├── app.py              # Main Flask application file with API endpoints
├── database.py         # SQLAlchemy models and database initialization
├── seed.py             # Script to populate the database with sample data
├── requirements.txt    # Python package dependencies
└── README.md           # This setup and documentation file
```
