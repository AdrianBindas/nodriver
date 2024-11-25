# Use the official Python 3.12 image from the Docker Hub
FROM python:3.12-slim

# Install Chrome and its dependencies
RUN apt-get update && \
    apt-get install -y wget gnupg && \
    wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | apt-key add - && \
    sh -c 'echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" > /etc/apt/sources.list.d/google-chrome.list' && \
    apt-get update && \
    apt-get install -y google-chrome-stable && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Install git
RUN apt-get update && \
    apt-get upgrade -y && \
    apt-get install -y git && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Set the working directory
WORKDIR /app

# Copy the local files to the container
COPY . /app

# Install the required Python package
RUN pip install uv

# Add github to known hosts
RUN ssh-keyscan -t rsa github.com >> ~/.ssh/known_hosts

# Run the sync command
RUN --mount=type=ssh uv sync --verbose

# Set the entrypoint to run the main script
ENTRYPOINT ["uv", "run", "./src/main.py"]
