# Dockerfile for a custom n8n image with pipx for persistent Python packages

# Use the official n8n image as the base
FROM n8nio/n8n:1.103.0

# Switch to the root user to install necessary system packages
USER root

# Update package lists and install python3 and python3-pip
RUN apk update && apk add --no-cache \
    python3 \
    py3-pip \
    git \
    curl \
    jq && \
    # Clean up the apk cache
    rm -rf /var/cache/apk/*

# Install npm packages globally
RUN npm install -g \
    axios \
    lodash \
    lodash \
    ytdl-core \
    jsonata \
    @types/node \
    async && \
    npm cache clean --force

# Switch back to the non-root 'node' user for security
USER node

# Create the n8n nodes directory if it doesn't exist
# This is where custom n8n nodes will be installed
RUN mkdir -p ~/.n8n/nodes
RUN cd ~/.n8n/nodes && npm i n8n-nodes-document-generator
RUN cd ~/.n8n/nodes && npm i n8n-nodes-text-manipulation

# Install pipx using pip
# We use --no-cache-dir to minimize layer size
RUN pip install --no-cache-dir --user --break-system-packages pipx google-genai markdown-it-py docling

# Set environment variables for pipx
# PIPX_HOME is where pipx stores its virtual environments and other data.
ENV PIPX_HOME=/home/node/.pipx
# PIPX_BIN_DIR is where the executables for apps installed by pipx are placed.
ENV PIPX_BIN_DIR=/home/node/.local/bin

# Add the pipx bin directory to the system's PATH
# This ensures that any command-line tools installed via pipx can be found and executed by n8n.
ENV PATH="$PATH:${PIPX_BIN_DIR}"
