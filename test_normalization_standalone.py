#!/usr/bin/env python3
"""
Test RPA Script Normalization - Standalone version
Tests that JSON scripts with alternative action names and structures are properly normalized.
"""

import json
from typing import Dict, Any


def normalize_action_type(action_type: str) -> str:
    """
    Normalize action type names to internal format.
    Supports multiple naming conventions for compatibility.
    """
    # Mapping of alternative names to internal names
    type_aliases = {
        # Alternative naming conventions
        'gotoUrl': 'navigate',
        'goto': 'navigate',
        'gotoURL': 'navigate',
        'goToUrl': 'navigate',
        'openUrl': 'navigate',
        
        'waitTime': 'wait',
        'waitFor': 'wait',
        'delay': 'wait',
        'sleep': 'wait',
        'pause': 'wait',
        
        'scrollPage': 'scroll',
        'pageScroll': 'scroll',
        'scrollTo': 'scroll',
        
        'clickElement': 'click',
        'clickOn': 'click',
        
        'inputText': 'input',
        'typeText': 'input',
        'enterText': 'input',
        
        'openPage': 'newPage',
        'createPage': 'newPage',
        'newTab': 'newPage',
        'openTab': 'newPage',
        
        'close': 'closePage',
        'closeCurrentPage': 'closePage',
    }
    
    # Return normalized type or original if not found
    return type_aliases.get(action_type, action_type)


def normalize_step_config(step_type: str, config: Dict[str, Any]) -> Dict[str, Any]:
    """
    Normalize step configuration to internal format.
    Handles different property naming conventions.
    """
    normalized = {}
    
    # Handle navigate/gotoUrl action
    if step_type == 'navigate':
        normalized['url'] = config.get('url', config.get('URL', ''))
        normalized['timeout'] = config.get('timeout', config.get('timeOut', 30000))
    
    # Handle wait/waitTime action
    elif step_type == 'wait':
        # Support different timeout naming
        timeout = config.get('timeout', config.get('timeOut', config.get('duration', 1000)))
        
        # Check if it's a range-based wait
        timeout_type = config.get('timeoutType', config.get('type', 'fixedValue'))
        
        if timeout_type == 'fixedValue' or timeout_type == 'Fixed':
            normalized['duration'] = timeout
            normalized['min_duration'] = timeout
            normalized['max_duration'] = timeout
        else:
            # Random range
            normalized['duration'] = timeout
            normalized['min_duration'] = config.get('timeoutMin', config.get('min_duration', timeout))
            normalized['max_duration'] = config.get('timeoutMax', config.get('max_duration', timeout))
        
        normalized['mode'] = 'Fixed' if timeout_type == 'fixedValue' else 'Random'
    
    # Handle scroll/scrollPage action
    elif step_type == 'scroll':
        # Determine scroll position
        position = config.get('position', 'Intermediate')
        scroll_type_value = config.get('scrollType', config.get('type', 'position'))
        
        if position == 'bottom':
            normalized['depth'] = 100
            normalized['position'] = 'Bottom'
        elif position == 'top':
            normalized['depth'] = 0
            normalized['position'] = 'Top'
        else:
            normalized['depth'] = config.get('depth', config.get('distance', 50))
            normalized['position'] = position.capitalize() if position else 'Intermediate'
        
        # Handle scroll type
        scroll_type = config.get('type', 'smooth')
        normalized['scroll_type'] = scroll_type.capitalize() if scroll_type else 'Smooth'
        
        # Speed settings
        normalized['min_speed'] = config.get('min_speed', 100)
        normalized['max_speed'] = config.get('max_speed', 500)
    
    # Handle click action
    elif step_type == 'click':
        normalized['selector'] = config.get('selector', '')
        normalized['confidence'] = config.get('confidence', 0.8)
    
    # Handle input action
    elif step_type == 'input':
        normalized['selector'] = config.get('selector', '')
        normalized['text'] = config.get('text', config.get('value', ''))
        normalized['typing_delay'] = config.get('typing_delay', config.get('typingDelay', 100))
    
    # For other actions or unmapped properties, copy all config as-is
    else:
        normalized = config.copy()
    
    # Preserve any additional properties not specifically mapped
    # IMPORTANT: Don't preserve 'type' as it may conflict with step type
    for key, value in config.items():
        if key not in normalized and key not in ['remark', 'description', 'type']:
            normalized[key] = value
    
    return normalized


def normalize_rpa_script(data: Any) -> Dict[str, Any]:
    """
    Normalize RPA script JSON to internal format.
    Handles multiple input formats:
    1. Array of steps with config objects
    2. Object with steps array
    3. Mixed formats
    """
    # If input is a list (array format), wrap it
    if isinstance(data, list):
        steps_data = data
    elif isinstance(data, dict):
        # If it already has 'steps', use it
        if 'steps' in data:
            steps_data = data['steps']
        else:
            # Single step object
            steps_data = [data]
    else:
        # Invalid format
        return {'name': 'Invalid Script', 'steps': []}
    
    # Normalize each step
    normalized_steps = []
    for step_data in steps_data:
        # Get the original type
        original_type = step_data.get('type', '')
        
        # Normalize the type
        step_type = normalize_action_type(original_type)
        
        # Get config (might be nested or flat)
        if 'config' in step_data:
            config = step_data.get('config', {})
        else:
            # Config is flat (properties at step level)
            config = {k: v for k, v in step_data.items() if k != 'type'}
        
        # Normalize the config
        normalized_config = normalize_step_config(step_type, config)
        
        # Create normalized step
        normalized_step = {
            'type': step_type,
            **normalized_config
        }
        
        normalized_steps.append(normalized_step)
    
    # Return in expected format
    return {
        'name': data.get('name', 'Loaded Script') if isinstance(data, dict) else 'Loaded Script',
        'description': data.get('description', 'Script loaded from JSON') if isinstance(data, dict) else 'Script loaded from JSON',
        'steps': normalized_steps
    }


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
    
    # Print normalized result for inspection
    print("\nNormalized script:")
    print(json.dumps(result, indent=2))


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
        import traceback
        traceback.print_exc()
        return False
    except Exception as e:
        print(f"\n✗ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == '__main__':
    import sys
    success = run_all_tests()
    sys.exit(0 if success else 1)
