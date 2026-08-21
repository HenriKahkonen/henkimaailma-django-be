# henkimaailma-django-be
A Python Django backend for my personal homepage Henkimaailma

## Installation for local development:

### Activate venv and install dependencies:
```
#Linux/MacOS

python -m venv
source venv/bin/activate
pip install -r requirements.txt
```
### Define environment variables
```
#.env at project root
DB_NAME="yourname"
DB_PASS="yourpassword"
DB_USER="youruser"
```

### Start the database dockerized:
```
docker compose -f 'docker-compose.yml' up -d --build 'henkimaalma_db' 
```
