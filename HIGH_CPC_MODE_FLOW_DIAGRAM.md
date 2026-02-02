# HIGH CPC/CPM Mode Visual Flow Diagram

```
┌─────────────────────────────────────────────────────────────────────────┐
│                        HIGH CPC/CPM MODE ENABLED                         │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                     PHASE 1: HIGH CPC WEBSITE (4 TABS)                  │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
        ┌───────────────────────────┼───────────────────────────┬─────────┐
        ▼                           ▼                           ▼         ▼
   ┌────────┐                  ┌────────┐                  ┌────────┐  ┌────────┐
   │ TAB 1  │                  │ TAB 2  │                  │ TAB 3  │  │ TAB 4  │
   └────────┘                  └────────┘                  └────────┘  └────────┘
        │                           │                           │         │
        ▼                           ▼                           ▼         ▼
   Load High CPC URL           Load High CPC URL          Load High CPC URL  Load High CPC URL
        │                           │                           │         │
        ▼                           ▼                           ▼         ▼
   Detect Cookie Popup         Wait for Page (2s)         Wait for Page (2s)  Wait for Page (2s)
        │                           │                           │         │
        ▼                           ▼                           ▼         ▼
   Click Accept/Allow          Wait for Cookie Popup      Wait for Cookie Popup  Wait for Cookie (10s)
        │                      (up to 20 seconds)         (up to 20 seconds)    │
        ▼                           │                           │         ▼
   Move to Tab 2                   ▼                           ▼    Shopping Interaction:
                              Accept if found             Accept if found      │
                                    │                           │         ├─ Click Product
                                    ▼                           ▼         ├─ Add to Bag/Cart
                              Move to Tab 3               Move to Tab 4   ├─ Go to Cart
                                                                          ├─ Checkout
                                                                          └─ Fill Form:
                                                                             • Name
                                                                             • Address
                                                                             • City/State
                                                                             • Postal Code
                                                                             • Phone
                                                                          
        └───────────────────────────┴───────────────────────────┴─────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                   PHASE 2: TARGET DOMAIN (5TH TAB)                       │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
                            Load Target Domain URL
                                    │
                                    ▼
                         Wait for Page to Fully Load
                                    │
                                    ▼
                        Scroll Up & Down (40-80% depth)
                                    │
                                    ▼
                    Perform 1-2 Random Clicks on Elements
                                    │
                                    ▼
                   ┌─────────────────────────────────┐
                   │  Wait Until Half of Stay Time   │
                   └─────────────────────────────────┘
                                    │
                                    ▼
                        Scroll Again (30-70% depth)
                                    │
                                    ▼
                    Perform 1-2 More Random Clicks
                                    │
                                    ▼
                   ┌─────────────────────────────────┐
                   │    Continue Scrolling Until     │
                   │    Full Stay Time Completes     │
                   └─────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                        PHASE 3: CLEANUP                                  │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                ┌───────────────────┼───────────────────┐
                ▼                   ▼                   ▼
           Close Tab 1          Close Tab 2        Close Tab 3
                │                   │                   │
                └───────────────────┼───────────────────┘
                                    │
                                    ▼
                            Close Tab 4 (Shopping)
                                    │
                                    ▼
                          Close Tab 5 (Target)
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│              Continue Based on Concurrency Settings                      │
│           (Process repeats for next profile if configured)               │
└─────────────────────────────────────────────────────────────────────────┘


═══════════════════════════════════════════════════════════════════════════
                            TIMING BREAKDOWN
═══════════════════════════════════════════════════════════════════════════

Tab 1:  Cookie handling (immediate)                          ~1-3 seconds
Tab 2:  Page load + cookie wait (up to 20s)                 ~2-22 seconds
Tab 3:  Page load + cookie wait (up to 20s)                 ~2-22 seconds
Tab 4:  Page load + cookie + shopping flow                  ~10-30 seconds
Tab 5:  Target domain full interaction                      User-defined stay time

Total Approximate Time per Profile: 15-77 seconds + Stay Time

═══════════════════════════════════════════════════════════════════════════
                          HUMAN-LIKE BEHAVIORS
═══════════════════════════════════════════════════════════════════════════

✓ Random delays between actions (500ms - 2000ms)
✓ Smooth scrolling with natural patterns
✓ Variable click count (1-2 clicks per phase)
✓ Realistic form data generation
✓ Time-distributed interactions
✓ Error-tolerant execution (graceful fallbacks)
✓ Natural mouse movements during scrolling
✓ Reading pauses between actions

═══════════════════════════════════════════════════════════════════════════
```

## Configuration Example

```python
config = {
    'high_cpc_enabled': True,
    'high_cpc_url': 'https://example-ecommerce.com',
    'high_cpc_target': 'https://your-target-domain.com',
    'high_cpc_stay_time': 180,  # 3 minutes
    'threads': 5,  # Run 5 concurrent profiles
    'platforms': ['windows'],  # Use Windows browser
    'proxy_enabled': True,  # Use proxies for each profile
}
```

## Execution Order

1. Bot checks if `high_cpc_enabled` is True
2. If enabled AND both URLs are provided:
   - Routes to `execute_high_cpc_mode()`
   - Skips normal visit execution
3. If disabled OR URLs missing:
   - Routes to normal visit execution
   - Continues with standard behavior

## Integration with Existing Features

| Feature | Integration |
|---------|-------------|
| Concurrency | Each profile runs HIGH CPC mode independently |
| Proxy Support | Each profile gets its own proxy |
| Platform Selection | HIGH CPC mode respects platform choice (Windows/Android) |
| Consent Manager | Uses existing cookie handling system |
| Human Behavior | Leverages existing HumanBehavior class methods |
| Logging | All actions logged with detailed messages |
