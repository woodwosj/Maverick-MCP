FROM node:18-alpine

WORKDIR /app

# Copy package.json
COPY package.json .

# Install the official Context7 package
RUN npm install

# Set environment
ENV NODE_ENV=production

# Accept API key as build argument and environment variable
ARG CONTEXT7_API_KEY
ENV CONTEXT7_API_KEY=${CONTEXT7_API_KEY}

# Run the official Context7 MCP server
CMD ["npx", "-y", "@upstash/context7-mcp"]