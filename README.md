# django-seenit
Reddit style message board with users, channels, posts, and comments. 

## Local setup
1. Create and activate a virtual environment
2. Install dependencies
   ```
   pip3 install -r requirements.txt
   ```
3. Create a new PostgreSQL database and user
   ```
   psql
   postgres=# CREATE DATABASE seenit;
   postgres=# CREATE USER seenitadmin WITH PASSWORD 'password';
   postgres=# ALTER ROLE seenitadmin SET client_encoding TO 'utf8';
   postgres=# ALTER ROLE seenitadmin SET default_transaction_isolation TO 'read committed';
   postgres=# ALTER ROLE seenitadmin SET timezone TO 'UTC';
   postgres=# GRANT ALL PRIVILEGES ON DATABASE seenit TO seenitadmin;
   ```
3. Generate a secret key
   ```
   python manage.py shell
   from django.core.management.utils import get_random_secret_key
   print(get_random_secret_key())
   ```
5. Create a .env file in seenit_project directory with:
   ```
   DB_NAME=seenit
   DB_USER=seenitadmin
   DB_PASSWORD=password
   DB_HOST=127.0.0.1
   DB_PORT=5432
   SECRET_KEY='{your generated secret key}'
   ```
6. To migrate models to DB: In seenit directory
   ```
   python manage.py makemigrations
   python manage.py migrate
   ```
7. To seed database (you can change thread_count and root_comments):
   ```
   python manage.py seed --thread_count=50 --root_comments=50
   ```
8. To start server:
   ```
   python manage.py runserver
   ```
9. Got to http://localhost:8000

10. To run tests: In seenit directory
    ```
    python manage.py test seenit.tests
    ``` 
