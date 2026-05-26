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

# Setup with Virtual Environment

## Clone repository

git clone https://github.com/Lilithabam13/Litha-News-Network

## Create virtual environment

python -m venv lbenv

## Activate environment

source lbenv/bin/activate

## Install dependencies

pip install -r requirements.txt

## Run migrations

python LNN/manage.py migrate

## Run server

python LNN/manage.py runserver

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
- SQLite

