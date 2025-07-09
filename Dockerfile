# Dockerfile for a custom n8n image with pipx for persistent Python packages

# Use the official n8n image as the base
FROM n8nio/n8n

# Switch to the root user to install necessary system packages
USER root

# Update package lists and install python3 and python3-pip
# --no-install-recommends reduces the image size
RUN apt-get update && apt-get install -y --no-install-recommends python3 python3-pip && \
    # Clean up the apt cache to keep the image lean
    rm -rf /var/lib/apt/lists/*

# Switch back to the non-root 'node' user for security
USER node

# Install pipx using pip
# We use --no-cache-dir to minimize layer size
RUN pip install --no-cache-dir pipx

# Set environment variables for pipx
# PIPX_HOME is where pipx stores its virtual environments and other data.
ENV PIPX_HOME=/home/node/.pipx
# PIPX_BIN_DIR is where the executables for apps installed by pipx are placed.
ENV PIPX_BIN_DIR=/home/node/.local/bin

# Add the pipx bin directory to the system's PATH
# This ensures that any command-line tools installed via pipx can be found and executed by n8n.
ENV PATH="$PATH:${PIPX_BIN_DIR}"
