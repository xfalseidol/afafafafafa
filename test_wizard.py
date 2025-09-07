#!/usr/bin/env python3
"""
Test script for the enhanced EcommerceTester wizard functionality.
This test mocks playwright dependencies to focus on testing the wizard improvements.
"""

import sys
import unittest.mock
from io import StringIO

# Mock playwright before importing stuff
sys.modules['playwright'] = unittest.mock.MagicMock()
sys.modules['playwright.sync_api'] = unittest.mock.MagicMock()

import stuff

class TestEcommerceWizard:
    def __init__(self):
        self.tester = stuff.EcommerceTester()
        
    def test_validation_functions(self):
        """Test all validation functions work correctly"""
        print("🧪 Testing validation functions...")
        
        # Test email validation
        assert self.tester.validate_email('test@example.com') == True
        assert 'valid email' in self.tester.validate_email('invalid-email')
        assert 'valid email' in self.tester.validate_email('test@')
        print("   ✅ Email validation works")
        
        # Test positive integer validation
        assert self.tester.validate_positive_integer('5') == True
        assert self.tester.validate_positive_integer('100') == True
        assert 'positive number' in self.tester.validate_positive_integer('-1')
        assert 'positive number' in self.tester.validate_positive_integer('0')
        assert 'valid number' in self.tester.validate_positive_integer('abc')
        print("   ✅ Positive integer validation works")
        
        # Test non-empty validation
        assert self.tester.validate_non_empty('test') == True
        assert self.tester.validate_non_empty('   test   ') == True
        assert 'cannot be empty' in self.tester.validate_non_empty('')
        assert 'cannot be empty' in self.tester.validate_non_empty('   ')
        print("   ✅ Non-empty validation works")
        
        # Test credit card validation
        assert self.tester.validate_credit_card('4111111111111111') == True
        assert self.tester.validate_credit_card('4111-1111-1111-1111') == True
        assert self.tester.validate_credit_card('4111 1111 1111 1111') == True
        assert 'only digits' in self.tester.validate_credit_card('abc123')
        assert 'between 13-19 digits' in self.tester.validate_credit_card('123')
        print("   ✅ Credit card validation works")
        
        # Test expiry date validation
        assert self.tester.validate_expiry_date('12/25') == True
        assert self.tester.validate_expiry_date('01/30') == True
        assert 'MM/YY format' in self.tester.validate_expiry_date('13/25')
        assert 'MM/YY format' in self.tester.validate_expiry_date('12/2025')
        print("   ✅ Expiry date validation works")
        
        # Test CVV validation
        assert self.tester.validate_cvv('123') == True
        assert self.tester.validate_cvv('1234') == True
        assert 'only digits' in self.tester.validate_cvv('abc')
        assert '3 or 4 digits' in self.tester.validate_cvv('12345')
        print("   ✅ CVV validation works")
        
    def test_enhanced_help_system(self):
        """Test that help commands work"""
        print("🧪 Testing enhanced help system...")
        
        # Capture output to test help commands
        old_stdout = sys.stdout
        sys.stdout = captured_output = StringIO()
        
        try:
            self.tester.do_help_wizard('')
            help_output = captured_output.getvalue()
            
            # Check that help contains wizard information
            assert 'Interactive Wizard Help' in help_output
            assert 'login' in help_output.lower()
            assert 'add_to_cart' in help_output.lower() or 'add items' in help_output.lower()
            assert 'guided' in help_output.lower()
            print("   ✅ Help wizard command works")
            
        finally:
            sys.stdout = old_stdout
            
    def test_backwards_compatibility(self):
        """Test that existing command formats still work"""
        print("🧪 Testing backwards compatibility...")
        
        # Mock browser/page to avoid playwright dependency
        self.tester.browser = unittest.mock.MagicMock()
        self.tester.page = unittest.mock.MagicMock()
        self.tester.page.url = "https://example.com/dashboard"
        self.tester.page.query_selector.return_value.inner_text.return_value = "In Stock"
        
        old_stdout = sys.stdout
        sys.stdout = captured_output = StringIO()
        
        try:
            # Test login with both parameters (should not prompt)
            self.tester.do_login('test@example.com mypassword')
            output = captured_output.getvalue()
            # Should not contain prompts since both params provided
            assert 'Login Wizard' not in output
            
            # Reset capture
            sys.stdout = captured_output = StringIO()
            
            # Test add_to_cart with both parameters
            self.tester.state['logged_in'] = True
            self.tester.do_add_to_cart('PROD123 5')
            output = captured_output.getvalue()
            assert 'Add to Cart Wizard' not in output
            
            print("   ✅ Backwards compatibility maintained")
            
        finally:
            sys.stdout = old_stdout
    
    def test_new_wizard_features(self):
        """Test that new wizard features are available"""
        print("🧪 Testing new wizard features...")
        
        # Check that methods exist
        assert hasattr(self.tester, 'prompt_for_input')
        assert hasattr(self.tester, 'confirm_action')
        assert hasattr(self.tester, 'do_wizard')
        assert hasattr(self.tester, 'do_help_wizard')
        
        # Check that new validation methods exist
        assert hasattr(self.tester, 'validate_credit_card')
        assert hasattr(self.tester, 'validate_expiry_date')
        assert hasattr(self.tester, 'validate_cvv')
        
        print("   ✅ All new wizard features are available")
        
    def run_all_tests(self):
        """Run all tests"""
        print("🚀 Starting EcommerceTester Wizard Tests\n")
        
        try:
            self.test_validation_functions()
            self.test_enhanced_help_system()
            self.test_backwards_compatibility()
            self.test_new_wizard_features()
            
            print(f"\n🎉 All tests passed! Enhanced wizard is working correctly.")
            return True
            
        except Exception as e:
            print(f"\n❌ Test failed: {e}")
            import traceback
            traceback.print_exc()
            return False

if __name__ == '__main__':
    tester = TestEcommerceWizard()
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)