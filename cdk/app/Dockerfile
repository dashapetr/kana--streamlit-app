# Use an official lightweight Python image
FROM python:3.11-slim

# Set the working directory in the container
WORKDIR /app

# Copy the app files into the container
COPY . .

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    wget \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt huggingface-hub

# Expose Streamlit port
EXPOSE 8501

# Command to run the app
CMD ["streamlit", "run", "init_streamlit_app.py", "--server.port=8501", "--server.address=0.0.0.0"]
