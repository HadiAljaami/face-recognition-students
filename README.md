# Face Recognition Students Project

## Overview

This project is a web-based face recognition system designed to identify and manage student records efficiently. The system uses PostgreSQL 16 as the database with the `pgvector` extension to handle vector similarity searches, enabling fast and accurate face recognition capabilities.

## Features

- **Face Recognition**: Efficiently identifies students using facial data.
- **Student Management**: Add, update, and remove student records.
- **PostgreSQL Integration**: Utilizes the power of PostgreSQL 16 with `pgvector` for vector data management.

## Prerequisites

Before starting, ensure you have the following:

- Node.js (v16 or later) and npm/yarn installed.
- PostgreSQL 16 installed on your system.
- `pgvector` extension enabled in PostgreSQL.

## Installation

### Step 1: Install PostgreSQL 16

1. Download and install PostgreSQL 16 from the [official PostgreSQL website](https://www.postgresql.org/download/).
2. Follow the installation guide for your operating system.
3. Verify the installation by running:
   ```bash
   psql --version
   ```

### Step 2: Install and Configure `pgvector`

Refer to the [pgvector repository](https://github.com/pgvector/pgvector.git) for installation instructions.

### Step 3: Clone the Repository

1. Extract the provided `face-recognition-students.zip` file or clone the repository:
   ```bash
   git clone https://github.com/HadiAljaami/face-recognition-students.git
   cd face-recognition-students
   ```

### Step 4: Install Dependencies

1. Install python dependencies:
   ```bash
   pip install -r requirements.txt
   ```

### Step 5: create database

After installation, run the `setup_db_vectors.py` script located in the `database` folder of this project to initialize the database and create the necessary tables:

```bash
py database/setup_db_vectors.py
```

Ensure you have Python 3 installed on your system.

### Step 7: Start the Project

1. Start the development server:
   ```bash
   py app.py
   ```
   or
   ```bash
   flask run --port=3000
   ```
2. Open your browser and navigate to `http://localhost:3000`.

## Usage

- Use the dashboard to manage students.
- Upload student photos for face recognition.

## Troubleshooting

- **Database connection issues**: Ensure `DATABASE_URL` is correctly set in `.env`.
- **`pgvector` not found**: Double-check that the `pgvector` extension is installed and enabled in PostgreSQL.

## Contributing

1. Fork the repository.
2. Create a feature branch.
3. Commit your changes.
4. Submit a pull request.

## License

This project is licensed under the MIT License. See the `LICENSE` file for details.

## Contact

For inquiries or support, please contact the project maintainer at [].
