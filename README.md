# Introduction
BeONE Web App is the core web application for the BeONE project. At this point it is not intended for production use, but can be used for testing and feedback.

# Installation prerequisites

## Docker
BeONE web app runs trough Docker, so you will need Docker on your computer in order to install it. Please see the Docker documentation for your platform. On Windows, the recommended way of running Docker is through Windows Subsystem for Linux (WSL) version 2. The application is being developed and tested with Ubuntu 20.02 on top of WSL2.

## Optional: install a tool for viewing MongoDB data
During the testing process it can sometimes be desirable to be able to view the MongoDB data in another way separate from the web app. For this purpose, the MongoDB Compass data viewer can be recommended. Please see MongoDB website for hos to download and install MongoDB Compass.

# Installation
If you haven't done so already, check out this repository on your computer (in Windows, do this on a Linux instance under WSL2).

'cd' to the installation directory.

In the installation directory, type:

    git submodule update --init --recursive
    export DOCKER_BUILDKIT=0 (on Mac: DOCKER_BUILDKIT=0)
    docker compose up

When Docker has finished downloading images and building and starting the containers, go to this address in a browser:

http://localhost:8080/

Open another terminal window (while the containers are still running in the first one) and type the following to generate the table structure in PostgreSQL:

    docker exec beone-datahub_django_1 python manage.py migrate

This should produce som text output but no error messages.

Then type in the same terminal window to create a user that can login to the web app:

    docker exec -it beone-datahub_django_1 python manage.py createsuperuser

Enter user information at the prompts.

Finally, type:

    docker exec -it beone-datahub_django_1 python manage.py loaddata dumps/group.json

You should now be able to login to the web application with the provided username and password.
