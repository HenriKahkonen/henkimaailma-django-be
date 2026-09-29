# henkimaailma-django-be
A Python Django backend for my personal homepage Henkimaailma.
For the frontend code, see [here](https://github.com/HenriKahkonen/henkimaailma-ts)

## Installation for local development:

#### 1. Make sure Docker is installed on the system.

#### 2. Create and activate venv and install dependencies:
```
#Linux/MacOS

python -m venv venv
source venv/bin/activate # or: source venv/bin/activate.fish if using fish terminal
pip install -r requirements.txt
```
#### 3. Define environment variables for the database
At the project root there is a template .env that you can use to define a local postgresql configuration as well as a deployed database connection. 

**Remember to remove the line DATABASE_URL if you are developing locally and not connecting to an external database.**

```
#.env at project root
DB_HOST="localhost"
DB_NAME="yourname"
DB_PASS="yourpassword"
DB_USER="youruser"
DB_PORT=5432
```

#### 4. Create the containers that run the app:
```
docker compose up -d
```

#### 5. Initialize database with the data models:
```
docker compose exec web python manage.py migrate
```

#### 6. Create superuser for Django:
```
docker compose exec web python manage.py createsuperuser
# Follow prompts to create root user
```

#### 7. Connect to Django admin panel to verify server is online

In your web browser navigate to http://127.0.0.1:8080/admin

#### 8. (Optional): migrate data

The backend supports exporting and importing backups of data, when manual backups are set to be allowed by setting the .env variable BACKUPS_ENABLED to True. If you wish to import data from a deployed Database, 

1. SSH into the deployed instance, set the .env variable to True and then 
2. GET, passing the correct credentials in the post to ${your_db_location}/backup/export and copy the response
3. Set the .env variable back to BACKUPS_ENABLED=False on your deployed instance
4. POST with the response as your post body, to http://localhost:8080/backup/restore 

**At this point the database is not synced with what Django expects so new items cannot be added to the database due to the new items throwing IntegrityError**. This is because after the data import Django tries to add a public key = 1 to the first new item in the database, all the while it already existing without Django's public key pointer being updated to match the actual state of the database.

To fix, replace the placeholder strings with your actual database DB_NAME and DB_USER settings declared in the .env and run:

```
docker compose exec web python manage.py sqlsequencereset content | docker compose exec -T henkimaailma_db psql -U <YOUR_DB_USER> -d <YOUR_DB_NAME>
```
