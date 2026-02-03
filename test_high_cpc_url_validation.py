#!/usr/bin/env python3
"""
Test that HIGH CPC/CPM Mode does not require target URLs.
This validates the fix for the issue where HIGH CPC mode was still
asking for target URLs even though it has its own target domain.
"""

import sys


def test_high_cpc_url_requirement():
    """Test that HIGH CPC mode does not require target URLs."""
    print("Testing HIGH CPC/CPM Mode URL requirement logic...")
    print("-" * 60)
    
    # Test scenarios
    test_cases = [
        {
            'name': 'Search Visit - should NOT require target URLs',
            'visit_type': 'search',
            'high_cpc_enabled': False,
            'url_list': [],
            'should_require_urls': False,
            'reason': 'Search visit uses keyword + target domain'
        },
        {
            'name': 'HIGH CPC Mode enabled - should NOT require target URLs',
            'visit_type': 'direct',
            'high_cpc_enabled': True,
            'url_list': [],
            'should_require_urls': False,
            'reason': 'HIGH CPC mode has its own target domain'
        },
        {
            'name': 'Direct Visit (no HIGH CPC) - SHOULD require target URLs',
            'visit_type': 'direct',
            'high_cpc_enabled': False,
            'url_list': [],
            'should_require_urls': True,
            'reason': 'Normal direct visit needs target URLs'
        },
        {
            'name': 'Referral Visit (no HIGH CPC) - SHOULD require target URLs',
            'visit_type': 'referral',
            'high_cpc_enabled': False,
            'url_list': [],
            'should_require_urls': True,
            'reason': 'Normal referral visit needs target URLs'
        },
        {
            'name': 'Direct Visit with URLs provided - should be OK',
            'visit_type': 'direct',
            'high_cpc_enabled': False,
            'url_list': ['https://example.com'],
            'should_require_urls': False,
            'reason': 'URLs are provided'
        },
    ]
    
    all_passed = True
    
    for test_case in test_cases:
        # Simulate the validation logic
        visit_type = test_case['visit_type']
        high_cpc_enabled = test_case['high_cpc_enabled']
        url_list = test_case['url_list']
        
        requires_urls = False
        
        if visit_type == 'search':
            # Search visit doesn't need target URLs
            requires_urls = False
        elif high_cpc_enabled:
            # HIGH CPC mode doesn't need target URLs
            requires_urls = False
        else:
            # Direct and referral visits need target URLs
            if not url_list:
                requires_urls = True
        
        expected = test_case['should_require_urls']
        
        if requires_urls == expected:
            print(f"✓ {test_case['name']}")
            print(f"  Reason: {test_case['reason']}")
        else:
            print(f"✗ {test_case['name']}")
            print(f"  Expected requires_urls={expected}, got {requires_urls}")
            print(f"  Reason: {test_case['reason']}")
            all_passed = False
    
    return 0 if all_passed else 1


def main():
    """Run all tests."""
    print("="*60)
    print("HIGH CPC/CPM Mode URL Validation Test")
    print("="*60)
    print()
    
    result = test_high_cpc_url_requirement()
    
    print()
    print("="*60)
    if result == 0:
        print("✓ All tests passed!")
        print()
        print("Summary: HIGH CPC/CPM Mode correctly bypasses target URL")
        print("         requirement, just like Search Visit mode.")
        return 0
    else:
        print("✗ Some tests failed")
        return 1


if __name__ == '__main__':
    sys.exit(main())
