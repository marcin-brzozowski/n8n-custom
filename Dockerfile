# Use a base image with ARM support
FROM node:22-bullseye
ARG N8N_VERSION=1.103.0

# Install build dependencies
# Python and build tools (make, g++) might be needed for building some npm packages
RUN apt-get update && apt-get install -y curl python3 python3-pip jq

# Install additional dependencies
RUN pip3 install --no-cache-dir \
        pipx==1.7.1 \
        google-genai==1.26.0 \
        markdown-it-py==3.0.0 \
        duckling

# Install n8n globally
RUN npm install n8n@${N8N_VERSION} -g

# Install problematic npm packages with --force
RUN npm install -g --force \
    markdown-it@14.1.0

# Install additional npm packages globally
RUN npm install -g \
    axios \
    lodash \
    lodash \
    ytdl-core \
    jsonata \
    @types/node \
    async && \
    npm cache clean --force



# Switch to the node user
USER node

# Create a directory for n8n data
RUN mkdir /home/node/.n8n

# Set the ownership of the n8n data directory to the node user
RUN chown -R node:node /home/node/.n8n

RUN mkdir -p ~/.n8n/nodes
RUN cd ~/.n8n/nodes && npm i n8n-nodes-document-generator@1.0.10
RUN cd ~/.n8n/nodes && npm i n8n-nodes-text-manipulation@1.4.0

# PIPX_HOME is where pipx stores its virtual environments and other data.
ENV PIPX_HOME=/home/node/.pipx
# PIPX_BIN_DIR is where the executables for apps installed by pipx are placed.
ENV PIPX_BIN_DIR=/home/node/.local/bin

# Add the pipx bin directory to the system's PATH
# This ensures that any command-line tools installed via pipx can be found and executed by n8n.
ENV PATH="$PATH:${PIPX_BIN_DIR}"

# Expose the n8n port
EXPOSE 5678

# Start n8n
CMD ["n8n"]