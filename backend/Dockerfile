# Use an official Python runtime as a parent image
FROM python:3.6-stretch

# Set the working directory to /app
WORKDIR /usr/src/app

# Copy requirements.txt to working directory
ADD requirements.txt /usr/src/app

# Install any needed packages specified in requirements.txt
RUN pip install --trusted-host pypi.python.org -r requirements.txt

# Make port 8888 available to the world outside this container
EXPOSE 8888

# Run app_2.py when the container launches
CMD ["python", "app_2.py"]

