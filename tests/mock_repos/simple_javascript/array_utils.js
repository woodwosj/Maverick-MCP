/**
 * Array Utilities Module
 * 
 * This module provides array manipulation and analysis functions
 * for testing MCP server generation with various data types and patterns.
 */

/**
 * Find unique elements in an array.
 * 
 * Returns a new array with duplicate elements removed,
 * preserving the order of first occurrence.
 * 
 * @param {Array} arr - Input array
 * @returns {Array} Array with unique elements
 * @example
 * findUnique([1, 2, 2, 3, 1]) // returns [1, 2, 3]
 */
export function findUnique(arr) {
    if (!Array.isArray(arr)) {
        throw new Error("Input must be an array");
    }
    
    return [...new Set(arr)];
}

/**
 * Group array elements by a specified property.
 * 
 * Groups objects in an array by a specified property value,
 * useful for data organization and analysis.
 * 
 * @param {Array} arr - Array of objects to group
 * @param {string} property - Property name to group by
 * @returns {Object} Object with grouped elements
 * @example
 * groupBy([{type: 'A', val: 1}, {type: 'B', val: 2}], 'type')
 */
export function groupBy(arr, property) {
    if (!Array.isArray(arr)) {
        throw new Error("Input must be an array");
    }
    
    return arr.reduce((groups, item) => {
        const key = item[property];
        if (!groups[key]) {
            groups[key] = [];
        }
        groups[key].push(item);
        return groups;
    }, {});
}

/**
 * Calculate statistical summary of numeric array.
 * 
 * Returns min, max, mean, median, and standard deviation
 * for numeric data analysis.
 * 
 * @param {Array<number>} numbers - Array of numbers
 * @returns {Object} Statistical summary object
 * @example
 * calculateStats([1, 2, 3, 4, 5]) // returns {min: 1, max: 5, mean: 3, ...}
 */
export function calculateStats(numbers) {
    if (!Array.isArray(numbers) || numbers.length === 0) {
        throw new Error("Input must be a non-empty array");
    }
    
    const numericValues = numbers.filter(n => typeof n === 'number' && !isNaN(n));
    if (numericValues.length === 0) {
        throw new Error("Array must contain at least one valid number");
    }
    
    const sorted = [...numericValues].sort((a, b) => a - b);
    const min = sorted[0];
    const max = sorted[sorted.length - 1];
    const mean = numericValues.reduce((sum, n) => sum + n, 0) / numericValues.length;
    
    // Calculate median
    const mid = Math.floor(sorted.length / 2);
    const median = sorted.length % 2 === 0 
        ? (sorted[mid - 1] + sorted[mid]) / 2 
        : sorted[mid];
    
    // Calculate standard deviation
    const variance = numericValues.reduce((sum, n) => sum + Math.pow(n - mean, 2), 0) / numericValues.length;
    const standardDeviation = Math.sqrt(variance);
    
    return {
        count: numericValues.length,
        min,
        max,
        mean: Math.round(mean * 100) / 100,
        median,
        standardDeviation: Math.round(standardDeviation * 100) / 100
    };
}

/**
 * Chunk array into smaller arrays of specified size.
 * 
 * Splits an array into multiple smaller arrays of the given size,
 * useful for batch processing and pagination.
 * 
 * @param {Array} arr - Array to chunk
 * @param {number} size - Size of each chunk
 * @returns {Array<Array>} Array of chunked arrays
 * @example
 * chunkArray([1, 2, 3, 4, 5], 2) // returns [[1, 2], [3, 4], [5]]
 */
export function chunkArray(arr, size) {
    if (!Array.isArray(arr)) {
        throw new Error("Input must be an array");
    }
    
    if (!Number.isInteger(size) || size <= 0) {
        throw new Error("Chunk size must be a positive integer");
    }
    
    const chunks = [];
    for (let i = 0; i < arr.length; i += size) {
        chunks.push(arr.slice(i, i + size));
    }
    
    return chunks;
}