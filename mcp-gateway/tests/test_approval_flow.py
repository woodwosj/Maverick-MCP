"""
Test script for the User Approval Flow system
"""

import sys
import os
import unittest
from unittest.mock import patch, MagicMock
from pathlib import Path
from io import StringIO

# Add the parent directory to path so we can import modules
sys.path.append(str(Path(__file__).parent.parent))

from approval_flow import (
    UserApprovalManager, 
    SecurityRiskDisplayer, 
    InteractivePrompts,
    integrate_approval_step
)
from analyzer.models import MCPToolCandidate, FunctionCandidate, FunctionParameter
from analyzer.security.pattern_scanner import SecurityScanner


class TestSecurityRiskDisplayer(unittest.TestCase):
    """Test SecurityRiskDisplayer functionality"""
    
    def setUp(self):
        self.displayer = SecurityRiskDisplayer()
        self.safe_candidate = self._create_test_candidate("safe_function", [])
        self.risky_candidate = self._create_test_candidate(
            "risky_function", 
            ["HIGH RISK (system_commands): Found potentially dangerous pattern",
             "HIGH RISK (file_system_access): Found potentially dangerous pattern"]
        )
    
    def _create_test_candidate(self, name: str, warnings: list):
        """Helper to create test candidates"""
        func = FunctionCandidate(
            function_name=name,
            file_path=f"/test/{name}.py",
            language="python",
            line_number=1,
            parameters=[],
            return_type="str",
            docstring=f"Test function {name}",
            source_code=f"def {name}():\n    return 'test'"
        )
        
        return MCPToolCandidate(
            function=func,
            mcp_score=7.5,
            description=f"Test {name} description",
            security_warnings=warnings,
            docker_requirements=[]
        )
    
    def test_show_risk_summary_safe(self):
        """Test risk summary display for safe functions"""
        with patch('sys.stdout', new=StringIO()) as fake_out:
            self.displayer.show_risk_summary([self.safe_candidate])
            output = fake_out.getvalue()
            
        self.assertIn("🟢 Safe functions: 1", output)
        self.assertIn("🟡 Medium risk: 0", output)
        self.assertIn("🔴 High risk: 0", output)
        self.assertNotIn("WARNING", output)
    
    def test_show_risk_summary_risky(self):
        """Test risk summary display for risky functions"""
        with patch('sys.stdout', new=StringIO()) as fake_out:
            self.displayer.show_risk_summary([self.risky_candidate])
            output = fake_out.getvalue()
            
        self.assertIn("🟢 Safe functions: 0", output)
        self.assertIn("🔴 High risk: 1", output)
        self.assertIn("WARNING", output)
        self.assertIn("high-risk functions detected", output)
    
    def test_show_detailed_warnings(self):
        """Test detailed warning display"""
        with patch('sys.stdout', new=StringIO()) as fake_out:
            self.displayer.show_detailed_warnings([self.risky_candidate])
            output = fake_out.getvalue()
            
        self.assertIn("risky_function", output)
        self.assertIn("🔴 HIGH", output)
        self.assertIn("HIGH RISK (system_commands)", output)
    
    def test_risk_explanations(self):
        """Test risk pattern explanations"""
        explanation = self.displayer.get_risk_explanation('system_commands')
        self.assertIn("System command execution", explanation)
        self.assertIn("arbitrary code execution", explanation)
        
        unknown = self.displayer.get_risk_explanation('unknown_pattern')
        self.assertIn("Unknown security risk", unknown)


