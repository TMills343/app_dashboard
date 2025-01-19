# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Install dependencies
RUN apt-get update && \
    apt-get install -y libheif-dev && \
    apt-get clean

# Set the working directory in the container
WORKDIR /usr/src/app

ARG FLASK_DEBUG
ENV FLASK_DEBUG=${FLASK_DEBUG:-1}

# Set environment variables
ENV FLASK_APP=app.py
ENV FLASK_RUN_HOST=0.0.0.0
ENV FLASK_ENV=development

# Install any needed packages specified in requirements.txt
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy the current directory contents into the container at /usr/src/app
COPY . .

# Make port 2390 available to the world outside this container
EXPOSE 2390

# Define environment variable
ENV NAME World

# Run app.py when the container launches
CMD ["flask", "run"]
