#!/usr/bin/env python3
"""
User Approval Flow for MCP Server Conversion

Interactive CLI workflow for approving repository to MCP server conversion
with security-focused user guidance and decision making.
"""

import sys
from typing import List, Dict, Optional, Tuple
from pathlib import Path

from analyzer.models import MCPToolCandidate, AnalysisResult
from analyzer.security.pattern_scanner import SecurityScanner


class SecurityRiskDisplayer:
    """Formats security information for user review"""
    
    def __init__(self):
        self.scanner = SecurityScanner()
    
    def show_risk_summary(self, candidates: List[MCPToolCandidate], verbose: bool = False) -> None:
        """Display security risk summary with traffic light system"""
        safe_count = 0
        medium_count = 0
        high_count = 0
        
        for candidate in candidates:
            risk_score = self.scanner.calculate_risk_score(candidate.security_warnings)
            if risk_score < 2.0:
                safe_count += 1
            elif risk_score < 5.0:
                medium_count += 1
            else:
                high_count += 1
        
        print(f"\n{'='*50}")
        print(f"SECURITY RISK SUMMARY")
        print(f"{'='*50}")
        print(f"🟢 Safe functions: {safe_count}")
        print(f"🟡 Medium risk: {medium_count}")
        print(f"🔴 High risk: {high_count}")
        
        if high_count > 0:
            print(f"\n⚠️  WARNING: {high_count} high-risk functions detected!")
            print(f"   These functions contain potentially dangerous patterns.")
            print(f"   Review carefully before approval.")
        
        if verbose and medium_count > 0:
            print(f"\nℹ️  {medium_count} medium-risk functions require review.")
            print(f"   These may need security considerations in deployment.")
    
    def show_detailed_warnings(self, candidates: List[MCPToolCandidate]) -> None:
        """Show detailed security warnings for each function"""
        print(f"\n{'='*70}")
        print(f"DETAILED SECURITY WARNINGS")
        print(f"{'='*70}")
        
        for candidate in candidates:
            if not candidate.security_warnings:
                continue
                
            risk_score = self.scanner.calculate_risk_score(candidate.security_warnings)
            risk_level = "🔴 HIGH" if risk_score >= 5.0 else "🟡 MEDIUM"
            
            print(f"\n{candidate.function.function_name} ({Path(candidate.function.file_path).name})")
            print(f"Risk Score: {risk_score:.1f} ({risk_level})")
            print(f"MCP Score: {candidate.mcp_score}")
            
            for warning in candidate.security_warnings:
                print(f"  - {warning}")
    
    def get_risk_explanation(self, pattern_type: str) -> str:
        """Get explanation for specific risk pattern types"""
        explanations = {
            'system_commands': (
                "System command execution can allow arbitrary code execution. "
                "Consider input validation and sandboxing."
            ),
            'file_system_access': (
                "File system operations can access sensitive files. "
                "Ensure path validation and access controls."
            ),
            'network_operations': (
                "Network operations can access external resources. "
                "Consider firewall rules and request validation."
            ),
            'dangerous_modules': (
                "These modules can execute arbitrary code or access system internals. "
                "Use with extreme caution in containerized environments."
            ),
            'credential_handling': (
                "Credential variables may expose sensitive information. "
                "Ensure proper secret management and environment isolation."
            ),
            'database_operations': (
                "Database operations can modify or delete data. "
                "Ensure proper authorization and query validation."
            )
        }
        
        return explanations.get(pattern_type, "Unknown security risk pattern.")


