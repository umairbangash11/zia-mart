# # Use an official Python runtime as a parent image
# FROM python:3.12

# LABEL maintainer="ameen-alam"
# # Set the working directory in the container
# WORKDIR /code
# # Install system dependencies required for potential Python packages
# RUN apt-get update && apt-get install -y \
#     build-essential \
#     libpq-dev \
#     protobuf-compiler \
#     && rm -rf /var/lib/apt/lists/*

# # Copy requirements first to leverage Docker cache
# COPY pyproject.toml poetry.lock* ./

# # Install Python dependencies
# RUN pip install --no-cache-dir -r requirements.txt

# # Copy the rest of the application
# COPY . /code/

# # Make port 8000 available to the world outside this container
# EXPOSE 8000

# # Run the application
# CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--reload"]

FROM python:3.12
WORKDIR /code
RUN apt-get update && apt-get install -y build-essential libpq-dev protobuf-compiler && rm -rf /var/lib/apt/lists/*
RUN pip install --no-cache-dir poetry
COPY pyproject.toml poetry.lock* ./
RUN poetry config virtualenvs.create false && poetry install --without dev
RUN pip install --no-cache-dir protobuf==5.29.0
COPY . .
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]