class TestInteractivePrompts(unittest.TestCase):
    """Test InteractivePrompts functionality"""
    
    def setUp(self):
        self.prompts = InteractivePrompts()
    
    @patch('builtins.input')
    def test_get_approval_decision_approve(self, mock_input):
        """Test approval decision - approve"""
        mock_input.return_value = 'y'
        decision = self.prompts.get_approval_decision()
        self.assertEqual(decision, 'approve')
        
        mock_input.return_value = 'yes'
        decision = self.prompts.get_approval_decision()
        self.assertEqual(decision, 'approve')
    
    @patch('builtins.input')
    def test_get_approval_decision_reject(self, mock_input):
        """Test approval decision - reject"""
        mock_input.return_value = 'n'
        decision = self.prompts.get_approval_decision()
        self.assertEqual(decision, 'reject')
        
        mock_input.return_value = ''  # Default to reject
        decision = self.prompts.get_approval_decision()
        self.assertEqual(decision, 'reject')
    
    @patch('builtins.input')
    def test_get_approval_decision_other_options(self, mock_input):
        """Test approval decision - other options"""
        mock_input.return_value = 'details'
        decision = self.prompts.get_approval_decision()
        self.assertEqual(decision, 'show_details')
        
        mock_input.return_value = 'security'
        decision = self.prompts.get_approval_decision()
        self.assertEqual(decision, 'show_security')
    
    @patch('builtins.input')
    @patch('sys.stdout', new_callable=StringIO)
    def test_get_approval_decision_invalid_then_valid(self, mock_stdout, mock_input):
        """Test invalid input followed by valid input"""
        mock_input.side_effect = ['invalid', 'y']
        decision = self.prompts.get_approval_decision()
        self.assertEqual(decision, 'approve')
        
        output = mock_stdout.getvalue()
        self.assertIn("Invalid input", output)
    
    @patch('builtins.input')
    def test_get_risk_threshold_default(self, mock_input):
        """Test risk threshold with default"""
        mock_input.return_value = ''
        threshold = self.prompts.get_risk_threshold()
        self.assertEqual(threshold, 5.0)
    
    @patch('builtins.input')
    def test_get_risk_threshold_custom(self, mock_input):
        """Test risk threshold with custom value"""
        mock_input.return_value = '7.5'
        threshold = self.prompts.get_risk_threshold()
        self.assertEqual(threshold, 7.5)
    
    @patch('builtins.input')
    @patch('sys.stdout', new_callable=StringIO)
    def test_get_risk_threshold_invalid(self, mock_stdout, mock_input):
        """Test invalid risk threshold input"""
        mock_input.side_effect = ['invalid', '15.0', '3.0']  # invalid, out of range, valid
        threshold = self.prompts.get_risk_threshold()
        self.assertEqual(threshold, 3.0)
        
        output = mock_stdout.getvalue()
        self.assertIn("valid number", output)
        self.assertIn("between 0.0 and 10.0", output)
    
    @patch('builtins.input')
    def test_confirm_high_risk_approval(self, mock_input):
        """Test high risk confirmation"""
        mock_input.return_value = 'y'
        confirmed = self.prompts.confirm_high_risk_approval(3)
        self.assertTrue(confirmed)
        
        mock_input.return_value = 'n'
        confirmed = self.prompts.confirm_high_risk_approval(3)
        self.assertFalse(confirmed)
    
    @patch('builtins.input')
    @patch('sys.stdout', new_callable=StringIO)
    def test_show_help(self, mock_stdout, mock_input):
        """Test help display"""
        self.prompts.show_help()
        output = mock_stdout.getvalue()
        
        self.assertIn("APPROVAL PROCESS HELP", output)
        self.assertIn("y/yes", output)
        self.assertIn("n/no", output)
        self.assertIn("details", output)
        self.assertIn("security", output)
        self.assertIn("🟢 Safe", output)
        self.assertIn("🟡 Medium", output)
        self.assertIn("🔴 High", output)


