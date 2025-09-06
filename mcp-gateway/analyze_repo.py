#!/usr/bin/env python3
"""
Repository Analyzer CLI Tool

Command-line interface for analyzing repositories and identifying MCP tool candidates.
"""

import argparse
import sys
import json
from pathlib import Path
from typing import Optional

from analyzer.repository_analyzer import RepositoryAnalyzer


def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description="Analyze a repository for MCP tool conversion candidates",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Analyze current directory
  python analyze_repo.py .
  
  # Analyze specific repository
  python analyze_repo.py /path/to/repo
  
  # Save results to specific file
  python analyze_repo.py /path/to/repo --output analysis_result.json
  
  # Show only high-scoring candidates
  python analyze_repo.py /path/to/repo --min-score 7.0
  
  # Include detailed security information
  python analyze_repo.py /path/to/repo --show-security
        """
    )
    
    parser.add_argument(
        "repository", 
        help="Path to the repository to analyze"
    )
    
    parser.add_argument(
        "--output", "-o",
        help="Output JSON file path (default: analysis_result_<repo_name>.json)"
    )
    
    parser.add_argument(
        "--min-score", 
        type=float, 
        default=3.0,
        help="Minimum MCP score to display (default: 3.0)"
    )
    
    parser.add_argument(
        "--show-security",
        action="store_true",
        help="Show detailed security warnings for each function"
    )
    
    parser.add_argument(
        "--limit",
        type=int,
        default=20,
        help="Maximum number of candidates to display (default: 20)"
    )
    
    parser.add_argument(
        "--format",
        choices=["table", "json", "summary"],
        default="table",
        help="Output format (default: table)"
    )
    
    args = parser.parse_args()
    
    # Validate repository path
    repo_path = Path(args.repository).resolve()
    if not repo_path.exists():
        print(f"Error: Repository path does not exist: {repo_path}")
        sys.exit(1)
    
    if not repo_path.is_dir():
        print(f"Error: Repository path is not a directory: {repo_path}")
        sys.exit(1)
    
    # Initialize analyzer
    print(f"Initializing Repository Analyzer...")
    analyzer = RepositoryAnalyzer()
    
    try:
        # Perform analysis
        print(f"Analyzing repository: {repo_path}")
        result = analyzer.analyze_repository(str(repo_path))
        
        # Filter candidates by minimum score
        filtered_candidates = [
            c for c in result.candidates 
            if c.mcp_score >= args.min_score
        ]
        
        # Limit results
        if args.limit:
            filtered_candidates = filtered_candidates[:args.limit]
        
        # Display results based on format
        if args.format == "json":
            output_data = {
                "repository": result.repository,
                "analyzed_files": result.analyzed_files,
                "languages": result.languages,
                "total_candidates": len(result.candidates),
                "filtered_candidates": len(filtered_candidates),
                "security_summary": result.security_summary,
                "candidates": [
                    {
                        "function_name": c.function.function_name,
                        "file_path": c.function.file_path,
                        "language": c.function.language,
                        "mcp_score": c.mcp_score,
                        "description": c.description,
                        "parameters": {
                            p.name: {
                                "type": p.type_hint,
                                "description": p.description,
                                "default": p.default_value,
                                "required": p.required
                            } for p in c.function.parameters
                        },
                        "security_warnings": c.security_warnings if args.show_security else len(c.security_warnings),
                        "docker_requirements": c.docker_requirements
                    } for c in filtered_candidates
                ]
            }
            print(json.dumps(output_data, indent=2))
        
        elif args.format == "summary":
            print_summary(result, filtered_candidates)
        
        else:  # table format (default)
            print_table_format(result, filtered_candidates, args.show_security)
        
        # Save to file if requested
        output_file = args.output
        if not output_file:
            repo_name = repo_path.name
            output_file = f"analysis_result_{repo_name}.json"
        
        analyzer.save_result(result, output_file)
        print(f"\nFull analysis result saved to: {output_file}")
        
    except Exception as e:
        print(f"Error during analysis: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


def print_summary(result, candidates):
    """Print a summary of the analysis results"""
    print(f"\n{'='*60}")
    print(f"REPOSITORY ANALYSIS SUMMARY")
    print(f"{'='*60}")
    print(f"Repository: {result.repository}")
    print(f"Files analyzed: {result.analyzed_files}")
    print(f"Languages: {', '.join(result.languages)}")
    print(f"Total function candidates: {len(result.candidates)}")
    print(f"High-quality candidates: {len(candidates)}")
    print(f"\nSecurity Summary:")
    for key, value in result.security_summary.items():
        print(f"  {key.replace('_', ' ').title()}: {value}")


def print_table_format(result, candidates, show_security=False):
    """Print results in a formatted table"""
    print(f"\n{'='*80}")
    print(f"REPOSITORY ANALYSIS RESULTS")
    print(f"{'='*80}")
    print(f"Repository: {result.repository}")
    print(f"Files analyzed: {result.analyzed_files} | Languages: {', '.join(result.languages)}")
    print(f"Total candidates: {len(result.candidates)} | Showing: {len(candidates)}")
    
    if not candidates:
        print("\nNo candidates found matching the criteria.")
        return
    
    print(f"\n{'#':<3} {'Function':<25} {'Score':<6} {'File':<30} {'Description':<40}")
    print(f"{'-'*3} {'-'*25} {'-'*6} {'-'*30} {'-'*40}")
    
    for i, candidate in enumerate(candidates):
        func = candidate.function
        file_path = Path(func.file_path).name  # Just filename
        description = candidate.description[:37] + "..." if len(candidate.description) > 40 else candidate.description
        
        print(f"{i+1:<3} {func.function_name:<25} {candidate.mcp_score:<6.1f} {file_path:<30} {description:<40}")
        
        if show_security and candidate.security_warnings:
            print(f"    Security warnings:")
            for warning in candidate.security_warnings:
                print(f"      - {warning}")
            print()
    
    # Security summary
    print(f"\nSecurity Summary:")
    security = result.security_summary
    safe = security.get('safe_functions', 0)
    medium = security.get('medium_risk_functions', 0) 
    high = security.get('high_risk_functions', 0)
    
    print(f"  Safe functions: {safe} | Medium risk: {medium} | High risk: {high}")
    
    if candidates:
        avg_score = sum(c.mcp_score for c in candidates) / len(candidates)
        print(f"\nAverage MCP Score: {avg_score:.1f}")


if __name__ == "__main__":
    main()