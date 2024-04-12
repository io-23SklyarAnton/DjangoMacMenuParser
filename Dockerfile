# syntax=docker/dockerfile:1

# Use the specified Python version as the base image
ARG PYTHON_VERSION=3.11.3
FROM python:${PYTHON_VERSION}-slim as base

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set the working directory
WORKDIR /app

# Create a non-privileged user that the app will run under
ARG UID=10001
RUN adduser \
    --disabled-password \
    --gecos "" \
    --home "/nonexistent" \
    --shell "/usr/sbin/nologin" \
    --no-create-home \
    --uid "${UID}" \
    appuser

# Download dependencies from requirements.txt
RUN --mount=type=cache,target=/root/.cache/pip \
    --mount=type=bind,source=requirements.txt,target=requirements.txt \
    python -m pip install -r requirements.txt

# Create static and media directories
RUN mkdir -p /app/static /app/media

# Switch to the non-privileged user to run the application
USER appuser

# Copy the source code into the container
COPY . .

# Expose the port that the application listens on
EXPOSE 8001

# Run the application
CMD ["python", "manage.py", "runserver"]
