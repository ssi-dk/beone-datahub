# Introduction
BeONE Web App is the core web application for the BeONE project. It this point it is not intended for production use, but can be used for testing and feedback.

# Installation prerequisites

## Docker
BeONE web app runs trough Docker, so you will need Docker on your computer in order to install it. Please see the Docker documentation for your platform. On Windows, the recommended way of running Docker is through Windows Subsystem for Linux (WSL) version 2. The application is being developed and tested with Ubuntu 20.02 on top of WSL2.

## MongoDB
In order to use BeONE Web App you must have access to a running instance of a MongoDB database that contains a BeONE data structure. At least for now, a read-only account for the MongoDB database will be sufficient as BeONE Web App will not write any data to the MongoDB database. If you don't have a MongoDB database already, see the paragraph 'Installing a local MongoDB'.

## Optional: install a tool for viewing MongoDB data
During the testing process it can sometimes be desirable to be able to view the MongoDB data in another way separate from the web app. For this purpose, the MongoDB Compass data viewer can be recommended. Please see MongoDB website for hos to download and install MongoDB Compass.

## A note about PostgreSQL
BeONE Web App also uses a PostgreSQL database for storing user accounts and other user-related data. The PostgreSQL database is provided through the Docker infrastructure, so having a PostgreSQL database is NOT a prerequisite.

# Installing a local MongoDB
If you do not already have a MongoDB database that you can use for testing the BeONE Web App, you can install MongoDB on your local machine. For development, a MongoDB 3.6 provided by the Ubuntu repositories is being used. Although this version is very old, it is currently sufficient for testing. You can install it in Ubuntu 20.04 with this command:

    sudo apt install mongodb

You will also need to start it by running:

    sudo service start mongodb

## Load test data into MongoDB
There is a small test data set included in the repository. It can be installed with the 'mongoimport' utility program that comes with MongoDB. The test data set consists of 10 JSON files, each containing data for one sample. However, 'mongoimport' can only import one file at a time. To make it less cumbersome (assuming you are running Ubuntu or another Linux OS), you should be able to install all the data with one command this way:

    cd test_data
    cat *.json | mongoimport -d beone –c samples

If you installed Compass, you can use it to verify that you now have a database named 'beone' with a collection named 'samples' which contains the samples from the test dataset.

# Installation
If you havn't done so already, check out this repository on your computer.

## Configure MONGO_CONNECTION

The URI for the MongoDB database is controlled by the MONGO_CONNECTION variable in settings.py. The following setting (which is the default) will connect to a MongoDB server instance running in the host OS and use a database named 'beone' for both authentication and data:

    MONGO_CONNECTION = 'mongodb://host.docker.internal:27017/beone'

Note that since settings.py is a version-controlled file Git will see it as a code change if you make a change to it. This is not optimal and will be changed later.

If you need to authenticate the MongoDB user through another database than the one that stores the data, can specify the authentication database this way:

    MONGO_CONNECTION = 'mongodb://host.docker.internal:27017/beone?authSource=auth_db'

## Build and run the Docker containers

cd to the installation folder and type:

    docker compose up

When Docker has finished downloading images and building and starting the containers you should see someting like:

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