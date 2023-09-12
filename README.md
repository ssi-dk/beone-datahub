# Installation prerequisites

BeONE web app runs trough Docker, so you will need Docker on your computer in order to install it. Please see the Docker documentation for your platform. On Windows, the recommended way of running Docker is through Windows Subsystem for Linux (WSL) version 2. The application is being developed and tested with Ubuntu 20.02 on top of WSL2.

# Installation

## Build the dashboard server
The dashboard server is not on Docker Hub yet, so the container has to be built manually following these instructions.
    
    git clone git@github.com:ssi-dk/dashboard_server.git
    cd dashboard_server
    docker build -t dashboard_server .

After this step, your Docker instance has an image of the dashboard server that can be used in the following step.

## Build rest of the the Docker environment

If you haven't done so already, check out this repository on your computer (in Windows, do this on a Linux instance under WSL2).

'cd' to the installation directory.

In the installation directory, type:

    git submodule update --init --recursive
    export DOCKER_BUILDKIT=0 (on Mac: DOCKER_BUILDKIT=0)
    docker compose up

## Initialize the Django environment
Open another terminal window (while the containers are still running in the first one) and type the following to create a shell in the Django container:

    docker exec -it beone-datahub-django-1 bash

Type the following commands in this shell.

Generate the table structure in PostgreSQL:

    python manage.py migrate

This should produce som text output but no error messages.

Create a user that can login to the web app:

    python manage.py createsuperuser

Enter user information at the prompts.

To create some dummy data, type:

    python manage.py createfakedata --count 20

You should now be able to login to the web application at:

http://localhost:8000/

You should be able to login with the username and password you provided.

You can then exit the Django shell.

## Get an access token from Microreact

In a terminal go to the folder 'comparison_backend' and type:

    cp settings_local.template.py settings_local.py

Open the created file, settings_local.py, in an editor.

Now point your web browser to the dashboard:

http://localhost:3000/

Login with username adminuser1. Password is 'password'. The user will be logged in via a dummy LDAP server. At first login, a user instance will be created in MongoDB in a collection named 'users'.

Go to the users' account settings:

http://localhost:3000/my-account/settings

Copy the access token to the field MICROREACT_ACCESS_TOKEN in settings_local.py.

It should now be possible to create Microreact projects programmatically using the main web interface in the prototype.

If you at any point experience problems with creating projects programmatically, try to:
- Logout from Microreact and log back in (using 'adminuser1' and 'password')
- Go to the account settings, copy the new token, and paste it in settings_local.py