# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

ENV TRAEFIK_HOST=traefik
ENV TRAEFIK_PORT=8080
#these will be checked in the main.py file
ENV CF_ZONE_ID=''
ENV CF_API_KEY=''
ENV EXTRA_DOMAINS=''


# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir requests

# Run main.py when the container launches
CMD ["python", "main.py"]
