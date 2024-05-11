# Use an official Python runtime as a parent image
FROM python:latest

# Set the working directory in the container
WORKDIR /app


# Install system dependencies required for Python and handling of .env files
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*




# Install poetry
RUN pip install poetry

# Copy only the files necessary for poetry to install dependencies
COPY pyproject.toml poetry.lock* /app/

# Configure Poetry
# - Do not create a virtual environment within the Docker container
# - Install production dependencies only
RUN poetry config virtualenvs.create false \
    && poetry install --no-dev --no-interaction --no-ansi

# Copy the .env file from your host to the container
# Make sure you include the .env file in your .dockerignore if it contains sensitive data
COPY .env /app/
COPY . /app


RUN chmod +x /app/scrape.sh


# Run the application
CMD ["/bin/bash", "-c", "/app/scrape.sh"]
