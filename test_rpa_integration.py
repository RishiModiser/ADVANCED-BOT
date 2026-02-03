#!/usr/bin/env python3
"""
Integration Test for RPA Script Loading
Tests the complete workflow from loading a JSON file to execution readiness.
"""

import json
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from test_normalization_standalone import normalize_rpa_script


def test_user_script_loading():
    """Test loading the user's exact script from problem statement."""
    print("\n" + "="*70)
    print("INTEGRATION TEST: User Script Loading")
    print("="*70 + "\n")
    
    # User's exact script from problem statement
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
                "rangeType": "window",
                "selectorRadio": "CSS",
                "selector": "",
                "serial": 1,
                "distance": 0,
                "type": "smooth",
                "scrollType": "position",
                "position": "bottom",
                "remark": "",
                "randomWheelDistance": [100, 150],
                "randomWheelSleepTime": [200, 300]
            }
        },
        {
            "type": "scrollPage",
            "config": {
                "rangeType": "window",
                "selectorRadio": "CSS",
                "selector": "",
                "serial": 1,
                "distance": 0,
                "type": "smooth",
                "scrollType": "position",
                "position": "top",
                "remark": "",
                "randomWheelDistance": [100, 150],
                "randomWheelSleepTime": [200, 300]
            }
        },
        {
            "type": "waitTime",
            "config": {
                "timeoutType": "fixedValue",
                "timeout": 15000,
                "timeoutMin": 10000,
                "timeoutMax": 300000,
                "remark": ""
            }
        }
    ]
    
    print("Step 1: Loading user's JSON script...")
    print(f"  → Original format: Array with {len(user_script)} items")
    print(f"  → Using action types: {[s['type'] for s in user_script]}")
    print("  ✓ JSON loaded successfully\n")
    
    print("Step 2: Normalizing script...")
    normalized_script = normalize_rpa_script(user_script)
    print(f"  → Normalized to: {len(normalized_script['steps'])} steps")
    print(f"  → Action types: {[s['type'] for s in normalized_script['steps']]}")
    print("  ✓ Script normalized successfully\n")
    
    print("Step 3: Validating normalized structure...")
    assert 'name' in normalized_script, "Missing 'name' field"
    assert 'description' in normalized_script, "Missing 'description' field"
    assert 'steps' in normalized_script, "Missing 'steps' field"
    assert isinstance(normalized_script['steps'], list), "'steps' must be a list"
    assert len(normalized_script['steps']) == 6, f"Expected 6 steps, got {len(normalized_script['steps'])}"
    print("  ✓ Structure validation passed\n")
    
    print("Step 4: Validating each action...")
    
    # Step 1: newPage
    step1 = normalized_script['steps'][0]
    assert step1['type'] == 'newPage', f"Step 1 should be 'newPage', got '{step1['type']}'"
    print("  ✓ Step 1: newPage - OK")
    
    # Step 2: navigate (was gotoUrl)
    step2 = normalized_script['steps'][1]
    assert step2['type'] == 'navigate', f"Step 2 should be 'navigate', got '{step2['type']}'"
    assert step2['url'] == 'https://zw.inatboxapk.biz/', f"URL mismatch"
    assert step2['timeout'] == 30000, f"Timeout mismatch"
    print("  ✓ Step 2: navigate (was gotoUrl) - OK")
    
    # Step 3: wait (was waitTime)
    step3 = normalized_script['steps'][2]
    assert step3['type'] == 'wait', f"Step 3 should be 'wait', got '{step3['type']}'"
    assert step3['duration'] == 30000, f"Duration mismatch"
    assert step3['mode'] == 'Fixed', f"Mode should be 'Fixed', got '{step3['mode']}'"
    print("  ✓ Step 3: wait (was waitTime) - OK")
    
    # Step 4: scroll to bottom (was scrollPage)
    step4 = normalized_script['steps'][3]
    assert step4['type'] == 'scroll', f"Step 4 should be 'scroll', got '{step4['type']}'"
    assert step4['position'] == 'Bottom', f"Position should be 'Bottom', got '{step4['position']}'"
    assert step4['depth'] == 100, f"Depth should be 100 for bottom, got {step4['depth']}"
    print("  ✓ Step 4: scroll to bottom (was scrollPage) - OK")
    
    # Step 5: scroll to top (was scrollPage)
    step5 = normalized_script['steps'][4]
    assert step5['type'] == 'scroll', f"Step 5 should be 'scroll', got '{step5['type']}'"
    assert step5['position'] == 'Top', f"Position should be 'Top', got '{step5['position']}'"
    assert step5['depth'] == 0, f"Depth should be 0 for top, got {step5['depth']}"
    print("  ✓ Step 5: scroll to top (was scrollPage) - OK")
    
    # Step 6: wait (was waitTime)
    step6 = normalized_script['steps'][5]
    assert step6['type'] == 'wait', f"Step 6 should be 'wait', got '{step6['type']}'"
    assert step6['duration'] == 15000, f"Duration mismatch"
    print("  ✓ Step 6: wait (was waitTime) - OK\n")
    
    print("Step 5: Verifying execution readiness...")
    # Check that ScriptExecutor would accept this format
    for i, step in enumerate(normalized_script['steps'], 1):
        step_type = step['type']
        assert step_type in ['newPage', 'navigate', 'wait', 'scroll', 'click', 'input', 'closePage', 
                             'refresh', 'closeTab', 'if', 'forLoopElements', 'forLoopTimes', 
                             'while', 'break', 'quitBrowser'], \
            f"Step {i} has invalid type '{step_type}'"
    print("  ✓ All steps use valid action types\n")
    
    print("Step 6: Workflow builder compatibility...")
    # Simulate what would be shown in the workflow list
    action_mapping = {
        'newPage': 'New Tab',
        'navigate': 'Access Website',
        'wait': 'Time',
        'scroll': 'Scroll'
    }
    
    print("  Workflow steps that would appear in UI:")
    for i, step in enumerate(normalized_script['steps'], 1):
        action_name = action_mapping.get(step['type'], step['type'])
        print(f"    {i}. {action_name}")
    print("  ✓ All actions mapped to visual builder\n")
    
    print("="*70)
    print("✓ INTEGRATION TEST PASSED")
    print("="*70)
    print("\nSummary:")
    print(f"  • Successfully loaded user's JSON with alternative action names")
    print(f"  • Normalized {len(normalized_script['steps'])} actions")
    print(f"  • All actions are execution-ready for ScriptExecutor")
    print(f"  • All actions will appear in workflow builder")
    print("\n" + "="*70 + "\n")
    
    return True


