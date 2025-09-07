# Simple Python Test Repository

This repository contains Python functions designed to test the Maverick-MCP repository conversion pipeline.

## Modules

### calculator.py
Mathematical operations with varying complexity:
- `add_numbers()` - Simple addition (safe, high MCP score)
- `calculate_power()` - Power calculations with optional parameters
- `factorial()` - Recursive function with error handling
- `calculate_circle_area()` - Uses mathematical constants
- `solve_quadratic()` - Complex return values with structured data

### text_utils.py
String manipulation and text processing:
- `reverse_string()` - Basic string operation (safe, high MCP score)
- `count_words()` - Text analysis with optional parameters
- `extract_emails()` - Regex-based extraction, array returns
- `generate_hash()` - Cryptographic functions (medium risk)
- `format_template()` - Template processing with dict parameters
- `validate_phone_number()` - Complex validation logic

### risky_operations.py
Functions with security implications (should trigger approval workflow):
- `execute_command()` - System command execution (HIGH RISK)
- `read_system_file()` - File system access (MEDIUM RISK)
- `deserialize_data()` - Pickle deserialization (HIGH RISK)
- `list_directory_contents()` - Directory traversal (LOW-MEDIUM RISK)
- `network_request()` - HTTP requests (MEDIUM RISK)

## Expected Test Results

### Security Scanner Results:
- **Low Risk**: calculator.py functions, basic text_utils functions
- **Medium Risk**: generate_hash, file/network operations
- **High Risk**: execute_command, deserialize_data

### MCP Tool Candidates:
Functions should be scored based on:
- Parameter complexity
- Return value structure
- Documentation quality
- Security risk level
- Utility as AI tool

### Integration Testing:
1. Repository analysis should detect all functions
2. Security scanner should flag risky operations
3. Generated MCP server should:
   - Expose safe functions as tools
   - Include proper parameter validation
   - Handle errors gracefully
   - Provide comprehensive documentation via prompts/resources