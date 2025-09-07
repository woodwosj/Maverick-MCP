/**
 * Risky Operations Module
 * 
 * This module contains potentially dangerous operations for testing security
 * classification in MCP server generation. These functions should be flagged
 * as high or medium risk by the security analyzer.
 */

import { execSync } from 'child_process';
import fs from 'fs';
import path from 'path';

/**
 * Execute a shell command (HIGH RISK).
 * 
 * This function executes arbitrary shell commands, which presents
 * significant security risks and should be flagged by security analysis.
 * 
 * @param {string} command - Shell command to execute
 * @param {Object} options - Execution options
 * @returns {string} Command output
 * @example
 * executeCommand("ls -la") // Lists directory contents
 */
export function executeCommand(command, options = {}) {
    try {
        const result = execSync(command, {
            encoding: 'utf8',
            timeout: options.timeout || 5000,
            maxBuffer: options.maxBuffer || 1024 * 1024,
            ...options
        });
        return result.toString();
    } catch (error) {
        throw new Error(`Command execution failed: ${error.message}`);
    }
}

/**
 * Write content to a file (HIGH RISK).
 * 
 * File system write operations can be dangerous as they can overwrite
 * important files or create security vulnerabilities.
 * 
 * @param {string} filePath - Path to the file to write
 * @param {string} content - Content to write to the file
 * @param {Object} options - Write options
 * @returns {string} Success message
 * @example
 * writeToFile("/tmp/test.txt", "Hello World")
 */
export function writeToFile(filePath, content, options = {}) {
    try {
        // Basic path validation to prevent some attacks
        if (filePath.includes('..') || !path.isAbsolute(filePath)) {
            throw new Error("Invalid file path: must be absolute and not contain '..'");
        }
        
        fs.writeFileSync(filePath, content, {
            encoding: options.encoding || 'utf8',
            mode: options.mode || 0o644,
            ...options
        });
        
        return `Successfully wrote ${content.length} characters to ${filePath}`;
    } catch (error) {
        throw new Error(`File write failed: ${error.message}`);
    }
}

/**
 * Read sensitive file content (MEDIUM RISK).
 * 
 * Reading files can expose sensitive information and should be
 * used with caution in MCP servers.
 * 
 * @param {string} filePath - Path to the file to read
 * @param {Object} options - Read options
 * @returns {string} File content
 * @example
 * const content = readSensitiveFile("/etc/passwd") // Dangerous!
 */
export function readSensitiveFile(filePath, options = {}) {
    try {
        // Basic security check (still not comprehensive)
        const sensitivePatterns = ['/etc/passwd', '/etc/shadow', '.ssh/id_rsa'];
        if (sensitivePatterns.some(pattern => filePath.includes(pattern))) {
            console.warn(`Warning: Attempting to read potentially sensitive file: ${filePath}`);
        }
        
        const content = fs.readFileSync(filePath, {
            encoding: options.encoding || 'utf8',
            ...options
        });
        
        return content;
    } catch (error) {
        throw new Error(`File read failed: ${error.message}`);
    }
}

/**
 * Make HTTP request to external service (MEDIUM RISK).
 * 
 * External network requests can be used for data exfiltration
 * or to communicate with malicious services.
 * 
 * @param {string} url - URL to make request to
 * @param {Object} options - Request options
 * @returns {Promise<Object>} Response data
 * @example
 * const response = await makeHttpRequest("http://example.com/api")
 */
export async function makeHttpRequest(url, options = {}) {
    try {
        // In a real implementation, this might use axios or fetch
        // For this mock, we'll simulate the behavior
        
        console.warn(`Making HTTP request to: ${url}`);
        
        // Simulate network delay
        await new Promise(resolve => setTimeout(resolve, Math.random() * 1000 + 500));
        
        // Check for suspicious URLs
        const suspiciousPatterns = ['localhost', '127.0.0.1', '192.168.', '10.0.'];
        if (suspiciousPatterns.some(pattern => url.includes(pattern))) {
            console.warn(`Warning: Request to potentially internal/local address: ${url}`);
        }
        
        return {
            url: url,
            status: 200,
            method: options.method || 'GET',
            timestamp: new Date().toISOString(),
            data: `Mock response from ${url}`
        };
    } catch (error) {
        throw new Error(`HTTP request failed: ${error.message}`);
    }
}

/**
 * Evaluate JavaScript code dynamically (HIGH RISK).
 * 
 * Using eval() or Function() constructor to execute arbitrary code
 * is extremely dangerous and should always be flagged as high risk.
 * 
 * @param {string} code - JavaScript code to evaluate
 * @param {Object} context - Context object for code execution
 * @returns {any} Result of code evaluation
 * @example
 * evaluateCode("2 + 2") // returns 4 (but very dangerous!)
 */
export function evaluateCode(code, context = {}) {
    console.warn("WARNING: Dynamic code evaluation is extremely dangerous!");
    
    try {
        // This is intentionally dangerous for testing security detection
        // In real applications, this should NEVER be done
        const func = new Function('context', `
            with(context) {
                return ${code};
            }
        `);
        
        return func(context);
    } catch (error) {
        throw new Error(`Code evaluation failed: ${error.message}`);
    }
}

/**
 * Delete files or directories (HIGH RISK).
 * 
 * File system deletion operations are extremely dangerous and can
 * cause permanent data loss.
 * 
 * @param {string} targetPath - Path to delete
 * @param {Object} options - Deletion options
 * @returns {string} Success message
 * @example
 * deleteFileOrDirectory("/tmp/test.txt") // Deletes the file
 */
export function deleteFileOrDirectory(targetPath, options = {}) {
    try {
        // Basic safety checks (still not comprehensive)
        const protectedPaths = ['/', '/home', '/etc', '/usr', '/var'];
        if (protectedPaths.includes(targetPath) || targetPath.length < 5) {
            throw new Error(`Refusing to delete protected or suspicious path: ${targetPath}`);
        }
        
        const stats = fs.statSync(targetPath);
        
        if (stats.isDirectory()) {
            if (options.recursive) {
                fs.rmSync(targetPath, { recursive: true, force: true });
                return `Directory ${targetPath} deleted recursively`;
            } else {
                fs.rmdirSync(targetPath);
                return `Directory ${targetPath} deleted`;
            }
        } else {
            fs.unlinkSync(targetPath);
            return `File ${targetPath} deleted`;
        }
    } catch (error) {
        throw new Error(`Deletion failed: ${error.message}`);
    }
}