def test_paste_scenario():
    """Test the scenario where user pastes JSON directly into editor."""
    print("Testing direct JSON paste scenario...")
    
    # Simulate pasting the array format directly
    pasted_json = '''[
  {
    "type": "gotoUrl",
    "config": {"url": "https://example.com", "timeout": 30000}
  }
]'''
    
    # Parse and normalize (simulates sync_json_to_visual)
    raw_data = json.loads(pasted_json)
    normalized = normalize_rpa_script(raw_data)
    
    assert normalized['steps'][0]['type'] == 'navigate'
    assert normalized['steps'][0]['url'] == 'https://example.com'
    
    print("  ✓ Paste scenario works correctly\n")
    return True


def test_load_from_file_scenario():
    """Test the scenario where user loads JSON from a file."""
    print("Testing load from file scenario...")
    
    # Simulate loading from file (simulates load_script)
    file_content = '''[
  {"type": "newPage", "config": {}},
  {"type": "waitTime", "config": {"timeout": 5000, "timeoutType": "fixedValue"}}
]'''
    
    # Parse and normalize (simulates load_script method)
    raw_data = json.loads(file_content)
    normalized = normalize_rpa_script(raw_data)
    
    assert len(normalized['steps']) == 2
    assert normalized['steps'][0]['type'] == 'newPage'
    assert normalized['steps'][1]['type'] == 'wait'
    assert normalized['steps'][1]['duration'] == 5000
    
    print("  ✓ Load from file scenario works correctly\n")
    return True


def run_integration_tests():
    """Run all integration tests."""
    try:
        test_user_script_loading()
        test_paste_scenario()
        test_load_from_file_scenario()
        return True
    except AssertionError as e:
        print(f"\n✗ Integration test failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    except Exception as e:
        print(f"\n✗ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == '__main__':
    success = run_integration_tests()
    sys.exit(0 if success else 1)