class TestUserApprovalManager(unittest.TestCase):
    """Test UserApprovalManager functionality"""
    
    def setUp(self):
        self.manager = UserApprovalManager(verbose=False)
        self.safe_candidate = self._create_test_candidate("safe_func", [])
        self.risky_candidate = self._create_test_candidate(
            "risky_func",
            ["HIGH RISK (system_commands): Found potentially dangerous pattern",
             "HIGH RISK (file_system_access): Found potentially dangerous pattern"]
        )
        self.server_info = {
            'name': 'test-server',
            'repository': '/test/repo',
            'candidates': [self.safe_candidate]
        }
    
    def _create_test_candidate(self, name: str, warnings: list):
        """Helper to create test candidates"""
        func = FunctionCandidate(
            function_name=name,
            file_path=f"/test/{name}.py",
            language="python",
            line_number=1,
            parameters=[
                FunctionParameter(
                    name="param1",
                    type_hint="str",
                    default_value=None,
                    required=True,
                    description="Test parameter"
                )
            ],
            return_type="str",
            docstring=f"Test function {name}",
            source_code=f"def {name}(param1: str) -> str:\n    return param1"
        )
        
        return MCPToolCandidate(
            function=func,
            mcp_score=7.5,
            description=f"Test {name} description",
            security_warnings=warnings,
            docker_requirements=[]
        )
    
    @patch('approval_flow.InteractivePrompts.get_approval_decision')
    @patch('sys.stdout', new_callable=StringIO)
    def test_request_approval_approve_safe(self, mock_stdout, mock_decision):
        """Test approval workflow - approve safe functions"""
        mock_decision.return_value = 'approve'
        
        decision = self.manager.request_approval([self.safe_candidate], self.server_info)
        
        self.assertTrue(decision['approved'])
        self.assertEqual(len(decision['candidates']), 1)
        self.assertFalse(decision['metadata']['risk_acknowledged'])
        
        output = mock_stdout.getvalue()
        self.assertIn("test-server", output)
        self.assertIn("🟢 Safe functions: 1", output)
    
    @patch('approval_flow.InteractivePrompts.get_approval_decision')
    @patch('approval_flow.InteractivePrompts.confirm_high_risk_approval')
    @patch('sys.stdout', new_callable=StringIO)
    def test_request_approval_approve_risky(self, mock_stdout, mock_confirm, mock_decision):
        """Test approval workflow - approve risky functions with confirmation"""
        mock_decision.return_value = 'approve'
        mock_confirm.return_value = True
        
        decision = self.manager.request_approval([self.risky_candidate], self.server_info)
        
        self.assertTrue(decision['approved'])
        self.assertTrue(decision['metadata']['risk_acknowledged'])
        mock_confirm.assert_called_once_with(1)  # 1 high-risk function
    
    @patch('approval_flow.InteractivePrompts.get_approval_decision')
    @patch('approval_flow.InteractivePrompts.confirm_high_risk_approval')
    def test_request_approval_reject_risky(self, mock_confirm, mock_decision):
        """Test approval workflow - reject risky functions"""
        mock_decision.return_value = 'approve'
        mock_confirm.return_value = False  # User rejects high risk
        mock_decision.side_effect = ['approve', 'reject']  # First approve, then reject after confirmation
        
        decision = self.manager.request_approval([self.risky_candidate], self.server_info)
        
        # Should go back to decision loop and then reject
        self.assertFalse(decision['approved'])
        self.assertEqual(decision['reason'], 'User rejected conversion')
    
    @patch('approval_flow.InteractivePrompts.get_approval_decision')
    def test_request_approval_reject_directly(self, mock_decision):
        """Test approval workflow - direct rejection"""
        mock_decision.return_value = 'reject'
        
        decision = self.manager.request_approval([self.safe_candidate], self.server_info)
        
        self.assertFalse(decision['approved'])
        self.assertEqual(decision['reason'], 'User rejected conversion')
    
    @patch('approval_flow.InteractivePrompts.get_approval_decision')
    @patch('approval_flow.UserApprovalManager._show_detailed_candidates')
    def test_request_approval_show_details(self, mock_show_details, mock_decision):
        """Test approval workflow - show details then approve"""
        mock_decision.side_effect = ['show_details', 'approve']
        
        decision = self.manager.request_approval([self.safe_candidate], self.server_info)
        
        self.assertTrue(decision['approved'])
        mock_show_details.assert_called_once()
    
    @patch('sys.stdout', new_callable=StringIO)
    def test_show_approval_summary_approved(self, mock_stdout):
        """Test approval summary display - approved"""
        decision = {'approved': True, 'metadata': {'risk_acknowledged': False}}
        self.manager.show_approval_summary(decision)
        
        output = mock_stdout.getvalue()
        self.assertIn("✅ SERVER CONVERSION APPROVED", output)
        self.assertNotIn("High-risk functions", output)
    
    @patch('sys.stdout', new_callable=StringIO)
    def test_show_approval_summary_approved_with_risk(self, mock_stdout):
        """Test approval summary display - approved with risk"""
        decision = {'approved': True, 'metadata': {'risk_acknowledged': True}}
        self.manager.show_approval_summary(decision)
        
        output = mock_stdout.getvalue()
        self.assertIn("✅ SERVER CONVERSION APPROVED", output)
        self.assertIn("⚠️  High-risk functions included", output)
    
    @patch('sys.stdout', new_callable=StringIO)
    def test_show_approval_summary_rejected(self, mock_stdout):
        """Test approval summary display - rejected"""
        decision = {'approved': False, 'reason': 'User rejected'}
        self.manager.show_approval_summary(decision)
        
        output = mock_stdout.getvalue()
        self.assertIn("❌ SERVER CONVERSION REJECTED", output)
        self.assertIn("User rejected", output)


