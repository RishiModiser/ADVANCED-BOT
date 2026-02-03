#!/usr/bin/env python3
"""
Test RPA Script Normalization
Tests that JSON scripts with alternative action names and structures are properly normalized.
"""

import json
import sys
from pathlib import Path

# Add parent directory to path to import from advanced_bot
sys.path.insert(0, str(Path(__file__).parent))

from advanced_bot import normalize_action_type, normalize_step_config, normalize_rpa_script


def test_action_type_normalization():
    """Test that alternative action type names are normalized correctly."""
    print("Testing action type normalization...")
    
    # Test gotoUrl variants
    assert normalize_action_type('gotoUrl') == 'navigate'
    assert normalize_action_type('goto') == 'navigate'
    assert normalize_action_type('gotoURL') == 'navigate'
    assert normalize_action_type('goToUrl') == 'navigate'
    
    # Test waitTime variants
    assert normalize_action_type('waitTime') == 'wait'
    assert normalize_action_type('waitFor') == 'wait'
    assert normalize_action_type('delay') == 'wait'
    
    # Test scrollPage variants
    assert normalize_action_type('scrollPage') == 'scroll'
    assert normalize_action_type('pageScroll') == 'scroll'
    
    # Test that normal types pass through
    assert normalize_action_type('navigate') == 'navigate'
    assert normalize_action_type('wait') == 'wait'
    assert normalize_action_type('scroll') == 'scroll'
    assert normalize_action_type('newPage') == 'newPage'
    
    print("✓ Action type normalization works correctly")


def test_navigate_config_normalization():
    """Test navigate/gotoUrl config normalization."""
    print("Testing navigate config normalization...")
    
    config = {
        "url": "https://example.com",
        "timeout": 30000,
        "remark": "test"
    }
    
    result = normalize_step_config('navigate', config)
    assert result['url'] == "https://example.com"
    assert result['timeout'] == 30000
    
    print("✓ Navigate config normalization works correctly")


def test_wait_config_normalization():
    """Test wait/waitTime config normalization."""
    print("Testing wait config normalization...")
    
    # Test fixed timeout
    config_fixed = {
        "timeoutType": "fixedValue",
        "timeout": 30000,
        "timeoutMin": 20000,
        "timeoutMax": 40000
    }
    
    result = normalize_step_config('wait', config_fixed)
    assert result['duration'] == 30000
    assert result['min_duration'] == 30000
    assert result['max_duration'] == 30000
    assert result['mode'] == 'Fixed'
    
    # Test random timeout
    config_random = {
        "timeoutType": "random",
        "timeout": 30000,
        "timeoutMin": 20000,
        "timeoutMax": 40000
    }
    
    result = normalize_step_config('wait', config_random)
    assert result['duration'] == 30000
    assert result['min_duration'] == 20000
    assert result['max_duration'] == 40000
    assert result['mode'] == 'Random'
    
    print("✓ Wait config normalization works correctly")


def test_scroll_config_normalization():
    """Test scroll/scrollPage config normalization."""
    print("Testing scroll config normalization...")
    
    # Test scroll to bottom
    config_bottom = {
        "position": "bottom",
        "type": "smooth"
    }
    
    result = normalize_step_config('scroll', config_bottom)
    assert result['depth'] == 100
    assert result['position'] == 'Bottom'
    assert result['scroll_type'] == 'Smooth'
    
    # Test scroll to top
    config_top = {
        "position": "top",
        "type": "smooth"
    }
    
    result = normalize_step_config('scroll', config_top)
    assert result['depth'] == 0
    assert result['position'] == 'Top'
    
    print("✓ Scroll config normalization works correctly")


def test_full_script_normalization():
    """Test full script normalization with the user's example."""
    print("Testing full script normalization...")
    
    # User's script format (array with config objects)
    user_script = [
        {
            "type": "newPage",
            "config": {}
        },
        {
            "type": "gotoUrl",
            "config": {
                "url": "https://zw.inatboxapk.biz/",
                "timeout": 30000,
                "remark": ""
            }
        },
        {
            "type": "waitTime",
            "config": {
                "timeoutType": "fixedValue",
                "timeout": 30000,
                "timeoutMin": 20000,
                "timeoutMax": 40000,
                "remark": ""
            }
        },
        {
            "type": "scrollPage",
            "config": {
                "position": "bottom",
                "type": "smooth"
            }
        }
    ]
    
    # Normalize
    result = normalize_rpa_script(user_script)
    
    # Verify structure
    assert 'name' in result
    assert 'steps' in result
    assert isinstance(result['steps'], list)
    assert len(result['steps']) == 4
    
    # Verify newPage step
    assert result['steps'][0]['type'] == 'newPage'
    
    # Verify navigate step (was gotoUrl)
    assert result['steps'][1]['type'] == 'navigate'
    assert result['steps'][1]['url'] == 'https://zw.inatboxapk.biz/'
    assert result['steps'][1]['timeout'] == 30000
    
    # Verify wait step (was waitTime)
    assert result['steps'][2]['type'] == 'wait'
    assert result['steps'][2]['duration'] == 30000
    assert result['steps'][2]['mode'] == 'Fixed'
    
    # Verify scroll step (was scrollPage)
    assert result['steps'][3]['type'] == 'scroll'
    assert result['steps'][3]['depth'] == 100
    assert result['steps'][3]['position'] == 'Bottom'
    
    print("✓ Full script normalization works correctly")
    print(f"  Normalized {len(result['steps'])} steps successfully")


def test_already_normalized_script():
    """Test that already normalized scripts pass through correctly."""
    print("Testing already normalized script...")
    
    # Already normalized format
    normalized_script = {
        "name": "Test Script",
        "description": "Test description",
        "steps": [
            {
                "type": "newPage"
            },
            {
                "type": "navigate",
                "url": "https://example.com",
                "timeout": 30000
            },
            {
                "type": "wait",
                "duration": 2000
            }
        ]
    }
    
    result = normalize_rpa_script(normalized_script)
    
    # Verify it's still valid
    assert result['name'] == 'Test Script'
    assert result['description'] == 'Test description'
    assert len(result['steps']) == 3
    assert result['steps'][0]['type'] == 'newPage'
    assert result['steps'][1]['type'] == 'navigate'
    assert result['steps'][2]['type'] == 'wait'
    
    print("✓ Already normalized script handled correctly")


def run_all_tests():
    """Run all normalization tests."""
    print("\n" + "="*60)
    print("RPA Script Normalization Tests")
    print("="*60 + "\n")
    
    try:
        test_action_type_normalization()
        test_navigate_config_normalization()
        test_wait_config_normalization()
        test_scroll_config_normalization()
        test_full_script_normalization()
        test_already_normalized_script()
        
        print("\n" + "="*60)
        print("✓ All tests passed!")
        print("="*60 + "\n")
        return True
        
    except AssertionError as e:
        print(f"\n✗ Test failed: {e}")
        return False
    except Exception as e:
        print(f"\n✗ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == '__main__':
    success = run_all_tests()
    sys.exit(0 if success else 1)
