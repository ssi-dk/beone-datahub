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

    docker compose up

When Docker has finished downloading images and building and starting the containers, go to this address in a browser:

http://localhost:8080/

Open another terminal window (while the containers are still running in the first one) and type the following to generate the table structure in PostgreSQL:

    docker exec beone_web_app-django-1 python manage.py migrate

This should produce som text output but no error messages.

Then type in the same terminal window to create a user that can login to the web app:

    docker exec -it beone_web_app-django-1 python manage.py createsuperuser

Enter user information at the prompts.

You should now be able to login to the web application with the provided username and password.

## Load test data into MongoDB
There is a small test dataset included in the repository. The test dataset consists of a number of JSON files, each containing fake/anonymized data for one sample. The dataset can be installed this way:

    docker exec -it beone_web_app-mongo-1 bash
    cd /mnt/test_data
    cat *.json | mongoimport -d beone -c samples
    exit

After this step, you should be able to see the samples in the 'sample list' in the UI (however, the fields 'Organization' and 'Name' will be empty).

## Add extra database keys and a unique index
Every organization that deals with sample data normally has internal rules and systems that ensures the uniqeness of sample names. However, the BeONE Web App - as well as the BeONE project itself - is about sharing data between organizations. This implies that there must be a way of ensuring the uniqueness of the samples so as to avoid that samples from two organizations are mixed up because the have the same sample name. Assuming that all samples received from a certain organization has unique names, we can solve the problem simply by adding a couple of extra keys and a unique index. This is not a part of the original BeONE MongoDB schema specification, so adding the keys and the index requires an extra step after importing the test data:

    docker exec -it beone_web_app-django-1 python manage.py addids TEST

This command will:
    - add an 'org' field with the value 'TEST' to each sample
    - Copy the field sample.summary.sample to a new 'name' field at the root level (as MongoDB cannot index non-root fields)
    - Ceate a unique index on these two fields

After this step, the fields 'Organization' and 'Name' in the UI should be filled.