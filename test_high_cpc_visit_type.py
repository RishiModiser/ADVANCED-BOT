#!/usr/bin/env python3
"""
Test for HIGH CPC/CPM Visit Type Radio Button implementation.
Validates that HIGH CPC mode is now integrated as a Visit Type option.
"""

import sys
import re


def test_high_cpc_radio_button_exists():
    """Test that HIGH CPC/CPM radio button was added to Visit Type section."""
    print("Testing HIGH CPC/CPM radio button exists...")
    
    with open('advanced_bot.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check for HIGH CPC radio button
    if 'self.visit_high_cpc_radio = QRadioButton' in content:
        print("✓ HIGH CPC/CPM radio button found")
        
        # Check that it's added to button group
        if 'self.visit_type_group.addButton(self.visit_high_cpc_radio' in content:
            print("✓ HIGH CPC radio button added to visit type button group")
        else:
            print("✗ HIGH CPC radio button NOT added to button group")
            return False
        
        # Check that it's added to layout
        if 'visit_type_layout.addWidget(self.visit_high_cpc_radio)' in content:
            print("✓ HIGH CPC radio button added to layout")
        else:
            print("✗ HIGH CPC radio button NOT added to layout")
            return False
        
        return True
    else:
        print("✗ HIGH CPC/CPM radio button NOT found")
        return False


def test_high_cpc_toggle_function_exists():
    """Test that toggle_high_cpc_section function exists."""
    print("\nTesting HIGH CPC toggle function...")
    
    with open('advanced_bot.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    if 'def toggle_high_cpc_section' in content:
        print("✓ toggle_high_cpc_section function found")
        
        # Check key functionality
        func_start = content.find('def toggle_high_cpc_section')
        func_content = content[func_start:func_start + 1000]
        
        checks = [
            'self.high_cpc_group.setVisible(checked)' in func_content,
            'self.url_group.setVisible(False)' in func_content,
            'if checked:' in func_content,
        ]
        
        passed = sum(checks)
        if passed >= 2:
            print(f"✓ Toggle function has proper functionality ({passed}/3 checks)")
            return True
        else:
            print(f"✗ Toggle function incomplete ({passed}/3 checks)")
            return False
    else:
        print("✗ toggle_high_cpc_section function NOT found")
        return False


def test_radio_button_connected_to_toggle():
    """Test that HIGH CPC radio button is connected to toggle function."""
    print("\nTesting radio button connection...")
    
    with open('advanced_bot.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    if 'self.visit_high_cpc_radio.toggled.connect(self.toggle_high_cpc_section)' in content:
        print("✓ HIGH CPC radio button connected to toggle function")
        return True
    else:
        print("✗ HIGH CPC radio button NOT connected to toggle function")
        return False


def test_checkbox_removed():
    """Test that the old checkbox was removed."""
    print("\nTesting old checkbox removal...")
    
    with open('advanced_bot.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check that old checkbox initialization is removed
    if 'self.high_cpc_enabled = QCheckBox' in content:
        print("✗ Old HIGH CPC checkbox still exists (should be removed)")
        return False
    else:
        print("✓ Old HIGH CPC checkbox removed")
        return True


def test_high_cpc_group_hidden_by_default():
    """Test that HIGH CPC group is hidden by default."""
    print("\nTesting HIGH CPC group visibility...")
    
    with open('advanced_bot.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Find the HIGH CPC group section
    if 'self.high_cpc_group.setVisible(False)' in content:
        print("✓ HIGH CPC group is hidden by default")
        return True
    else:
        print("✗ HIGH CPC group NOT set to hidden by default")
        return False


def test_validation_uses_radio_button():
    """Test that validation logic uses radio button instead of checkbox."""
    print("\nTesting validation logic...")
    
    with open('advanced_bot.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check for visit_type = 'high_cpc'
    if "visit_type = 'high_cpc'" in content:
        print("✓ Validation uses visit_type='high_cpc'")
        
        # Check that it checks the radio button
        if 'self.visit_high_cpc_radio.isChecked()' in content:
            print("✓ Validation checks HIGH CPC radio button")
            return True
        else:
            print("✗ Validation does NOT check HIGH CPC radio button")
            return False
    else:
        print("✗ visit_type='high_cpc' NOT found in validation")
        return False


def test_url_hiding_behavior():
    """Test that URL section is hidden when HIGH CPC is selected."""
    print("\nTesting URL hiding behavior...")
    
    with open('advanced_bot.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Find toggle_high_cpc_section function
    func_start = content.find('def toggle_high_cpc_section')
    if func_start == -1:
        print("✗ toggle_high_cpc_section function not found")
        return False
    
    func_content = content[func_start:func_start + 1000]
    
    # Check that URL group is hidden when HIGH CPC is checked
    checks = [
        'if checked:' in func_content,
        'self.url_group.setVisible(False)' in func_content,
    ]
    
    if all(checks):
        print("✓ URL section is properly hidden when HIGH CPC is selected")
        return True
    else:
        print("✗ URL hiding behavior incomplete")
        return False


def test_high_cpc_validation():
    """Test that HIGH CPC fields are validated."""
    print("\nTesting HIGH CPC field validation...")
    
    with open('advanced_bot.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check for validation of HIGH CPC fields
    checks = [
        'high_cpc_url = self.high_cpc_url_input.text().strip()' in content,
        'high_cpc_target = self.high_cpc_target_input.text().strip()' in content,
        "'Please enter a High CPC Website URL" in content,
        "'Please enter a Target Domain URL" in content,
    ]
    
    passed = sum(checks)
    if passed >= 3:
        print(f"✓ HIGH CPC field validation implemented ({passed}/4 checks)")
        return True
    else:
        print(f"✗ HIGH CPC validation incomplete ({passed}/4 checks)")
        return False


def main():
    """Run all tests."""
    print("="*70)
    print("HIGH CPC/CPM Visit Type Radio Button Test Suite")
    print("="*70)
    
    tests = [
        test_high_cpc_radio_button_exists,
        test_high_cpc_toggle_function_exists,
        test_radio_button_connected_to_toggle,
        test_checkbox_removed,
        test_high_cpc_group_hidden_by_default,
        test_validation_uses_radio_button,
        test_url_hiding_behavior,
        test_high_cpc_validation,
    ]
    
    results = []
    for test in tests:
        try:
            result = test()
            results.append(result)
        except Exception as e:
            print(f"✗ Test failed with error: {e}")
            results.append(False)
    
    print("\n" + "="*70)
    print(f"Test Results: {sum(results)}/{len(results)} tests passed")
    print("="*70)
    
    if all(results):
        print("\n✅ All tests PASSED! HIGH CPC/CPM Visit Type implementation is complete.")
        return 0
    else:
        print(f"\n⚠ Some tests failed. Review the implementation.")
        return 1


if __name__ == '__main__':
    sys.exit(main())
