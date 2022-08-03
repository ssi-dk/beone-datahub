# Introduction
BeONE Web App is the core web application for the BeONE project. It this point it is not intended for production use, but can be used for testing and feedback.

# Installation prerequisites

## Docker
BeONE web app runs trough Docker, so you will need Docker on your computer in order to install it. Please see the Docker documentation for your platform. On Windows, the recommended way of running Docker is through Windows Subsystem for Linux (WSL) version 2. The application is being developed and tested with Ubuntu 20.02 on top of WSL2.

## MongoDB
In order to use BeONE Web App you must have access to a running instance of a MongoDB database that contains a BeONE data structure. At least for now, a read-only account for the MongoDB database will be sufficient as BeONE Web App will not write any data to the MongoDB database.

### Install a local MongoDB on Ubuntu
If you do not already have a MongoDB database that you can use for testing the BeONE Web App, you can install MongoDB on your local machine. For development, a MongoDB 3.6 provided by the Ubuntu repositories is being used. Although this version is very old, it is currently sufficient for testing. You can install it in Ubuntu 20.04 with thic command:

    sudo apt install mongodb

You will also need to start it by running:

    sudo service start mongodb

### Load test data into MongoDB
Todo.

### Configure MONGO_CONNECTION
Set the database URI in the MONGO_CONNECTION variable in settings.py. The following setting will connect to a MongoDB server instance running in the host OS and use a database named 'beone' for both authentication and data:

    MONGO_CONNECTION = 'mongodb://host.docker.internal:27017/beone'

If you need to authenticate the MongoDB user through another database than the one that stores the data, you need to specify the auth database this way:

    MONGO_CONNECTION = 'mongodb://host.docker.internal:27017/beone?authSource=auth_db'

Note that since this change is made in a version-controlled file Git will see it as a code change. This is not optimal and will be changed later.

### Optional: install a tool for viewing MongoDB data
During the testing process it can sometimes be desirable to be able to view the MongoDB data in another way separate from the web app. For this purpose, the MongoDB Compass data viewer can be recommended. Please see MongoDB website for hos to download and install MongoDB Compass.

# A note about PostgreSQL
BeONE Web App also uses a PostgreSQL database for storing user accounts and other user-related data. The PostgreSQL database is provided through the Docker infrastructure, so having a PostgreSQL database is NOT a prerequisite.

# Installation
Check out this repository on your computer.

cd to the installation folder and type:

    docker compose up

When Docker has downloaded and initialized the containers you should see someting like:

Starting development server at http://0.0.0.0:8000/

That address will probably not work. Use this address instead to see the user interface in a browser:

http://localhost:8000/

Open another terminal window (while the containers are still running in the first one) and type the following to generate the table structure in PostgreSQL:

    docker exec beone_web_app-web-1 python manage.py migrate

This should produce som text output but no error messages.

Then type in the same terminal window to create a user that can login to the web app:

    docker exec -it beone_web_app-web-1 python manage.py createsuperuser

Enter user information at the prompts.

You should now be able to login to the web application with the provided username and password.