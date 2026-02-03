#!/usr/bin/env python3
"""Test script to verify the enhanced consent handler functionality."""

import sys


def test_consent_button_texts():
    """Test that CONSENT_BUTTON_TEXTS has been enhanced."""
    print("\n=== Testing Enhanced CONSENT_BUTTON_TEXTS ===")
    
    with open('advanced_bot.py', 'r') as f:
        content = f.read()
    
    # Check for new consent button texts
    new_texts = ['okay', 'yes', 'allow', 'enable', 'confirm', 'proceed']
    found_count = 0
    
    for text in new_texts:
        if f"'{text}'" in content.lower() or f'"{text}"' in content.lower():
            found_count += 1
            print(f"✓ Found enhanced text: '{text}'")
    
    if found_count >= 4:
        print(f"\n✅ CONSENT_BUTTON_TEXTS enhanced ({found_count}/{len(new_texts)} new texts found)")
        return True
    else:
        print(f"\n❌ CONSENT_BUTTON_TEXTS not sufficiently enhanced ({found_count}/{len(new_texts)} found)")
        return False


def test_consent_manager_strategies():
    """Test that ConsentManager has multiple detection strategies."""
    print("\n=== Testing ConsentManager Strategies ===")
    
    with open('advanced_bot.py', 'r') as f:
        content = f.read()
    
    strategies = [
        ('_handle_text_based_buttons', 'Text-based button detection'),
        ('_handle_role_based_dialogs', 'Role-based dialog detection'),
        ('_handle_css_class_based_popups', 'CSS class-based detection'),
        ('_handle_iframe_consents', 'iFrame consent handling'),
        ('_handle_modal_overlays', 'Modal overlay handling'),
        ('_handle_shadow_dom_consents', 'Shadow DOM handling'),
        ('continuous_consent_monitoring', 'Continuous monitoring')
    ]
    
    found_strategies = []
    missing_strategies = []
    
    for method_name, description in strategies:
        if f'async def {method_name}' in content:
            found_strategies.append(description)
            print(f"✓ Found strategy: {description}")
        else:
            missing_strategies.append(description)
            print(f"✗ Missing strategy: {description}")
    
    if len(found_strategies) >= 6:
        print(f"\n✅ ConsentManager has {len(found_strategies)}/{len(strategies)} strategies")
        return True
    else:
        print(f"\n❌ ConsentManager missing strategies ({len(found_strategies)}/{len(strategies)} found)")
        return False


def test_search_visit_consent():
    """Test that consent handling is integrated in search visit."""
    print("\n=== Testing Search Visit Consent Integration ===")
    
    with open('advanced_bot.py', 'r') as f:
        content = f.read()
    
    # Look for consent handling in handle_search_visit
    search_visit_start = content.find('async def handle_search_visit')
    if search_visit_start == -1:
        print("❌ handle_search_visit function not found")
        return False
    
    # Get the function content (approximately)
    search_visit_section = content[search_visit_start:search_visit_start + 15000]
    
    checks = [
        ('temp_consent_manager = ConsentManager', 'Creates temporary consent manager'),
        ('handle_consents(page', 'Calls handle_consents'),
        ('Checking target domain for consent', 'Logs consent checking')
    ]
    
    passed = 0
    for check_text, description in checks:
        if check_text in search_visit_section:
            print(f"✓ {description}")
            passed += 1
        else:
            print(f"✗ {description} - NOT FOUND")
    
    if passed >= 2:
        print(f"\n✅ Search visit has consent integration ({passed}/{len(checks)} checks)")
        return True
    else:
        print(f"\n❌ Search visit missing consent integration ({passed}/{len(checks)} checks)")
        return False


def test_referral_visit_consent():
    """Test that consent handling is integrated in referral visit."""
    print("\n=== Testing Referral Visit Consent Integration ===")
    
    with open('advanced_bot.py', 'r') as f:
        content = f.read()
    
    # Look for consent handling in handle_referral_visit
    referral_visit_start = content.find('async def handle_referral_visit')
    if referral_visit_start == -1:
        print("❌ handle_referral_visit function not found")
        return False
    
    # Get the function content
    referral_visit_section = content[referral_visit_start:referral_visit_start + 5000]
    
    checks = [
        ('temp_consent_manager = ConsentManager', 'Creates temporary consent manager'),
        ('handle_consents(page', 'Calls handle_consents'),
        ('Checking for consent popups on referral', 'Logs consent checking')
    ]
    
    passed = 0
    for check_text, description in checks:
        if check_text in referral_visit_section:
            print(f"✓ {description}")
            passed += 1
        else:
            print(f"✗ {description} - NOT FOUND")
    
    if passed >= 2:
        print(f"\n✅ Referral visit has consent integration ({passed}/{len(checks)} checks)")
        return True
    else:
        print(f"\n❌ Referral visit missing consent integration ({passed}/{len(checks)} checks)")
        return False


def test_continuous_monitoring():
    """Test that time_based_browsing has continuous consent monitoring."""
    print("\n=== Testing Continuous Consent Monitoring ===")
    
    with open('advanced_bot.py', 'r') as f:
        content = f.read()
    
    # Look for time_based_browsing modifications
    time_browsing_start = content.find('async def time_based_browsing')
    if time_browsing_start == -1:
        print("❌ time_based_browsing function not found")
        return False
    
    time_browsing_section = content[time_browsing_start:time_browsing_start + 3000]
    
    checks = [
        ('consent_manager=None', 'Accepts consent_manager parameter'),
        ('last_consent_check', 'Tracks last consent check time'),
        ('consent_manager and (time.time() - last_consent_check)', 'Periodic consent checking logic'),
        ('handle_consents(page, max_retries=1)', 'Calls handle_consents during browsing')
    ]
    
    passed = 0
    for check_text, description in checks:
        if check_text in time_browsing_section:
            print(f"✓ {description}")
            passed += 1
        else:
            print(f"✗ {description} - NOT FOUND")
    
    if passed >= 3:
        print(f"\n✅ Continuous consent monitoring implemented ({passed}/{len(checks)} checks)")
        return True
    else:
        print(f"\n❌ Continuous monitoring not properly implemented ({passed}/{len(checks)} checks)")
        return False


def main():
    """Run all tests."""
    print("="*70)
    print("ADVANCED CONSENT HANDLER - COMPREHENSIVE TEST")
    print("="*70)
    
    results = []
    
    # Run all tests
    results.append(('Enhanced Button Texts', test_consent_button_texts()))
    results.append(('ConsentManager Strategies', test_consent_manager_strategies()))
    results.append(('Search Visit Integration', test_search_visit_consent()))
    results.append(('Referral Visit Integration', test_referral_visit_consent()))
    results.append(('Continuous Monitoring', test_continuous_monitoring()))
    
    # Summary
    print("\n" + "="*70)
    print("TEST SUMMARY")
    print("="*70)
    
    passed_count = sum(1 for _, result in results if result)
    total_count = len(results)
    
    for test_name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{test_name:.<50} {status}")
    
    print("="*70)
    print(f"Total: {passed_count}/{total_count} tests passed")
    print("="*70)
    
    if passed_count == total_count:
        print("\n🎉 All tests passed! Consent handler is fully enhanced.")
        return 0
    else:
        print(f"\n⚠️  {total_count - passed_count} test(s) failed. Review implementation.")
        return 1


if __name__ == '__main__':
    sys.exit(main())
