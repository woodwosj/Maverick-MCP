#!/usr/bin/env node

/**
 * Context7 MCP Server - Simplified version for demonstration
 * Provides documentation retrieval capabilities
 */

import { Server } from '@modelcontextprotocol/sdk/server/index.js';
import { StdioServerTransport } from '@modelcontextprotocol/sdk/server/stdio.js';
import axios from 'axios';

class Context7Server {
  constructor() {
    this.server = new Server(
      {
        name: "context7-server",
        version: "1.0.0",
      },
      {
        capabilities: {
          tools: {},
        },
      }
    );

    this.setupHandlers();
  }

  setupHandlers() {
    // List available tools
    this.server.setRequestHandler('tools/list', async () => {
      return {
        tools: [
          {
            name: "get_documentation",
            description: "Fetch up-to-date documentation for programming libraries",
            inputSchema: {
              type: "object",
              properties: {
                library: {
                  type: "string",
                  description: "Name of the library to get documentation for"
                },
                version: {
                  type: "string",
                  description: "Specific version (optional)"
                },
                topic: {
                  type: "string", 
                  description: "Specific topic or function to focus on (optional)"
                }
              },
              required: ["library"]
            }
          },
          {
            name: "search_code_examples",
            description: "Search for code examples and usage patterns",
            inputSchema: {
              type: "object",
              properties: {
                library: {
                  type: "string",
                  description: "Library name"
                },
                query: {
                  type: "string",
                  description: "Search query for specific functionality"
                }
              },
              required: ["library", "query"]
            }
          }
        ]
      };
    });

    // Handle tool calls
    this.server.setRequestHandler('tools/call', async (request) => {
      const { name, arguments: args } = request.params;

      try {
        switch (name) {
          case "get_documentation":
            return await this.getDocumentation(args);
          case "search_code_examples":
            return await this.searchCodeExamples(args);
          default:
            throw new Error(`Unknown tool: ${name}`);
        }
      } catch (error) {
        return {
          content: [
            {
              type: "text",
              text: `Error executing tool ${name}: ${error.message}`
            }
          ],
          isError: true
        };
      }
    });
  }

  async getDocumentation(args) {
    const { library, version, topic } = args;
    
    // Simplified documentation fetching
    // In real implementation, this would fetch from official docs, npm, etc.
    const docUrl = this.buildDocumentationUrl(library, version, topic);
    
    try {
      const response = await axios.get(docUrl, { timeout: 10000 });
      
      return {
        content: [
          {
            type: "text",
            text: `Documentation for ${library}${version ? ` v${version}` : ''}${topic ? ` - ${topic}` : ''}:\n\n${this.extractRelevantContent(response.data, topic)}`
          }
        ]
      };
    } catch (error) {
      // Fallback to general information
      return {
        content: [
          {
            type: "text", 
            text: `Documentation lookup for ${library}: Unable to fetch live documentation. This would typically return current API docs, installation instructions, and usage examples for ${library}.`
          }
        ]
      };
    }
  }

  async searchCodeExamples(args) {
    const { library, query } = args;
    
    // Simplified code example search
    // In real implementation, would search GitHub, Stack Overflow, etc.
    const searchResults = await this.performCodeSearch(library, query);
    
    return {
      content: [
        {
          type: "text",
          text: `Code examples for ${library} - ${query}:\n\n${searchResults}`
        }
      ]
    };
  }

  buildDocumentationUrl(library, version, topic) {
    // Build URL for documentation source
    // This is simplified - real implementation would handle multiple doc sources
    const baseUrls = {
      'react': 'https://reactjs.org/docs',
      'nodejs': 'https://nodejs.org/api',
      'express': 'https://expressjs.com/en/api',
      'fastapi': 'https://fastapi.tiangolo.com',
    };
    
    const baseUrl = baseUrls[library.toLowerCase()] || `https://www.npmjs.com/package/${library}`;
    return baseUrl;
  }

  extractRelevantContent(htmlContent, topic) {
    // Simplified content extraction
    // Real implementation would parse HTML and extract relevant sections
    if (topic) {
      return `Relevant content for "${topic}" would be extracted and returned here. This includes API reference, examples, and usage patterns.`;
    }
    
    return "General documentation content would be extracted and formatted here, including installation, basic usage, and key concepts.";
  }

  async performCodeSearch(library, query) {
    // Simplified code search
    // Real implementation would search multiple sources
    return `Example code snippets for "${query}" in ${library}:

\`\`\`javascript
// Example usage of ${library} for ${query}
// This would contain actual working code examples
// fetched from GitHub, documentation, or Stack Overflow
\`\`\`

Additional examples and patterns would be included here.`;
  }

  async run() {
    const transport = new StdioServerTransport();
    await this.server.connect(transport);
    console.error("Context7 MCP server running on stdio");
  }
}

const server = new Context7Server();
server.run().catch(console.error);