This is a project in Python using PostgreSQL and Celery integrated into Django for an easy to use website interface.

If you would like to run this server on your local host follow these steps:

1) git clone this repo into your text editor

2) On the front page of this repo, copy the requirements.txt file into your project and download it

      a) need to download apache2 for modwsgi, 
        
        brew install postgresql
        brew install apache2
        pip install -r requirements.txt 
               
3) Create a 'frontend_config.py' file for our settings.py file in Website_Settings, of form

       Django = {
           "Key": '',
       }

       PostgreSQL = {
           "UserName": "",
           "Password": "",
           "Name": "",
           "Host": "",
           "Port": ,
       }
        
4) Go into the DDI directory

        cd DDI_Website

5) Then once the above steps are completed, you now run in order in the terminal:

        python manage.py makemigrations
        python manage.py migrate
        python manage.py runserver // For just the regular server (for testing purposes)
        OR  
        python manage.py runmodwsgi // Runs on Apache (final server)

6) Then create a new terminal instance while still in DDI_Website folder

        if windows 10:
            pip install gevent 
            celery -A Website_Settings worker -l info -P gevent
        if macOS:
            celery -A Website_Settings worker -l info

    note: This will let you run your tasks in the background using Celery


7) Finally, start the File Server to help deliver the files to the webserver by going to the File_Server folder and running:

        python server.py

Now the website is fully functional!
Just register a new user and enjoy :)

Author:

      - Hedayat Tabesh
      - Elsa Donovan
      - Pranav Sood
      - Jonathan Silveira
