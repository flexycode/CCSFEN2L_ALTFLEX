FROM python:3.10-slim

# Install basic tools
RUN apt-get update && apt-get install -y \
    git \
    curl \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Create user
RUN useradd -m -s /bin/bash vscode

# Set working directory
WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Switch to user
USER vscode
