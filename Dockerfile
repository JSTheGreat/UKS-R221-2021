# Use an official Python runtime as a parent image
FROM python:3.8-slim-buster

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set the working directory to /app
WORKDIR /app

# Copy the requirements file to the container
COPY requirements.txt /app/

RUN pip install --upgrade pip
RUN pip uninstall psycopg2
RUN pip install --upgrade wheel
RUN pip install --upgrade setuptools

# Install any needed packages specified in requirements.txt
RUN pip install -r requirements.txt

# Copy the rest of the application code to the container

COPY ./scripts/wait-for-postgres.sh /usr/local/bin/wait-for-postgres.sh
RUN chmod +x /usr/local/bin/wait-for-postgres.sh
RUN apt-get update && apt-get install -y dos2unix
RUN dos2unix /usr/local/bin/wait-for-postgres.sh

CMD ["wait-for-postgres.sh"]

COPY ./scripts/start-django.sh /usr/local/bin/start-django.sh
RUN chmod +x /usr/local/bin/start-django.sh
RUN dos2unix /usr/local/bin/start-django.sh

CMD ["start-django.sh"]

COPY . /app/