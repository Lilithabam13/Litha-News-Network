# Litha News Network

Litha News Network is a Django-based article and newsletter management platform.

The system allows journalists to create articles, editors to review and approve content, and readers access to published news articles.

## Features

- Role-based authentication and access control
- Journalists, editor, reader dashboards
- Article creation, editing, approval and deletion workflows
- Password reset system using secure tokens
- Email notifications
- REST API endpoint for articles
- Sphinx-generated documentation
- Docker container support

## Setup with Virtual Environment

Follow these steps in order to set up and run the application locally.

### 1. Clone repository
Clone the repository to your local machine and navigate into project directory:

git clone [https://github.com/Lilithabam13/Litha-News-Network](http://github.com/Lilithabam13/Litha-News-Network) cd Litha-News-Network

## 2. Create virtual environment

python -m venv lbenv

## 3. Activate environment

source lbenv/bin/activate

## 4. Install dependencies

pip install --upgrade pip
pip install -r requirements.txt
pip install mysqlclient

## 5. Database configuration

Before running Litha News Network Application, configure a local MariaDB instance:
'''sql
CREATE DATABASE lnn_db;

## 6. Run migrations

python LNN/manage.py migrate

## 7. Run server

python LNN/manage.py runserver

## Access the application

Local URL: http://127.0.0.1:8000/

---

# Docker Setup

## Build image

docker build -t lnn-app .

## Run container

docker run -p 8000:8000 lnn-app

### Technologies Used

- Python
- Django
- Django REST Framework
- Sphinx
- Docker
- MariaDB
