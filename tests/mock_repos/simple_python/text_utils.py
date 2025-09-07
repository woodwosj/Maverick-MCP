"""
Text Utility Functions

Provides string manipulation and text processing functions for testing
MCP server generation with different parameter types and security levels.
"""

import re
import hashlib
from typing import List, Optional


def reverse_string(text: str) -> str:
    """
    Reverse a string.
    
    Simple string manipulation function for basic MCP tool testing.
    
    Args:
        text: String to reverse
        
    Returns:
        Reversed string
        
    Examples:
        >>> reverse_string("hello")
        'olleh'
        >>> reverse_string("Python")
        'nohtyP'
    """
    return text[::-1]


def count_words(text: str, case_sensitive: bool = False) -> dict:
    """
    Count word frequency in text.
    
    Demonstrates text analysis with optional parameters and structured
    return values. Good for testing complex data handling.
    
    Args:
        text: Text to analyze
        case_sensitive: Whether to treat words case-sensitively
        
    Returns:
        Dictionary with word counts and statistics
        
    Examples:
        >>> result = count_words("Hello world hello")
        >>> result['total_words']
        3
    """
    if not case_sensitive:
        text = text.lower()
    
    # Split on whitespace and remove empty strings
    words = [word.strip('.,!?";:()[]{}') for word in text.split() if word.strip()]
    words = [word for word in words if word]  # Remove empty after stripping
    
    word_counts = {}
    for word in words:
        word_counts[word] = word_counts.get(word, 0) + 1
    
    return {
        "word_counts": word_counts,
        "total_words": len(words),
        "unique_words": len(word_counts),
        "most_common": max(word_counts.items(), key=lambda x: x[1]) if word_counts else None
    }


def extract_emails(text: str) -> List[str]:
    """
    Extract email addresses from text using regex.
    
    Demonstrates regex usage and list return values. Tests how MCP servers
    handle complex string processing and array returns.
    
    Args:
        text: Text to search for email addresses
        
    Returns:
        List of found email addresses
        
    Examples:
        >>> extract_emails("Contact: john@example.com or admin@test.org")
        ['john@example.com', 'admin@test.org']
    """
    email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    return re.findall(email_pattern, text)


def generate_hash(text: str, algorithm: str = "sha256") -> str:
    """
    Generate cryptographic hash of text.
    
    SECURITY NOTE: This function involves cryptographic operations which
    should be flagged by security scanner as medium risk due to potential
    misuse in sensitive contexts.
    
    Args:
        text: Text to hash
        algorithm: Hash algorithm (md5, sha1, sha256, sha512)
        
    Returns:
        Hexadecimal hash string
        
    Raises:
        ValueError: If algorithm is not supported
        
    Examples:
        >>> len(generate_hash("test"))
        64  # SHA256 produces 64 character hex string
    """
    algorithms = {
        'md5': hashlib.md5,
        'sha1': hashlib.sha1,
        'sha256': hashlib.sha256,
        'sha512': hashlib.sha512
    }
    
    if algorithm not in algorithms:
        raise ValueError(f"Unsupported algorithm: {algorithm}")
    
    return algorithms[algorithm](text.encode('utf-8')).hexdigest()


def format_template(template: str, variables: dict) -> str:
    """
    Format a string template with variables.
    
    Demonstrates template processing with dictionary parameters.
    Tests complex parameter handling and string formatting.
    
    Args:
        template: Template string with {variable} placeholders
        variables: Dictionary of variables to substitute
        
    Returns:
        Formatted string with variables substituted
        
    Examples:
        >>> format_template("Hello {name}!", {"name": "World"})
        'Hello World!'
    """
    try:
        return template.format(**variables)
    except KeyError as e:
        raise ValueError(f"Missing variable in template: {e}")


def validate_phone_number(phone: str, country_code: str = "US") -> dict:
    """
    Validate phone number format for different countries.
    
    Complex validation logic that demonstrates conditional processing
    and structured validation results.
    
    Args:
        phone: Phone number to validate
        country_code: Country code for format validation
        
    Returns:
        Dictionary with validation results
        
    Examples:
        >>> result = validate_phone_number("(555) 123-4567")
        >>> result['valid']
        True
    """
    # Clean phone number
    cleaned = re.sub(r'[^\d]', '', phone)
    
    patterns = {
        'US': (r'^\d{10}$', 10),
        'UK': (r'^\d{10,11}$', (10, 11)),
        'DE': (r'^\d{10,12}$', (10, 11, 12))
    }
    
    if country_code not in patterns:
        return {
            "valid": False,
            "reason": f"Unsupported country code: {country_code}",
            "cleaned": cleaned
        }
    
    pattern, expected_length = patterns[country_code]
    
    if isinstance(expected_length, tuple):
        length_valid = len(cleaned) in expected_length
    else:
        length_valid = len(cleaned) == expected_length
    
    pattern_valid = bool(re.match(pattern, cleaned))
    
    return {
        "valid": length_valid and pattern_valid,
        "cleaned": cleaned,
        "original_length": len(phone),
        "cleaned_length": len(cleaned),
        "country_code": country_code,
        "reason": "Valid" if (length_valid and pattern_valid) else "Invalid format"
    }