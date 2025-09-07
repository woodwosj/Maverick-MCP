"""
Simple Calculator Module

This module provides basic mathematical operations for testing MCP server generation.
Functions are designed with different complexity levels and parameter patterns.
"""

import math
from typing import Optional, Union


def add_numbers(a: float, b: float) -> float:
    """
    Add two numbers together.
    
    A simple addition function that demonstrates basic MCP tool functionality
    with required parameters and straightforward return value.
    
    Args:
        a: First number to add
        b: Second number to add
        
    Returns:
        Sum of a and b
        
    Examples:
        >>> add_numbers(2, 3)
        5.0
        >>> add_numbers(-1, 1)
        0.0
    """
    return a + b


def calculate_power(base: float, exponent: float = 2.0) -> float:
    """
    Calculate base raised to the power of exponent.
    
    Demonstrates optional parameters with default values and more complex
    mathematical operations. Good for testing parameter handling.
    
    Args:
        base: The base number
        exponent: The power to raise base to (default: 2.0)
        
    Returns:
        Result of base^exponent
        
    Examples:
        >>> calculate_power(3)
        9.0
        >>> calculate_power(2, 3)
        8.0
    """
    return math.pow(base, exponent)


def factorial(n: int) -> int:
    """
    Calculate factorial of a non-negative integer.
    
    Includes input validation and error handling to test how generated
    MCP servers handle exceptions and edge cases.
    
    Args:
        n: Non-negative integer to calculate factorial for
        
    Returns:
        Factorial of n
        
    Raises:
        ValueError: If n is negative
        
    Examples:
        >>> factorial(5)
        120
        >>> factorial(0)
        1
    """
    if n < 0:
        raise ValueError("Factorial is not defined for negative numbers")
    if n == 0 or n == 1:
        return 1
    return n * factorial(n - 1)


def calculate_circle_area(radius: float) -> float:
    """
    Calculate the area of a circle given its radius.
    
    Uses mathematical constants and demonstrates scientific calculations
    that might be useful as MCP tools.
    
    Args:
        radius: Radius of the circle (must be positive)
        
    Returns:
        Area of the circle
        
    Raises:
        ValueError: If radius is negative
        
    Examples:
        >>> round(calculate_circle_area(1), 2)
        3.14
        >>> round(calculate_circle_area(2), 2)
        12.57
    """
    if radius < 0:
        raise ValueError("Radius cannot be negative")
    return math.pi * radius * radius


def solve_quadratic(a: float, b: float, c: float) -> dict:
    """
    Solve quadratic equation ax² + bx + c = 0.
    
    Returns complex results and demonstrates handling of multiple return values
    in a structured format. Tests how MCP servers handle dict returns.
    
    Args:
        a: Coefficient of x² (cannot be 0)
        b: Coefficient of x
        c: Constant term
        
    Returns:
        Dictionary with solutions and discriminant info
        
    Raises:
        ValueError: If a is 0 (not a quadratic equation)
        
    Examples:
        >>> solve_quadratic(1, -3, 2)
        {'discriminant': 1.0, 'solutions': [2.0, 1.0], 'type': 'real'}
    """
    if a == 0:
        raise ValueError("Coefficient 'a' cannot be zero for quadratic equation")
    
    discriminant = b * b - 4 * a * c
    
    if discriminant > 0:
        sqrt_discriminant = math.sqrt(discriminant)
        x1 = (-b + sqrt_discriminant) / (2 * a)
        x2 = (-b - sqrt_discriminant) / (2 * a)
        return {
            "discriminant": discriminant,
            "solutions": [x1, x2],
            "type": "real"
        }
    elif discriminant == 0:
        x = -b / (2 * a)
        return {
            "discriminant": discriminant,
            "solutions": [x],
            "type": "repeated"
        }
    else:
        real_part = -b / (2 * a)
        imaginary_part = math.sqrt(-discriminant) / (2 * a)
        return {
            "discriminant": discriminant,
            "solutions": [
                {"real": real_part, "imaginary": imaginary_part},
                {"real": real_part, "imaginary": -imaginary_part}
            ],
            "type": "complex"
        }