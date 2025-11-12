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
7. Now, for this part, files which i use to populate the database are too large for github so they can be downloaded here: http://88.99.170.77:8000/export/. Files being used for this are: ADD FILES PATHS.
    7a. Put these files in the project directory. I use working_files/ folder for this
8. CD to where ```manage.py``` file is and run ```python3 manage.py load_data --books_file path_to/BX-Books-cleaned_new.csv --ratings_file path_to/BX-Books-clean-ratings_new.csv```. This will populate the database with books and ratings.
9. Now, these files are not completely clean, there is one step i used to clean files in django, which is: ```python3 manage.py fix_title_quotes```. There were some leftover quotes from csv escaping double quotes. This command fixes it by fetching names from openlibrary api. 

Now we have populated, clean database.

10. Run ```python3 manage.py runserver``` to run the application
    10a. Run ```python3 manage.py createsuperuser``` if you want to have access to django admin dashboard, but it's not necessary