# Use the official Python 3.7 Alpine image as the base image
FROM python:3.7-alpine

# Set the working directory to /app in the container
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Install the Python dependencies specified in requirements.txt
RUN pip install -r requirements.txt

# Expose port 5000 to the outside world, allowing external access to your application
EXPOSE 5000

# Define the default command to run when the container starts
CMD ["python", "app.py"]