class TestIntegrationFunction(unittest.TestCase):
    """Test the integration helper function"""
    
    def setUp(self):
        self.safe_candidate = self._create_test_candidate("safe_func", [])
        self.server_info = {
            'name': 'test-server',
            'repository': '/test/repo'
        }
    
    def _create_test_candidate(self, name: str, warnings: list):
        """Helper to create test candidates"""
        func = FunctionCandidate(
            function_name=name,
            file_path=f"/test/{name}.py",
            language="python",
            line_number=1,
            parameters=[],
            return_type="str",
            docstring=f"Test function {name}",
            source_code=f"def {name}():\n    return 'test'"
        )
        
        return MCPToolCandidate(
            function=func,
            mcp_score=7.5,
            description=f"Test {name} description",
            security_warnings=warnings,
            docker_requirements=[]
        )
    
    def test_integrate_approval_step_non_interactive(self):
        """Test integration function in non-interactive mode"""
        approved, candidates = integrate_approval_step(
            candidates=[self.safe_candidate],
            server_info=self.server_info,
            interactive=False
        )
        
        self.assertTrue(approved)
        self.assertEqual(len(candidates), 1)
    
    @patch('approval_flow.UserApprovalManager.request_approval')
    @patch('approval_flow.UserApprovalManager.show_approval_summary')
    def test_integrate_approval_step_interactive_approve(self, mock_summary, mock_request):
        """Test integration function in interactive mode - approve"""
        mock_request.return_value = {
            'approved': True,
            'candidates': [self.safe_candidate],
            'metadata': {'risk_acknowledged': False}
        }
        
        approved, candidates = integrate_approval_step(
            candidates=[self.safe_candidate],
            server_info=self.server_info,
            interactive=True
        )
        
        self.assertTrue(approved)
        self.assertEqual(len(candidates), 1)
        mock_request.assert_called_once()
        mock_summary.assert_called_once()
    
    @patch('approval_flow.UserApprovalManager.request_approval')
    @patch('approval_flow.UserApprovalManager.show_approval_summary')
    def test_integrate_approval_step_interactive_reject(self, mock_summary, mock_request):
        """Test integration function in interactive mode - reject"""
        mock_request.return_value = {
            'approved': False,
            'reason': 'User rejected',
            'metadata': {'timestamp': '2025-09-06T12:00:00'}
        }
        
        approved, candidates = integrate_approval_step(
            candidates=[self.safe_candidate],
            server_info=self.server_info,
            interactive=True
        )
        
        self.assertFalse(approved)
        self.assertEqual(len(candidates), 0)
        mock_request.assert_called_once()
        mock_summary.assert_called_once()


def test_approval_workflow_basic():
    """Basic integration test of approval workflow components"""
    print("=== Testing Approval Workflow Components ===")
    
    # Test SecurityRiskDisplayer
    print("Testing SecurityRiskDisplayer...")
    displayer = SecurityRiskDisplayer()
    
    func = FunctionCandidate(
        function_name="test_function",
        file_path="/test/test.py",
        language="python",
        line_number=1,
        parameters=[],
        return_type="str",
        docstring="Test function",
        source_code="def test_function():\n    return 'hello'"
    )
    
    candidate = MCPToolCandidate(
        function=func,
        mcp_score=8.0,
        description="Test function for approval",
        security_warnings=[],
        docker_requirements=[]
    )
    
    # This should show safe functions
    displayer.show_risk_summary([candidate])
    
    print("✅ SecurityRiskDisplayer test passed")
    
    # Test risk explanation
    explanation = displayer.get_risk_explanation('system_commands')
    assert "System command execution" in explanation
    print("✅ Risk explanation test passed")
    
    print("=== All approval workflow component tests passed! ===")


def run_manual_tests():
    """Run manual tests that require user interaction"""
    print("=== Manual Tests (require user interaction) ===")
    print("These tests will prompt for input. Press Ctrl+C to skip.")
    
    try:
        # Test interactive prompts
        prompts = InteractivePrompts()
        print("\nTesting InteractivePrompts.show_help()...")
        prompts.show_help()
        
        print("\nTesting approval decision (enter 'help' to see options, then 'n' to continue)...")
        decision = prompts.get_approval_decision()
        print(f"You chose: {decision}")
        
    except KeyboardInterrupt:
        print("\nManual tests skipped by user.")


if __name__ == "__main__":
    print("Running Approval Flow Tests...")
    
    # Run automated tests
    test_approval_workflow_basic()
    
    # Run unit tests
    print("\n=== Running Unit Tests ===")
    unittest.main(argv=[''], exit=False, verbosity=2)
    
    print("\n=== All Tests Complete ===")
    print("To run manual interactive tests, call run_manual_tests()")