/**
 * Simple Calculator Module
 * 
 * This module provides basic mathematical operations for testing MCP server generation.
 * Functions are designed with different complexity levels and parameter patterns.
 */

/**
 * Add two numbers together.
 * 
 * A simple addition function that demonstrates basic MCP tool functionality
 * with required parameters and straightforward return value.
 * 
 * @param {number} a - First number to add
 * @param {number} b - Second number to add
 * @returns {number} Sum of a and b
 * @example
 * addNumbers(2, 3) // returns 5
 * addNumbers(-1, 1) // returns 0
 */
export function addNumbers(a, b) {
    return a + b;
}

/**
 * Calculate base raised to the power of exponent.
 * 
 * Demonstrates optional parameters with default values and more complex
 * mathematical operations. Good for testing parameter handling.
 * 
 * @param {number} base - The base number
 * @param {number} exponent - The power to raise base to (default: 2)
 * @returns {number} Result of base^exponent
 * @example
 * calculatePower(3) // returns 9
 * calculatePower(2, 3) // returns 8
 */
export function calculatePower(base, exponent = 2) {
    return Math.pow(base, exponent);
}

/**
 * Calculate factorial of a non-negative integer.
 * 
 * Includes input validation and error handling to test how generated
 * MCP servers handle exceptions and edge cases.
 * 
 * @param {number} n - Non-negative integer to calculate factorial for
 * @returns {number} Factorial of n
 * @throws {Error} If n is negative
 * @example
 * factorial(5) // returns 120
 * factorial(0) // returns 1
 */
export function factorial(n) {
    if (n < 0) {
        throw new Error("Factorial is not defined for negative numbers");
    }
    if (n === 0 || n === 1) {
        return 1;
    }
    return n * factorial(n - 1);
}

/**
 * Calculate the area of a circle given its radius.
 * 
 * Uses mathematical constants and demonstrates scientific calculations
 * that might be useful as MCP tools.
 * 
 * @param {number} radius - Radius of the circle (must be positive)
 * @returns {number} Area of the circle
 * @throws {Error} If radius is negative
 * @example
 * calculateCircleArea(1) // returns ~3.14
 * calculateCircleArea(2) // returns ~12.57
 */
export function calculateCircleArea(radius) {
    if (radius < 0) {
        throw new Error("Radius cannot be negative");
    }
    return Math.PI * radius * radius;
}

/**
 * Solve quadratic equation ax² + bx + c = 0.
 * 
 * Returns complex results and demonstrates handling of multiple return values
 * in a structured format. Tests how MCP servers handle object returns.
 * 
 * @param {number} a - Coefficient of x² (cannot be 0)
 * @param {number} b - Coefficient of x
 * @param {number} c - Constant term
 * @returns {Object} Object with solutions and discriminant info
 * @throws {Error} If a is 0 (not a quadratic equation)
 * @example
 * solveQuadratic(1, -3, 2) // returns {discriminant: 1, solutions: [2, 1], type: 'real'}
 */
export function solveQuadratic(a, b, c) {
    if (a === 0) {
        throw new Error("Coefficient 'a' cannot be zero for quadratic equation");
    }
    
    const discriminant = b * b - 4 * a * c;
    
    if (discriminant > 0) {
        const sqrtDiscriminant = Math.sqrt(discriminant);
        const x1 = (-b + sqrtDiscriminant) / (2 * a);
        const x2 = (-b - sqrtDiscriminant) / (2 * a);
        return {
            discriminant: discriminant,
            solutions: [x1, x2],
            type: "real"
        };
    } else if (discriminant === 0) {
        const x = -b / (2 * a);
        return {
            discriminant: discriminant,
            solutions: [x],
            type: "repeated"
        };
    } else {
        const realPart = -b / (2 * a);
        const imaginaryPart = Math.sqrt(-discriminant) / (2 * a);
        return {
            discriminant: discriminant,
            solutions: [
                {real: realPart, imaginary: imaginaryPart},
                {real: realPart, imaginary: -imaginaryPart}
            ],
            type: "complex"
        };
    }
}