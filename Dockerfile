# Use a lightweight Python base image
FROM python:3.10-slim

# Set the working directory inside the container
WORKDIR /app

# Copy only the requirements first to leverage Docker caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy the rest of the project files into the container
COPY . .

# Expose the port that Chainlit will run on (default is 8000)
EXPOSE 8000

# Run Chainlit on port 8000 and listen on all interfaces
CMD ["chainlit", "run", "src/main.py", "--host", "0.0.0.0", "--port", "8000"]
