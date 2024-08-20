# Use an official Python runtime as a parent image
FROM python:3.10-slim

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Install the base dependencies that do not cause conflicts
RUN pip install --no-cache-dir -r app/requirements.txt

# Install specific versions of the conflicting packages
RUN pip install --no-cache-dir -r app/conflict-requirements.txt

# Ensure the .env file is copied into the container (if using environment variables)
COPY .env /app/.env

# Expose the port that Chainlit will run on
EXPOSE 8000

# Command to run your application
CMD ["chainlit", "run", "app/main.py", "--host", "0.0.0.0", "--port", "8000"]