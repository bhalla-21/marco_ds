# Stage 1: Build the React frontend
FROM node:18-alpine AS frontend-builder

# Set the working directory for the frontend code
WORKDIR /app

# Copy package.json and package-lock.json first to leverage Docker's layer caching
COPY package*.json ./

# Install frontend dependencies
RUN npm install

# Copy the rest of the frontend source code
COPY . ./

# Build the optimized production assets
RUN npm run build

# Stage 2: Create the final production image
FROM python:3.9-slim-buster

# Set the working directory for the backend
WORKDIR /app

# Copy the backend requirements file and install Python dependencies
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the backend application code
COPY backend/ .

# Copy the built frontend assets from the previous stage
COPY --from=frontend-builder /app/build /app/static

# Expose the port
EXPOSE 8000

# Command to run the application
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "app.main:app"]
