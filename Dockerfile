# Use an official Python runtime as a parent image
FROM python:latest

# Set the working directory in the container
WORKDIR /app

# Install poetry
RUN pip install poetry

# Copy the poetry configuration files into the container at /app
COPY pyproject.toml poetry.lock* /app/

# Configure Poetry:
# - Do not create a virtual environment within the Docker container
# - Install production dependencies only
RUN poetry config virtualenvs.create false \
    && poetry install 

# Copy the rest of your application into the container at /app
COPY . /app
RUN chmod +x scrape.sh
# Run the application
CMD ["./scrape.sh"]
