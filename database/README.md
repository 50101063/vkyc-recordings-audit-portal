# Database

This directory contains the SQLite database file and related scripts for the V-KYC Recordings Audit Portal.

## Technology

- **Database:** SQLite
- **Interfacing Library:** SQLAlchemy (used by the Python backend)

## Overview

The database stores metadata for the V-KYC recordings, which allows the backend to quickly search and retrieve information without needing to access the video files on the NFS directly. It also stores user information for authenticating and authorizing access to the portal.

## Schema

The database contains two main tables:

1.  **`recordings`**: Stores metadata about each V-KYC recording, such as:
    -   `lan_id` (Loan Application Number)
    -   `call_duration_minutes`
    -   `status`
    -   `time`
    -   `date`
    -   `nfs_upload_time`
    -   `nfs_file_path` (the absolute path to the video file on the NFS)

2.  **`users`**: Stores credentials for portal access, including:
    -   `username`
    -   `password_hash`
    -   `role` (e.g., 'TL', 'Manager')

## Setup and Initialization

The SQLite database file (`vkyc_audit.db`) is managed by the backend application.

1.  **Automatic Creation**: The database file will be automatically created in the `backend/data/` directory when the backend server is started for the first time. The initialization logic is handled by the SQLAlchemy setup in the backend code.

2.  **Location**: The database file is located at `backend/data/vkyc_audit.db`.

3.  **Data Seeding**: The initial data, including the sample recordings metadata and user credentials, is seeded by a script in the backend. To run the seeding process, execute the following command from the `backend` directory:

    ```bash
    # Ensure your virtual environment is activated
    # On macOS/Linux: source venv/bin/activate
    # On Windows: .\\venv\\Scripts\\activate

    python seed_db.py
    ```

This will populate the database with the necessary data for the application to function correctly.
