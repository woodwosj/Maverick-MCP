#!/usr/bin/env python3
"""
Docker MCP Server Generator CLI

Command-line interface for generating Docker-based MCP servers from repository analysis.
"""

import argparse
import sys
import json
from pathlib import Path
from typing import Optional

from analyzer.repository_analyzer import RepositoryAnalyzer
from dockerfile_generator.dockerfile_generator import DockerfileGenerator
from approval_flow import integrate_approval_step


def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description="Generate Docker-based MCP servers from repository analysis",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Analyze and generate MCP server from repository
  python generate_docker_server.py /path/to/repo my-server
  
  # Interactive approval with security review
  python generate_docker_server.py /path/to/repo my-server --interactive
  
  # Use existing analysis result
  python generate_docker_server.py --analysis analysis_result.json my-server
  
  # Generate with specific output directory
  python generate_docker_server.py /path/to/repo my-server --output ./generated_servers/
  
  # Include low-scoring candidates with interactive approval
  python generate_docker_server.py /path/to/repo my-server --min-score 2.0 --interactive
        """
    )
    
    parser.add_argument(
        "input",
        help="Path to repository or analysis result JSON file"
    )
    
    parser.add_argument(
        "server_name",
        help="Name for the generated MCP server"
    )
    
    parser.add_argument(
        "--output", "-o",
        default="./generated_servers",
        help="Output directory for generated files (default: ./generated_servers)"
    )
    
    parser.add_argument(
        "--analysis",
        action="store_true",
        help="Input is an analysis result JSON file (skip repository analysis)"
    )
    
    parser.add_argument(
        "--min-score",
        type=float,
        default=5.0,
        help="Minimum MCP score for included functions (default: 5.0)"
    )
    
    parser.add_argument(
        "--language",
        choices=["python", "javascript", "go"],
        help="Override language detection (use specific language)"
    )
    
    parser.add_argument(
        "--build",
        action="store_true",
        help="Automatically build Docker image after generation"
    )
    
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Verbose output"
    )
    
    parser.add_argument(
        "--interactive", "-i",
        action="store_true",
        help="Enable interactive approval workflow with security review"
    )
    
    args = parser.parse_args()
    
    # Validate inputs
    input_path = Path(args.input).resolve()
    if not input_path.exists():
        print(f"Error: Input path does not exist: {input_path}")
        sys.exit(1)
    
    server_name = args.server_name.lower().replace('_', '-').replace(' ', '-')
    output_dir = Path(args.output) / server_name
    
    try:
        # Step 1: Get analysis result
        if args.analysis:
            if args.verbose:
                print(f"Loading analysis result from: {input_path}")
            
            with open(input_path, 'r') as f:
                analysis_data = json.load(f)
            
            # Convert back to analysis result (simplified)
            from analyzer.models import AnalysisResult, MCPToolCandidate, FunctionCandidate
            
            # This is a simplified reconstruction - in a real implementation,
            # you'd want to properly deserialize the full objects
            candidates = []  # TODO: Implement proper deserialization
            
            analysis_result = AnalysisResult(
                repository=analysis_data['repository'],
                analyzed_files=analysis_data['analyzed_files'],
                languages=analysis_data['languages'],
                candidates=candidates,
                security_summary=analysis_data.get('security_summary', {})
            )
            
            repo_info = {
                'name': Path(analysis_data['repository']).name,
                'url': analysis_data.get('url', ''),
                'path': analysis_data['repository']
            }
            
        else:
            if args.verbose:
                print(f"Analyzing repository: {input_path}")
            
            analyzer = RepositoryAnalyzer()
            analysis_result = analyzer.analyze_repository(str(input_path))
            
            repo_info = {
                'name': input_path.name,
                'url': '',
                'path': str(input_path)
            }
        
        # Step 2: Filter candidates by score
        filtered_candidates = [
            c for c in analysis_result.candidates
            if c.mcp_score >= args.min_score
        ]
        
        if not filtered_candidates:
            print(f"No candidates found with score >= {args.min_score}")
            print(f"Total candidates: {len(analysis_result.candidates)}")
            if analysis_result.candidates:
                max_score = max(c.mcp_score for c in analysis_result.candidates)
                print(f"Highest score: {max_score}")
            sys.exit(1)
        
        # Step 3: Override language if specified
        if args.language:
            # Filter candidates to only include the specified language
            filtered_candidates = [
                c for c in filtered_candidates 
                if c.function.language == args.language
            ]
            
            if not filtered_candidates:
                print(f"No candidates found for language: {args.language}")
                sys.exit(1)
        
        if args.verbose:
            print(f"Using {len(filtered_candidates)} candidates for server generation")
            primary_language = args.language or filtered_candidates[0].function.language
            print(f"Primary language: {primary_language}")
        
        # Step 3.5: Interactive approval workflow (if enabled)
        if args.interactive:
            server_info = {
                'name': server_name,
                'repository': repo_info.get('path', 'Unknown'),
                'candidates': filtered_candidates
            }
            
            approved, approved_candidates = integrate_approval_step(
                candidates=filtered_candidates,
                server_info=server_info,
                interactive=True,
                verbose=args.verbose
            )
            
            if not approved:
                print(f"\nServer conversion cancelled by user.")
                sys.exit(0)
            
            # Use approved candidates for generation
            filtered_candidates = approved_candidates
            
            if args.verbose:
                print(f"Proceeding with {len(filtered_candidates)} approved candidates")
        
        # Step 4: Generate MCP server package
        generator = DockerfileGenerator()
        
        if args.verbose:
            print(f"Generating MCP server package in: {output_dir}")
        
        result = generator.generate_mcp_server_package(
            candidates=filtered_candidates,
            server_name=server_name,
            repo_info=repo_info,
            output_dir=str(output_dir)
        )
        
        # Step 5: Display results
        print(f"\n{'='*60}")
        print(f"MCP SERVER GENERATION COMPLETE")
        print(f"{'='*60}")
        print(f"Server name: {result['server_name']}")
        print(f"Language: {result['language']}")
        print(f"Functions: {result['total_functions']}")
        print(f"Output directory: {output_dir}")
        
        print(f"\nGenerated files:")
        for file_type, file_path in result['generated_files'].items():
            print(f"  - {file_type}: {Path(file_path).name}")
        
        # Step 6: Build Docker image if requested
        if args.build:
            print(f"\nBuilding Docker image...")
            import subprocess
            
            build_cmd = [
                "docker", "build", 
                "-t", f"mcp-{server_name}",
                str(output_dir)
            ]
            
            try:
                if args.verbose:
                    print(f"Running: {' '.join(build_cmd)}")
                
                result_build = subprocess.run(build_cmd, capture_output=True, text=True)
                
                if result_build.returncode == 0:
                    print(f"✅ Docker image 'mcp-{server_name}' built successfully!")
                else:
                    print(f"❌ Docker build failed:")
                    print(result_build.stderr)
                    sys.exit(1)
                    
            except FileNotFoundError:
                print("❌ Docker not found. Please install Docker to build images.")
                print("Generated files are ready for manual building.")
        
        # Step 7: Display usage instructions
        print(f"\nNext steps:")
        print(f"1. Review generated files in: {output_dir}")
        if not args.build:
            print(f"2. Build Docker image: docker build -t mcp-{server_name} {output_dir}")
        print(f"3. Add to servers.yaml (see servers_entry.yaml)")
        print(f"4. Test with: docker run -i mcp-{server_name}")
        
        print(f"\nGeneration completed successfully! 🎉")
        
    except Exception as e:
        print(f"Error during server generation: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()