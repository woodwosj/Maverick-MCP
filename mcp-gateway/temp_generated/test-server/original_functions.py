"""\nOriginal functions extracted from repository\n"""\n\n# Function: process_csv_data\n# File: /home/loomworks3/MCP Library/mcp-gateway/tests/test_data/sample_functions.py\n# Line: 12\n\ndef process_csv_data(csv_path: str, clean_nulls: bool = True) -> pd.DataFrame:
    """
    Process CSV data and return cleaned results
    
    This function reads a CSV file, optionally cleans null values,
    and returns a pandas DataFrame with the processed data.
    
    Args:
        csv_path: Path to the CSV file to process
        clean_nulls: Whether to remove null values (default: True)
        
    Returns:
        Processed pandas DataFrame
    """
    df = pd.read_csv(csv_path)
    
    if clean_nulls:
        df = df.dropna()
    
    return df\n\n# Function: fetch_user_data\n# File: /home/loomworks3/MCP Library/mcp-gateway/tests/test_data/sample_functions.py\n# Line: 34\n\ndef fetch_user_data(api_url: str, user_id: int, timeout: int = 30) -> Dict:
    """
    Fetch user data from REST API
    
    Makes a GET request to retrieve user information from the specified API.
    
    Args:
        api_url: Base URL of the API  
        user_id: Unique identifier for the user
        timeout: Request timeout in seconds
        
    Returns:
        Dictionary containing user data
    """
    response = requests.get(f"{api_url}/users/{user_id}", timeout=timeout)
    response.raise_for_status()
    return response.json()\n\n# Function: validate_email\n# File: /home/loomworks3/MCP Library/mcp-gateway/tests/test_data/sample_functions.py\n# Line: 53\n\ndef validate_email(email: str) -> bool:
    """
    Validate email address format
    
    Simple email validation using basic regex pattern.
    
    Args:
        email: Email address to validate
        
    Returns:
        True if email format is valid, False otherwise
    """
    import re
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))\n\n# Function: calculate_compound_interest\n# File: /home/loomworks3/MCP Library/mcp-gateway/tests/test_data/sample_functions.py\n# Line: 70\n\ndef calculate_compound_interest(principal: float, rate: float, time: float, n: int = 1) -> float:
    """
    Calculate compound interest
    
    Uses the compound interest formula: A = P(1 + r/n)^(nt)
    
    Args:
        principal: Initial amount of money
        rate: Annual interest rate (as decimal, e.g. 0.05 for 5%)
        time: Time period in years
        n: Number of times interest is compounded per year
        
    Returns:
        Final amount after compound interest
    """
    amount = principal * (1 + rate / n) ** (n * time)
    return round(amount, 2)\n\n# Function: transform_json_data\n# File: /home/loomworks3/MCP Library/mcp-gateway/tests/test_data/sample_functions.py\n# Line: 125\n\n    def transform_json_data(self, json_data: str, format_type: str = "compact") -> Dict:
        """
        Transform JSON data to different formats
        
        Parses JSON string and reformats it according to the specified type.
        
        Args:
            json_data: JSON string to transform
            format_type: Type of formatting (compact, pretty, minified)
            
        Returns:
            Transformed data as dictionary
        """
        data = json.loads(json_data)
        
        if format_type == "compact":
            return {k: v for k, v in data.items() if v is not None}
        elif format_type == "pretty":
            return data
        else:
            return data\n\n# Function: async_function_example\n# File: /home/loomworks3/MCP Library/mcp-gateway/tests/test_data/sample_functions.py\n# Line: 160\n\nasync def async_function_example(url: str) -> str:
    """
    Async function example for testing async support
    
    Args:
        url: URL to fetch
        
    Returns:
        Response content as string
    """
    # This would normally use aiohttp or similar
    return f"Async result from {url}"\n\n# Function: dangerous_file_operation\n# File: /home/loomworks3/MCP Library/mcp-gateway/tests/test_data/sample_functions.py\n# Line: 94\n\ndef dangerous_file_operation(file_path: str):
    """
    This function performs dangerous file operations
    
    WARNING: This function has security issues and should be flagged
    """
    import os
    import subprocess
    
    # Dangerous patterns that should be detected
    os.system(f"rm -rf {file_path}")  # System command execution
    subprocess.call(["cat", file_path], shell=True)  # Shell execution
    
    with open("/etc/passwd", "r") as f:  # Absolute path access
        return f.read()\n\n# Function: function_with_complex_types\n# File: /home/loomworks3/MCP Library/mcp-gateway/tests/test_data/sample_functions.py\n# Line: 152\n\ndef function_with_complex_types(data: List[Dict[str, Optional[int]]]) -> Optional[List[str]]:
    """Function with complex type hints to test type parsing"""
    if not data:
        return None
    
    return [str(item.get("key", "")) for item in data if item]\n\n