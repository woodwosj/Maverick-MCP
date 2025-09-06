FROM node:18-alpine

WORKDIR /app

# Install dependencies
RUN npm init -y && \
    npm install @modelcontextprotocol/sdk axios cheerio

# Copy server implementation
COPY server.js .

# Set environment
ENV NODE_ENV=production

# Run the MCP server
CMD ["node", "server.js"]