class InteractivePrompts:
    """Handles user input and validation"""
    
    def get_approval_decision(self) -> str:
        """Get user approval decision with validation"""
        while True:
            response = input(
                "\nApprove server conversion? [y/N/details/security/help]: "
            ).lower().strip()
            
            if response in ['y', 'yes']:
                return 'approve'
            elif response in ['n', 'no', '']:
                return 'reject'
            elif response in ['d', 'details']:
                return 'show_details'
            elif response in ['s', 'security']:
                return 'show_security'
            elif response in ['h', 'help']:
                return 'show_help'
            else:
                print("Invalid input. Please enter 'y' (yes), 'n' (no), 'details', 'security', or 'help'")
    
    def get_risk_threshold(self) -> float:
        """Get user-specified risk threshold"""
        while True:
            try:
                response = input(
                    "\nSet maximum risk threshold (0.0-10.0, default 5.0): "
                ).strip()
                
                if not response:
                    return 5.0
                
                threshold = float(response)
                if 0.0 <= threshold <= 10.0:
                    return threshold
                else:
                    print("Please enter a value between 0.0 and 10.0")
            except ValueError:
                print("Please enter a valid number")
    
    def confirm_high_risk_approval(self, high_risk_count: int) -> bool:
        """Confirm approval for high-risk functions"""
        print(f"\n⚠️  SECURITY CONFIRMATION REQUIRED")
        print(f"You are about to approve {high_risk_count} high-risk functions.")
        print(f"These functions contain potentially dangerous patterns that could:")
        print(f"  - Execute system commands")
        print(f"  - Access sensitive files")
        print(f"  - Make network requests")
        print(f"  - Handle credentials")
        
        while True:
            response = input(
                f"\nDo you understand the risks and want to proceed? [y/N]: "
            ).lower().strip()
            
            if response in ['y', 'yes']:
                return True
            elif response in ['n', 'no', '']:
                return False
            else:
                print("Please enter 'y' (yes) or 'n' (no)")
    
    def show_help(self) -> None:
        """Display help information for approval process"""
        print(f"\n{'='*60}")
        print(f"APPROVAL PROCESS HELP")
        print(f"{'='*60}")
        print(f"Options:")
        print(f"  y/yes      - Approve server conversion and proceed")
        print(f"  n/no       - Reject conversion and exit (default)")
        print(f"  details    - Show detailed function information")
        print(f"  security   - Show detailed security warnings")
        print(f"  help       - Show this help message")
        print(f"\nSecurity Risk Levels:")
        print(f"  🟢 Safe     - No known security risks (score < 2.0)")
        print(f"  🟡 Medium   - Some security considerations (score 2.0-5.0)")
        print(f"  🔴 High     - Potentially dangerous patterns (score > 5.0)")
        print(f"\nRecommendation: Review all high-risk functions carefully")
        print(f"before approval. When in doubt, choose 'no'.")


