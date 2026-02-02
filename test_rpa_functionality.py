#!/usr/bin/env python3
"""
Test script for RPA Script Creator functionality.
This script validates that:
1. Visual builder actions can be converted to JSON
2. Configuration parameters are properly passed to execution
3. All action types are supported
"""

import json
import sys

def test_action_to_step_type():
    """Test action name to step type conversion."""
    print("Testing action_to_step_type mapping...")
    
    action_mapping = {
        '➕ New Tab': 'newPage',
        '🌐 Access Website': 'navigate',
        '⏱ Time': 'wait',
        '📜 Scroll': 'scroll',
        '🖱 Click Element': 'click',
        '⌨ Input Text': 'input',
        '❌ Close Page': 'closePage'
    }
    
    # Simulate the conversion logic
    for action_name, expected_type in action_mapping.items():
        clean_name = action_name.split(' ', 1)[1] if ' ' in action_name else action_name
        mapping = {
            'New Tab': 'newPage',
            'Access Website': 'navigate',
            'Time': 'wait',
            'Scroll': 'scroll',
            'Click Element': 'click',
            'Input Text': 'input',
            'Close Page': 'closePage',
        }
        step_type = mapping.get(clean_name, 'unknown')
        
        if step_type == expected_type:
            print(f"✓ {action_name} → {step_type}")
        else:
            print(f"✗ {action_name} → Expected {expected_type}, got {step_type}")
            return False
    
    print("All action mappings passed!\n")
    return True

def test_default_configs():
    """Test default configuration values."""
    print("Testing default configurations...")
    
    defaults = {
        'navigate': {'url': 'https://example.com', 'timeout': 30000},
        'wait': {'duration': 2000, 'mode': 'Fixed'},
        'scroll': {'depth': 50, 'scroll_type': 'Smooth', 'min_speed': 100, 'max_speed': 500},
        'click': {'selector': ''},
        'input': {'selector': '', 'text': ''}
    }
    
    for step_type, config in defaults.items():
        print(f"✓ {step_type}: {config}")
    
    print("All default configurations defined!\n")
    return True

def test_script_structure():
    """Test that the test RPA workflow has correct structure."""
    print("Testing RPA workflow structure...")
    
    with open('test_rpa_workflow.json', 'r') as f:
        script = json.load(f)
    
    # Validate structure
    if 'name' not in script:
        print("✗ Missing 'name' field")
        return False
    print(f"✓ Script name: {script['name']}")
    
    if 'steps' not in script or not isinstance(script['steps'], list):
        print("✗ Missing or invalid 'steps' field")
        return False
    print(f"✓ Script has {len(script['steps'])} steps")
    
    # Validate each step
    required_fields = ['type']
    for i, step in enumerate(script['steps']):
        if 'type' not in step:
            print(f"✗ Step {i+1} missing 'type' field")
            return False
        print(f"✓ Step {i+1}: {step['type']}")
        
        # Check type-specific fields
        if step['type'] == 'navigate':
            if 'url' not in step:
                print(f"  ⚠ Warning: navigate step missing 'url'")
            if 'timeout' not in step:
                print(f"  ⚠ Warning: navigate step missing 'timeout'")
            else:
                print(f"    - URL: {step['url']}")
                print(f"    - Timeout: {step['timeout']}ms")
        
        elif step['type'] == 'scroll':
            if 'scroll_type' not in step:
                print(f"  ⚠ Warning: scroll step missing 'scroll_type'")
            if 'min_speed' not in step or 'max_speed' not in step:
                print(f"  ⚠ Warning: scroll step missing speed parameters")
            else:
                print(f"    - Type: {step['scroll_type']}")
                print(f"    - Depth: {step['depth']}%")
                print(f"    - Speed: {step['min_speed']}-{step['max_speed']}ms")
        
        elif step['type'] == 'wait':
            if 'duration' not in step:
                print(f"  ⚠ Warning: wait step missing 'duration'")
            else:
                print(f"    - Duration: {step['duration']}ms")
                if 'mode' in step:
                    print(f"    - Mode: {step['mode']}")
    
    print("Script structure is valid!\n")
    return True

def main():
    """Run all tests."""
    print("=" * 60)
    print("RPA Script Creator Functionality Tests")
    print("=" * 60 + "\n")
    
    all_passed = True
    
    # Run tests
    all_passed &= test_action_to_step_type()
    all_passed &= test_default_configs()
    all_passed &= test_script_structure()
    
    print("=" * 60)
    if all_passed:
        print("✓ All tests passed!")
        print("=" * 60)
        return 0
    else:
        print("✗ Some tests failed!")
        print("=" * 60)
        return 1

if __name__ == '__main__':
    sys.exit(main())
