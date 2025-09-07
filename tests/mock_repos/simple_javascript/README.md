# Simple JavaScript Mock Repository

This repository contains JavaScript functions designed for testing the Maverick MCP analysis and generation system. It includes 18 functions across different categories and risk levels.

## Modules

### calculator.js (5 functions)
- `addNumbers(a, b)` - Basic addition (LOW RISK)
- `calculatePower(base, exponent = 2)` - Power calculation (LOW RISK)  
- `factorial(n)` - Factorial calculation with validation (LOW RISK)
- `calculateCircleArea(radius)` - Circle area calculation (LOW RISK)
- `solveQuadratic(a, b, c)` - Quadratic equation solver (LOW RISK)

### text_utils.js (6 functions)
- `toTitleCase(text)` - Convert to title case (LOW RISK)
- `countWords(text)` - Count words in text (LOW RISK)
- `removeWhitespace(text)` - Remove all whitespace (LOW RISK)
- `isPalindrome(text)` - Check if palindrome (LOW RISK)
- `generateSlug(text)` - Generate URL slug (LOW RISK)
- `truncateText(text, maxLength, suffix)` - Truncate with ellipsis (LOW RISK)

### async_ops.js (4 functions)
- `delay(ms)` - Async delay operation (LOW RISK)
- `fetchMockData(url, timeout)` - Mock API fetch (MEDIUM RISK)
- `processItemsAsync(items, delayMs)` - Async array processing (LOW RISK)
- `retryOperation(operation, maxAttempts, baseDelay)` - Retry with backoff (LOW RISK)

### array_utils.js (4 functions)
- `findUnique(arr)` - Find unique elements (LOW RISK)
- `groupBy(arr, property)` - Group objects by property (LOW RISK)
- `calculateStats(numbers)` - Statistical analysis (LOW RISK)
- `chunkArray(arr, size)` - Split array into chunks (LOW RISK)

### risky_operations.js (6 functions)
- `executeCommand(command, options)` - Shell command execution (**HIGH RISK**)
- `writeToFile(filePath, content, options)` - File system write (**HIGH RISK**)
- `readSensitiveFile(filePath, options)` - File reading (**MEDIUM RISK**)
- `makeHttpRequest(url, options)` - HTTP requests (**MEDIUM RISK**)
- `evaluateCode(code, context)` - Dynamic code evaluation (**HIGH RISK**)
- `deleteFileOrDirectory(targetPath, options)` - File/directory deletion (**HIGH RISK**)

## Security Risk Distribution

- **LOW RISK**: 15 functions - Pure computation, string manipulation, data processing
- **MEDIUM RISK**: 2 functions - File reading, HTTP requests  
- **HIGH RISK**: 4 functions - Command execution, file writing, code evaluation, file deletion

## Testing Purpose

This repository is designed to test:

1. **Function Detection**: Various function declaration styles (function, arrow, method, export)
2. **Parameter Extraction**: Required/optional parameters, default values, destructuring
3. **Documentation Parsing**: JSDoc comments with different annotation styles
4. **Async Pattern Recognition**: async/await, Promise-based operations
5. **Security Classification**: Risk assessment for different operation types
6. **MCP Generation**: Complete pipeline from analysis to working MCP server

## Expected Analysis Results

The Maverick MCP analyzer should:
- Detect all 18 functions across the 5 modules
- Properly classify security risks (4 HIGH, 2 MEDIUM, 15 LOW)
- Extract JSDoc documentation and parameter information
- Generate working Node.js MCP server with all functions callable
- Handle both ES6 modules and various JavaScript patterns

This repository validates the JavaScript language support in Maverick MCP and ensures feature parity with the existing Python analyzer.