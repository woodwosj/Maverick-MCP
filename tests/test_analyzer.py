"""
Test script for the Repository Analyzer
"""

import sys
import os
from pathlib import Path

# Add the parent directory to path so we can import the analyzer
sys.path.append(str(Path(__file__).parent.parent))

from analyzer.repository_analyzer import RepositoryAnalyzer
from analyzer.language_parsers.python_analyzer import PythonAnalyzer
from analyzer.security.pattern_scanner import SecurityScanner


def test_python_analyzer():
    """Test the Python analyzer on sample code"""
    print("=== Testing Python Analyzer ===")
    
    analyzer = PythonAnalyzer()
    test_file = Path(__file__).parent / "test_data" / "sample_functions.py"
    
    functions = analyzer.analyze_file(str(test_file))
    
    print(f"Found {len(functions)} functions:")
    for func in functions:
        print(f"  - {func.function_name} ({len(func.parameters)} params)")
        if func.docstring:
            print(f"    Docstring: {func.docstring[:100]}...")
        print(f"    Line: {func.line_number}")
    
    return functions


def test_security_scanner():
    """Test the security scanner"""
    print("\n=== Testing Security Scanner ===")
    
    analyzer = PythonAnalyzer()
    scanner = SecurityScanner()
    
    test_file = Path(__file__).parent / "test_data" / "sample_functions.py"
    functions = analyzer.analyze_file(str(test_file))
    
    for func in functions:
        warnings = scanner.scan_function(func)
        risk_score = scanner.calculate_risk_score(warnings)
        
        print(f"\nFunction: {func.function_name}")
        print(f"Risk Score: {risk_score}")
        if warnings:
            print("Warnings:")
            for warning in warnings:
                print(f"  - {warning}")
        else:
            print("No security warnings")


def test_repository_analyzer():
    """Test the full repository analyzer"""
    print("\n=== Testing Repository Analyzer ===")
    
    analyzer = RepositoryAnalyzer()
    test_dir = Path(__file__).parent / "test_data"
    
    result = analyzer.analyze_repository(str(test_dir))
    
    print(f"Analysis Result:")
    print(f"  Repository: {result.repository}")
    print(f"  Files analyzed: {result.analyzed_files}")
    print(f"  Languages: {result.languages}")
    print(f"  Candidates found: {len(result.candidates)}")
    print(f"  Security summary: {result.security_summary}")
    
    print("\nTop MCP Tool Candidates:")
    for i, candidate in enumerate(result.candidates[:5]):  # Top 5
        print(f"  {i+1}. {candidate.function.function_name} (score: {candidate.mcp_score:.1f})")
        print(f"     {candidate.description}")
        if candidate.security_warnings:
            print(f"     Security warnings: {len(candidate.security_warnings)}")
    
    # Save result to file
    output_file = Path(__file__).parent / "test_analysis_result.json"
    analyzer.save_result(result, str(output_file))
    print(f"\nResult saved to: {output_file}")


def main():
    """Run all tests"""
    try:
        functions = test_python_analyzer()
        test_security_scanner()
        test_repository_analyzer()
        
        print("\n=== All Tests Completed Successfully ===")
        
    except Exception as e:
        print(f"Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()