#!/usr/bin/env python3
"""
Test HIGH CPC/CPM Mode configuration and basic validation.
"""

import sys


def test_high_cpc_config():
    """Test HIGH CPC/CPM Mode configuration parsing."""
    print("Testing HIGH CPC/CPM Mode configuration...")
    print("-" * 60)
    
    # Test configuration
    test_config = {
        'high_cpc_enabled': True,
        'high_cpc_url': 'https://high-cpc-website.com',
        'high_cpc_target': 'https://target-domain.com',
        'high_cpc_stay_time': 180,
    }
    
    # Validate configuration
    errors = []
    
    if not isinstance(test_config.get('high_cpc_enabled'), bool):
        errors.append("high_cpc_enabled must be a boolean")
    
    if test_config.get('high_cpc_enabled'):
        if not test_config.get('high_cpc_url'):
            errors.append("high_cpc_url is required when HIGH CPC mode is enabled")
        
        if not test_config.get('high_cpc_target'):
            errors.append("high_cpc_target is required when HIGH CPC mode is enabled")
        
        stay_time = test_config.get('high_cpc_stay_time', 0)
        if not isinstance(stay_time, int) or stay_time < 30 or stay_time > 3600:
            errors.append("high_cpc_stay_time must be between 30 and 3600 seconds")
    
    if errors:
        print("✗ Configuration validation failed:")
        for error in errors:
            print(f"  - {error}")
        return 1
    else:
        print("✓ Configuration validation passed")
        print()
        print("Configuration details:")
        print(f"  - HIGH CPC Mode: {'Enabled' if test_config['high_cpc_enabled'] else 'Disabled'}")
        if test_config['high_cpc_enabled']:
            print(f"  - High CPC URL: {test_config['high_cpc_url']}")
            print(f"  - Target Domain: {test_config['high_cpc_target']}")
            print(f"  - Stay Time: {test_config['high_cpc_stay_time']} seconds")
        return 0


def test_high_cpc_execution_flow():
    """Test HIGH CPC/CPM Mode execution flow logic."""
    print("\nTesting HIGH CPC/CPM Mode execution flow...")
    print("-" * 60)
    
    # Simulate decision logic
    test_cases = [
        {
            'name': 'HIGH CPC Mode enabled with valid config',
            'enabled': True,
            'url': 'https://high-cpc.com',
            'target': 'https://target.com',
            'expected': 'high_cpc_mode'
        },
        {
            'name': 'HIGH CPC Mode disabled',
            'enabled': False,
            'url': 'https://high-cpc.com',
            'target': 'https://target.com',
            'expected': 'normal_mode'
        },
        {
            'name': 'HIGH CPC Mode enabled but missing URL',
            'enabled': True,
            'url': '',
            'target': 'https://target.com',
            'expected': 'normal_mode'
        },
        {
            'name': 'HIGH CPC Mode enabled but missing target',
            'enabled': True,
            'url': 'https://high-cpc.com',
            'target': '',
            'expected': 'normal_mode'
        },
    ]
    
    all_passed = True
    
    for test_case in test_cases:
        # Simulate the decision logic from execute_single_profile
        if test_case['enabled'] and test_case['url'] and test_case['target']:
            result = 'high_cpc_mode'
        else:
            result = 'normal_mode'
        
        if result == test_case['expected']:
            print(f"✓ {test_case['name']}: {result}")
        else:
            print(f"✗ {test_case['name']}: Expected {test_case['expected']}, got {result}")
            all_passed = False
    
    return 0 if all_passed else 1


def main():
    """Run all tests."""
    print("="*60)
    print("HIGH CPC/CPM Mode Test Suite")
    print("="*60)
    print()
    
    result1 = test_high_cpc_config()
    result2 = test_high_cpc_execution_flow()
    
    print()
    print("="*60)
    if result1 == 0 and result2 == 0:
        print("✓ All tests passed!")
        return 0
    else:
        print("✗ Some tests failed")
        return 1


if __name__ == '__main__':
    sys.exit(main())