class UserApprovalManager:
    """Orchestrates the approval workflow"""
    
    def __init__(self, verbose: bool = False):
        self.verbose = verbose
        self.risk_displayer = SecurityRiskDisplayer()
        self.prompts = InteractivePrompts()
        self.scanner = SecurityScanner()
    
    def request_approval(
        self, 
        candidates: List[MCPToolCandidate], 
        server_info: Dict,
        security_info: Optional[Dict] = None
    ) -> Dict:
        """
        Request user approval for server conversion
        
        Args:
            candidates: List of MCP tool candidates
            server_info: Information about the server being created
            security_info: Optional security summary information
            
        Returns:
            Dictionary with approval decision and metadata
        """
        print(f"\n{'='*70}")
        print(f"MCP SERVER CONVERSION APPROVAL")
        print(f"{'='*70}")
        print(f"Server: {server_info.get('name', 'Unknown')}")
        print(f"Repository: {server_info.get('repository', 'Unknown')}")
        print(f"Functions found: {len(candidates)}")
        
        # Calculate and display security summary
        self.risk_displayer.show_risk_summary(candidates, self.verbose)
        
        # Show top candidates
        self._show_candidate_summary(candidates)
        
        # Main approval loop
        while True:
            decision = self.prompts.get_approval_decision()
            
            if decision == 'approve':
                # Check for high-risk functions and confirm
                high_risk_candidates = [
                    c for c in candidates 
                    if self.scanner.calculate_risk_score(c.security_warnings) >= 5.0
                ]
                
                if high_risk_candidates:
                    if not self.prompts.confirm_high_risk_approval(len(high_risk_candidates)):
                        continue  # Go back to main decision
                
                return {
                    'approved': True,
                    'candidates': candidates,
                    'metadata': {
                        'timestamp': self._get_timestamp(),
                        'risk_acknowledged': len(high_risk_candidates) > 0
                    }
                }
            
            elif decision == 'reject':
                return {
                    'approved': False,
                    'reason': 'User rejected conversion',
                    'metadata': {
                        'timestamp': self._get_timestamp()
                    }
                }
            
            elif decision == 'show_details':
                self._show_detailed_candidates(candidates)
            
            elif decision == 'show_security':
                self.risk_displayer.show_detailed_warnings(candidates)
            
            elif decision == 'show_help':
                self.prompts.show_help()
    
    def show_approval_summary(self, decision: Dict) -> None:
        """Display summary of approval decision"""
        if decision['approved']:
            print(f"\n✅ SERVER CONVERSION APPROVED")
            if decision['metadata'].get('risk_acknowledged'):
                print(f"⚠️  High-risk functions included with user acknowledgment")
            print(f"Proceeding with server generation...")
        else:
            print(f"\n❌ SERVER CONVERSION REJECTED")
            print(f"Reason: {decision.get('reason', 'Unknown')}")
            print(f"Server generation cancelled.")
    
    def _show_candidate_summary(self, candidates: List[MCPToolCandidate], limit: int = 10) -> None:
        """Show summary of top candidates"""
        print(f"\nTop function candidates:")
        
        # Sort by MCP score (descending) and show top N
        sorted_candidates = sorted(candidates, key=lambda c: c.mcp_score, reverse=True)
        display_candidates = sorted_candidates[:limit]
        
        for i, candidate in enumerate(display_candidates, 1):
            func = candidate.function
            risk_score = self.scanner.calculate_risk_score(candidate.security_warnings)
            risk_emoji = "🔴" if risk_score >= 5.0 else "🟡" if risk_score >= 2.0 else "🟢"
            
            file_name = Path(func.file_path).name
            print(f"  {i:2}. {func.function_name:<25} (score: {candidate.mcp_score:4.1f}) {risk_emoji} {file_name}")
        
        if len(candidates) > limit:
            print(f"  ... and {len(candidates) - limit} more functions")
    
    def _show_detailed_candidates(self, candidates: List[MCPToolCandidate]) -> None:
        """Show detailed information about candidates"""
        print(f"\n{'='*70}")
        print(f"DETAILED FUNCTION INFORMATION")
        print(f"{'='*70}")
        
        sorted_candidates = sorted(candidates, key=lambda c: c.mcp_score, reverse=True)
        
        for i, candidate in enumerate(sorted_candidates, 1):
            func = candidate.function
            risk_score = self.scanner.calculate_risk_score(candidate.security_warnings)
            
            print(f"\n{i}. {func.function_name}")
            print(f"   File: {func.file_path}")
            print(f"   Language: {func.language}")
            print(f"   MCP Score: {candidate.mcp_score}")
            print(f"   Risk Score: {risk_score:.1f}")
            print(f"   Description: {candidate.description}")
            
            if func.parameters:
                print(f"   Parameters:")
                for param in func.parameters:
                    required = " (required)" if param.required else " (optional)"
                    print(f"     - {param.name}: {param.type_hint}{required}")
            
            if candidate.security_warnings:
                print(f"   Security warnings: {len(candidate.security_warnings)}")
    
    def _get_timestamp(self) -> str:
        """Get current timestamp string"""
        from datetime import datetime
        return datetime.now().isoformat()


def create_approval_workflow(verbose: bool = False) -> UserApprovalManager:
    """Factory function to create approval workflow manager"""
    return UserApprovalManager(verbose=verbose)


# CLI integration helper functions
def integrate_approval_step(
    candidates: List[MCPToolCandidate],
    server_info: Dict,
    interactive: bool = True,
    verbose: bool = False
) -> Tuple[bool, List[MCPToolCandidate]]:
    """
    Integrate approval step into existing CLI workflows
    
    Args:
        candidates: MCP tool candidates from analysis
        server_info: Server information dictionary
        interactive: Whether to show interactive approval (default: True)
        verbose: Verbose output mode
        
    Returns:
        Tuple of (approved, filtered_candidates)
    """
    if not interactive:
        # Non-interactive mode: approve all candidates
        return True, candidates
    
    # Interactive approval workflow
    approval_manager = UserApprovalManager(verbose=verbose)
    decision = approval_manager.request_approval(candidates, server_info)
    approval_manager.show_approval_summary(decision)
    
    if decision['approved']:
        return True, decision['candidates']
    else:
        return False, []


if __name__ == "__main__":
    # Simple test when run directly
    print("User Approval Flow Module")
    print("This module provides interactive approval workflow for MCP server conversion.")
    print("Import and use integrate_approval_step() in your CLI tools.")