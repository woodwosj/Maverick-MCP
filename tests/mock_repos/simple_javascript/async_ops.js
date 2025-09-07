/**
 * Async Operations Module
 * 
 * This module provides asynchronous functions for testing MCP server generation.
 * Includes Promise-based operations, async/await patterns, and error handling.
 */

/**
 * Simulate an async delay operation.
 * 
 * Returns a promise that resolves after the specified delay.
 * Useful for testing async MCP tool behavior and timing operations.
 * 
 * @param {number} ms - Milliseconds to delay (default: 1000)
 * @returns {Promise<string>} Promise that resolves with a success message
 * @example
 * await delay(500) // waits 500ms then returns "Delay completed: 500ms"
 */
export async function delay(ms = 1000) {
    return new Promise((resolve) => {
        setTimeout(() => {
            resolve(`Delay completed: ${ms}ms`);
        }, ms);
    });
}

/**
 * Fetch data from a mock API endpoint.
 * 
 * Simulates an HTTP request with random success/failure for testing
 * error handling and network operations in MCP servers.
 * 
 * @param {string} url - URL to fetch from
 * @param {number} timeout - Request timeout in ms (default: 5000)
 * @returns {Promise<Object>} Promise that resolves with mock data or rejects
 * @example
 * const data = await fetchMockData("https://api.example.com/users")
 */
export async function fetchMockData(url, timeout = 5000) {
    return new Promise((resolve, reject) => {
        // Simulate network delay
        const networkDelay = Math.random() * 1000 + 500;
        
        setTimeout(() => {
            // Simulate random success/failure (80% success rate)
            if (Math.random() < 0.8) {
                resolve({
                    url: url,
                    status: 200,
                    data: {
                        id: Math.floor(Math.random() * 1000),
                        timestamp: new Date().toISOString(),
                        message: "Mock data retrieved successfully"
                    }
                });
            } else {
                reject(new Error(`Failed to fetch data from ${url}: Network error`));
            }
        }, Math.min(networkDelay, timeout));
        
        // Handle timeout
        setTimeout(() => {
            reject(new Error(`Request timeout: ${url} took longer than ${timeout}ms`));
        }, timeout);
    });
}

/**
 * Process an array of items asynchronously.
 * 
 * Processes items with a delay, demonstrating async iteration
 * and batch processing patterns for MCP tools.
 * 
 * @param {Array} items - Array of items to process
 * @param {number} delayMs - Delay between processing each item (default: 100)
 * @returns {Promise<Array>} Promise that resolves with processed items
 * @example
 * const result = await processItemsAsync([1, 2, 3], 200)
 */
export async function processItemsAsync(items, delayMs = 100) {
    if (!Array.isArray(items)) {
        throw new Error("Items must be an array");
    }
    
    const results = [];
    
    for (let i = 0; i < items.length; i++) {
        const item = items[i];
        
        // Simulate async processing
        await new Promise(resolve => setTimeout(resolve, delayMs));
        
        results.push({
            index: i,
            original: item,
            processed: `processed_${item}`,
            timestamp: new Date().toISOString()
        });
    }
    
    return results;
}

/**
 * Retry an async operation with exponential backoff.
 * 
 * Attempts an operation multiple times with increasing delays between attempts.
 * Demonstrates advanced async patterns and error recovery strategies.
 * 
 * @param {Function} operation - Async function to retry
 * @param {number} maxAttempts - Maximum number of attempts (default: 3)
 * @param {number} baseDelay - Base delay in ms (default: 1000)
 * @returns {Promise<any>} Promise that resolves with operation result
 * @example
 * const result = await retryOperation(async () => fetchMockData("/api/data"), 3, 500)
 */
export async function retryOperation(operation, maxAttempts = 3, baseDelay = 1000) {
    if (typeof operation !== 'function') {
        throw new Error("Operation must be a function");
    }
    
    let lastError;
    
    for (let attempt = 1; attempt <= maxAttempts; attempt++) {
        try {
            const result = await operation();
            return {
                success: true,
                result: result,
                attempts: attempt
            };
        } catch (error) {
            lastError = error;
            
            if (attempt === maxAttempts) {
                break; // Don't wait after the last attempt
            }
            
            // Exponential backoff: delay increases with each attempt
            const delay = baseDelay * Math.pow(2, attempt - 1);
            await new Promise(resolve => setTimeout(resolve, delay));
        }
    }
    
    throw new Error(`Operation failed after ${maxAttempts} attempts. Last error: ${lastError.message}`);
}