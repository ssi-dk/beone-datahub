# Introduction
BeONE Web App is the core web application for the BeONE project. It this point it is not intended for production use, but can only be used for testing and feedback.

# Installation prerequisites
BeONE web app runs trough Docker, so you will need Docker in your computer in order to install it. Please see the Docker documentation for your platform.

# Installation
Check out this repository on your computer.

cd to the installation folder and type:

    docker compose up

When Docker has downloaded and initialized the containers you should see someting like:

Starting development server at http://0.0.0.0:8000/

That address will probably not work. Use this address instead to se the user interface in a browser:

http://localhost:8000/

# Create a user
Open another terminal window (while the containers are still running in the first one) and type:

    docker exec beone_web_app-web-1 python manage.py migrate

This should produce som text output but no error messages.

Then type in the same terminal window:

    docker exec -it beone_web_app-web-1 python manage.py createsuperuser

Enter user information at the prompts.

You should now be able to login to the web application with the provided username and password.