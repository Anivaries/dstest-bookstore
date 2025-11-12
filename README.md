A Bookstore application

How to run:
1. Cd to directory and activate venv ```python3 -m venv venv```
2. Clone the repo ```git clone https://github.com/Anivaries/dstest-bookstore.git```
3. Activate venv linux:```source venv/bin/activate``` or windows:```venv/scripts/activate``` 
4. cd into folder with requirements and run ```pip install -r requirements.txt```
5. Enter postgres terminal ```psql -U postgres``` and create a database ```CREATEA DATABASE bookstore;```
    bookstore is the name of the database we use in our django project
    5a. open settings.py file and update username and password for your database 
    ```python
    DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'bookstore',
        'USER': 'postgres',
        'PASSWORD': 'password',
        'HOST': '127.0.0.1',
        'PORT': 5432,
        }
    }
    ```
6. Run migrations: CD to where ```manage.py``` file is and run ```python manage.py migrate```. This will populate the database with our tables from ```models.py``` file
7. 