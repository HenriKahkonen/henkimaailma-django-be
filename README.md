# henkimaailma-django-be
A Python Django backend for my personal homepage Henkimaailma

## Installation for local development:

#### 1. Activate venv and install dependencies:
```
#Linux/MacOS

python -m venv
source venv/bin/activate
pip install -r requirements.txt
```
#### 2. Define environment variables for the database
At the project root there is a template .env that you can use to define a local postgresql configuration as well as a deployed database connection.
```
#.env at project root
DB_HOST="localhost"
DB_NAME="yourname"
DB_PASS="yourpassword"
DB_USER="youruser"
DB_PORT=5432
```

#### 3. Create the containerized database:
```
docker compose -f 'docker-compose.yml' up -d --build 'henkimaalma_db' 
```

#### 4. Initialize database with the data models:
```
python manage.py makemigrations
python manage.py migrate
```

#### 5. Create superuser for Django:
```
python manage.py createsuperuser
# Follow prompts to create root user
```

#### 6. Run 
```
python manage.py runserver
# In your web browser navigate to http://127.0.0.1:8000/admin
```

