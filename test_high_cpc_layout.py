#!/usr/bin/env python3
"""
Test to verify HIGH CPC/CPM Settings layout positioning.

This test verifies that the HIGH CPC/CPM Mode Settings section appears
in the correct position in the UI layout - after Search Settings and
before Traffic Settings, matching the behavior of Referral and Search settings.
"""

def test_high_cpc_layout_position():
    """Test that HIGH CPC/CPM settings are positioned correctly."""
    print("=" * 70)
    print("HIGH CPC/CPM Settings Layout Position Test")
    print("=" * 70)
    
    # Read the file
    with open('advanced_bot.py', 'r') as f:
        lines = f.readlines()
    
    # Find the layout additions
    layout_order = []
    for i, line in enumerate(lines, 1):
        if 'layout.addWidget(visit_type_group)' in line:
            layout_order.append(('visit_type_group', i))
        elif 'layout.addWidget(self.referral_group)' in line:
            layout_order.append(('referral_group', i))
        elif 'layout.addWidget(self.search_group)' in line:
            layout_order.append(('search_group', i))
        elif 'layout.addWidget(self.high_cpc_group)' in line:
            layout_order.append(('high_cpc_group', i))
        elif 'layout.addWidget(traffic_group)' in line:
            layout_order.append(('traffic_group', i))
        elif 'layout.addWidget(platform_group)' in line:
            layout_order.append(('platform_group', i))
    
    print("\nExpected UI Layout Order:")
    print("  1. Visit Type (radio buttons)")
    print("  2. Referral Settings (hidden by default)")
    print("  3. Search Settings (hidden by default)")
    print("  4. HIGH CPC/CPM Settings (hidden by default) ← SHOULD BE HERE")
    print("  5. Traffic Settings")
    print("  6. Platform Selection")
    
    print("\nActual Layout Order Found:")
    # Sort by line number to get actual order
    layout_order.sort(key=lambda x: x[1])
    for i, (group, line_num) in enumerate(layout_order, 1):
        marker = " ← HIGH CPC/CPM" if 'high_cpc' in group else ""
        print(f"  {i}. {group:25s} (line {line_num}){marker}")
    
    # Verify the order is correct
    try:
        visit_type_idx = next(i for i, (g, _) in enumerate(layout_order) if 'visit_type' in g)
        referral_idx = next(i for i, (g, _) in enumerate(layout_order) if 'referral' in g)
        search_idx = next(i for i, (g, _) in enumerate(layout_order) if 'search' in g)
        high_cpc_idx = next(i for i, (g, _) in enumerate(layout_order) if 'high_cpc' in g)
        traffic_idx = next(i for i, (g, _) in enumerate(layout_order) if 'traffic' in g)
        platform_idx = next(i for i, (g, _) in enumerate(layout_order) if 'platform' in g)
        
        # Check that the order is correct
        order_correct = (
            visit_type_idx < referral_idx < search_idx < high_cpc_idx < traffic_idx < platform_idx
        )
        
        if order_correct:
            print("\n" + "=" * 70)
            print("✓ TEST PASSED: HIGH CPC/CPM Settings are correctly positioned")
            print("=" * 70)
            print("\nBehavior:")
            print("  • HIGH CPC/CPM Settings now appear after Search Settings")
            print("  • HIGH CPC/CPM Settings now appear before Traffic Settings")
            print("  • This matches the layout pattern of Referral and Search settings")
            print("  • All settings (Referral, Search, HIGH CPC) are grouped together")
            print("  • Traffic Settings appear after all visit-type-specific settings")
            return True
        else:
            print("\n✗ TEST FAILED: Incorrect order")
            print(f"  Expected: visit_type < referral < search < high_cpc < traffic < platform")
            print(f"  Got: {visit_type_idx} < {referral_idx} < {search_idx} < {high_cpc_idx} < {traffic_idx} < {platform_idx}")
            return False
            
    except Exception as e:
        print(f"\n✗ TEST FAILED: {e}")
        return False

if __name__ == '__main__':
    success = test_high_cpc_layout_position()
    exit(0 if success else 1)
