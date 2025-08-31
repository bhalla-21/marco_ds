# This is a multi-stage Dockerfile for a full-stack application
# with a React frontend and a Python backend.

# --- Stage 1: Build the React Frontend ---
# Use an official Node.js image to build the frontend assets.
FROM node:18-alpine AS frontend_builder

# Set a working directory for the frontend build. This ensures a clean
# and predictable environment.
WORKDIR /app/frontend

# Copy everything from the repository root into this directory.
# This ensures that all necessary files, including package.json,
# src, and public, are available for the build process.
COPY . .

# Install Node.js dependencies.
RUN npm install

# Build the React application for production.
RUN npm run build

# --- Stage 2: Build and Run the Python Backend ---
# Use a Python image to serve the backend and the static frontend files.
FROM python:3.9-slim-buster

# Set the working directory for the backend.
WORKDIR /app/backend

# Copy the Python requirements file from the repository root.
COPY ../requirements.txt ./

# Install Python dependencies from the requirements file, and also install
# gunicorn to run the server and whitenoise to serve the static frontend files.
RUN pip install --no-cache-dir -r requirements.txt gunicorn whitenoise

# Copy the backend application code.
COPY ./app ./app

# Copy the built frontend assets from the previous stage into the static directory of the backend.
# The `build` folder from the frontend builder stage contains the static files.
COPY --from=frontend_builder /app/frontend/build ./app/public

# Expose the port that the app will run on.
EXPOSE 8000

# The command to start the application using Gunicorn.
# It binds to 0.0.0.0 and uses the port provided by Render.
# The app is located at backend/app/main.py and the entry point is the `app` object.
# Assumes your Python code is configured to serve the static files from the `public` directory.
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "app.main:app"]
