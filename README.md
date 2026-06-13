# Litha News Network
Litha News Network is a Django-based article and newsletter management platform.

The system allows journalists to create articles, editors to review and approve content, and readers access to published news articles.

## Features
- Role-based authentication and access control (Journalist, Editor, Reader)
- Journalists, editor, reader dashboards
- Article creation, editing, approval and deletion workflows
- Newsletter management
- Password reset system using secure tokens
- Email notifications
- REST API endpoints
- Sphinx-generated documentation
- Docker container support

## Project Setup with Virtual Environment
Follow these steps in order to set up and run the application locally.

## 1. Clone repository
git clone https://github.com/Lilithabam13/Litha-News-Network.git
cd Litha-News-Network

## 2. Create virtual environment
python -m venv lbenv

## 3. Activate environment
- Linux / Mac:
  source lbenv/bin/activate

- Windows:
  lbenv\Scripts\activate

## 4. Install dependencies
- pip install --upgrade pip
- pip install -r requirements.txt
- pip install mysqlclient

## Database configuration (MariaDB)
Before running Litha News Network Application, configure a local MariaDB instance:

CREATE DATABASE lnn_db;

## 5. Run migrations
python LNN/manage.py migrate

## 6. Run server
python LNN/manage.py runserver

## Access the application
Local URL: http://127.0.0.1:8000/

## Docker Setup (Container Branch)

## Build image
docker build -t lnn-app .

## Run container
docker run -p 8000:8000 lnn-app

## Documentation (Sphinx)
- cd docs
- make html

## Project Structure
- master - main application
- container - Docker configuration
- docs - Sphinx documentation

## Technologies Used
- Python
- Django
- Django REST Framework
- Sphinx
- Docker
- MariaDB

