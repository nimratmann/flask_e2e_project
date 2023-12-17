# flask_e2e_project

This is a full-stack medication tracker application built with Python (Flask) for the backend and Tailwind CSS for the frontend. The inspiration behind this application is to address the issue of individuals forgetting to complete their prescribed medication dosages.

The Medication Tracker provides users with real-time visibility into their prescription progress and allows them to track details about the prescribing doctoras well




## Technologies Utilized

1. GitHub: Employed for version control of the project scripts.
2. Environment Variables (.env): Used to store credentials for Google OAuth and database connection strings, particularly for MySQL connection.
3. Flask: Chosen as the backend framework to develop the web-service project, enabling the creation of a Flask app.
4. Tailwind: Employed as the frontend framework to design the web-service interface.
5. Azure Database for MySQL flexible server: Selected as the project's database to integrate data seamlessly into the Flask app.
6. SQLAlchemy: Utilized as the Object-Relational Mapping (ORM) tool within the Flask app, facilitating the establishment of a connection with the MySQL database and enabling data querying.
7. Google OAuth: Integrated as the authorization service in the project to implement straightforward user authorization within the Flask app.
8. Docker: Incorporated into the project to containerize the Flask app, streamlining deployment and ensuring consistency across different environments.
9. Cloud Deployment with Azure: Utilized Microsoft Azure's App Services to deploy the Flask app to the cloud, providing an alternative method for deploying the web application.


## Environment Variables (.env) Configuration

In this project, environment variables played a crucial role in storing credentials for both Google OAuth and MySQL database connections. The .env file structure in the repository adhered to the following template:

- GOOGLE_CLIENT_ID = "client-id"
- GOOGLE_CLIENT_SECRET = "client-secret"
- DB_HOST = "azure-host-link"
- DB_DATABASE = "database-name"
- DB_USERNAME = "username"
- DB_PASSWORD = "password"
- DB_PORT = 3306

This organized structure allowed for easy management and secure storage of sensitive information, facilitating seamless integration with the MySQL database and enabling secure communication with Google OAuth services within the project.

## Running the Application Locally

### 1. Clone the Repository

Clone the repository to your local machine:

### 2. Install and configure tailwind

#### run the following commands to set up Tailwind CSS:
1. run "npm init -y" to create a package.json file
2. run "npm i tailwindcss" to install tailwind
3. run "npx tailwindcss init" to initialize tailwind
4. Change the content section of the file such that the final tailwind.config.js looks something like this:

    content: ["./app/templates/.html", "./app/static/src/.js"],

5. Create "input.css" file inside css folder under static folder and add the following:

    @tailwind base;
    @tailwind components;
    @tailwind utilities;

6. Create an alias in the package.json inorder to listen to new tailwind changes i.e

    "buildcss": "npx tailwindcss -i ./static/css/input.css -o ./static/css/output.css --watch"

### 3.Install flask packages

     Run "pip install -r requirements.txt"

### 4.Setup the Environmental variables

### 5.Run "env\scripts\activate" to activate your environmental variables

### 6. Run "python app.py" to start the project.


## Deploying using Docker and Docker Compose

1. Ensure Docker and Docker Compose are on your local machine

2. Create a .env file in the same directory as your docker-compose.yml file. Populate it with the required environment variables, including DB_USERNAME, DB_PASSWORD, DOCKER_DB_HOST, DB_NAME, etc.

3. Place the DigiCertGlobalRootCA.crt.pem file in the ./app directory.

4. Open a terminal, and navigate to the directory containing your docker-compose.yml file.

5. Run the following command to build and start the services

`docker-compose up --build`

6. Access your Flask application at http://localhost:5000. The application should be connected to the MySQL database.


## Deploying Application on Azure

