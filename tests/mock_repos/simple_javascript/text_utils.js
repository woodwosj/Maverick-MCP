/**
 * Text Utilities Module
 * 
 * This module provides text processing functions for testing MCP server generation.
 * Includes string manipulation, formatting, and analysis functions.
 */

/**
 * Convert text to title case.
 * 
 * Capitalizes the first letter of each word while making other letters lowercase.
 * Handles edge cases with special characters and multiple spaces.
 * 
 * @param {string} text - Text to convert to title case
 * @returns {string} Title case version of the text
 * @example
 * toTitleCase("hello world") // returns "Hello World"
 * toTitleCase("HELLO WORLD") // returns "Hello World"
 */
export function toTitleCase(text) {
    if (!text || typeof text !== 'string') {
        return '';
    }
    
    return text.toLowerCase().replace(/\b\w/g, char => char.toUpperCase());
}

/**
 * Count words in a text string.
 * 
 * Counts words separated by whitespace, handling multiple spaces and
 * edge cases. Useful for text analysis and content management.
 * 
 * @param {string} text - Text to count words in
 * @returns {number} Number of words in the text
 * @example
 * countWords("Hello world") // returns 2
 * countWords("  Hello   world  ") // returns 2
 */
export function countWords(text) {
    if (!text || typeof text !== 'string') {
        return 0;
    }
    
    return text.trim().split(/\s+/).filter(word => word.length > 0).length;
}

/**
 * Remove all whitespace from a string.
 * 
 * Strips all spaces, tabs, newlines, and other whitespace characters.
 * Useful for data cleaning and normalization tasks.
 * 
 * @param {string} text - Text to remove whitespace from
 * @returns {string} Text with all whitespace removed
 * @example
 * removeWhitespace("Hello World") // returns "HelloWorld"
 * removeWhitespace("  H e l l o  ") // returns "Hello"
 */
export function removeWhitespace(text) {
    if (!text || typeof text !== 'string') {
        return '';
    }
    
    return text.replace(/\s/g, '');
}

/**
 * Check if a string is a palindrome.
 * 
 * Case-insensitive palindrome check that ignores spaces and punctuation.
 * Demonstrates string analysis and boolean return values.
 * 
 * @param {string} text - Text to check for palindrome
 * @returns {boolean} True if text is a palindrome, false otherwise
 * @example
 * isPalindrome("racecar") // returns true
 * isPalindrome("A man a plan a canal Panama") // returns true
 */
export function isPalindrome(text) {
    if (!text || typeof text !== 'string') {
        return false;
    }
    
    // Remove non-alphanumeric characters and convert to lowercase
    const cleaned = text.replace(/[^a-zA-Z0-9]/g, '').toLowerCase();
    const reversed = cleaned.split('').reverse().join('');
    
    return cleaned === reversed;
}

/**
 * Generate a URL slug from text.
 * 
 * Converts text to lowercase, replaces spaces with hyphens,
 * and removes special characters. Useful for SEO and URL generation.
 * 
 * @param {string} text - Text to convert to slug
 * @returns {string} URL-friendly slug
 * @example
 * generateSlug("Hello World!") // returns "hello-world"
 * generateSlug("JavaScript & TypeScript") // returns "javascript-typescript"
 */
export function generateSlug(text) {
    if (!text || typeof text !== 'string') {
        return '';
    }
    
    return text
        .toLowerCase()
        .trim()
        .replace(/[^a-z0-9\s-]/g, '') // Remove special characters
        .replace(/\s+/g, '-') // Replace spaces with hyphens
        .replace(/-+/g, '-') // Replace multiple hyphens with single
        .replace(/^-|-$/g, ''); // Remove leading/trailing hyphens
}

/**
 * Truncate text to specified length with ellipsis.
 * 
 * Safely truncates text without breaking words, adding ellipsis when needed.
 * Demonstrates optional parameters and string manipulation.
 * 
 * @param {string} text - Text to truncate
 * @param {number} maxLength - Maximum length of result (default: 100)
 * @param {string} suffix - Suffix to add when truncated (default: "...")
 * @returns {string} Truncated text with suffix if needed
 * @example
 * truncateText("This is a long sentence", 10) // returns "This is a..."
 */
export function truncateText(text, maxLength = 100, suffix = '...') {
    if (!text || typeof text !== 'string') {
        return '';
    }
    
    if (text.length <= maxLength) {
        return text;
    }
    
    // Find the last space within the limit to avoid breaking words
    const truncated = text.substring(0, maxLength - suffix.length);
    const lastSpace = truncated.lastIndexOf(' ');
    
    if (lastSpace > 0) {
        return truncated.substring(0, lastSpace) + suffix;
    }
    
    return truncated + suffix;
}