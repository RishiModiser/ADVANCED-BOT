# HIGH CPC/CPM Mode Feature Documentation

## Overview

The HIGH CPC/CPM Mode is an advanced feature designed to simulate high-value traffic by combining High CPC (Cost Per Click) website interactions with target domain visits. This mode opens multiple tabs to interact with a High CPC website before visiting the target domain.

## Feature Location

The HIGH CPC/CPM Mode controls are located in the **Traffic Settings Layout** section of the bot's GUI, appearing after the Content Interaction percentage setting and before the Platform Selection section.

## UI Components

### 1. Enable Checkbox
- **Label**: "✅ Enable HIGH CPC/CPM Mode"
- **Default**: Disabled
- **Function**: When checked, activates HIGH CPC/CPM mode and enables input fields

### 2. High CPC Website URL
- **Label**: "High CPC Website URL:"
- **Type**: Text input field
- **Placeholder**: "https://high-cpc-website.com"
- **Purpose**: URL of the high CPC website to interact with in 4 tabs

### 3. Target Domain URL
- **Label**: "Target Domain URL:"
- **Type**: Text input field
- **Placeholder**: "https://target-domain.com"
- **Purpose**: URL of the target domain to visit in the 5th tab

### 4. Target Stay Time
- **Label**: "Target Stay Time (seconds):"
- **Type**: Spin box (30-3600 seconds)
- **Default**: 180 seconds (3 minutes)
- **Purpose**: Total time to spend on the target domain with interactions

## Execution Flow

When HIGH CPC/CPM Mode is enabled, the bot follows this detailed process:

### Phase 1: High CPC Website (4 Tabs)

#### Tab 1
1. Opens High CPC URL
2. Waits for page to fully load
3. Detects and accepts cookie popup if present
4. Immediately moves to Tab 2

#### Tab 2
1. Opens High CPC URL
2. Waits for page to properly reload (2 seconds)
3. Waits up to 20 seconds for cookie/consent popup
4. If popup appears, accepts it
5. If no popup within 20 seconds, moves to Tab 3

#### Tab 3
1. Opens High CPC URL
2. Waits for page to properly reload (2 seconds)
3. Waits up to 20 seconds for cookie/consent popup
4. If popup appears, accepts it
5. If no popup within 20 seconds, moves to Tab 4

#### Tab 4
1. Opens High CPC URL
2. Waits for page to fully reload (2 seconds)
3. Waits up to 10 seconds for cookie/consent popup
4. If popup appears, accepts it
5. Performs shopping interactions:
   - Looks for product buttons ("Add to Bag", "Add to Cart", "Shop Now", "Buy Now")
   - Clicks product button if found
   - Navigates to Cart/Bag
   - Proceeds to Checkout
   - Fills checkout form with random data:
     * Random name
     * Random address
     * Random city
     * Random state
     * Random postal code
     * Random country
     * Random phone number

### Phase 2: Target Domain (5th Tab)

1. Opens Target Domain URL in a new tab
2. Waits for page to fully load
3. Performs initial scrolling (40-80% depth)
4. Performs 1-2 random clicks on clickable elements
5. Waits until half of the stay time has passed
6. At half-time:
   - Performs scrolling (30-70% depth)
   - Performs 1-2 additional random clicks
7. Continues scrolling during remaining time
8. Closes all tabs after full stay time completes

### Phase 3: Cleanup

1. Closes all 4 High CPC tabs
2. Closes Target Domain tab
3. Returns control to concurrency manager
4. Process repeats based on concurrency settings

## Human-Like Behavior

The feature implements several human-like behaviors:

- **Random delays**: Between actions (500ms-2000ms)
- **Smooth scrolling**: Uses natural scroll patterns
- **Variable clicks**: Random number of clicks (1-2)
- **Form filling**: Uses realistic random data
- **Time distribution**: Interactions spread across stay time
- **Error tolerance**: Gracefully handles missing elements

## Configuration Integration

The HIGH CPC mode integrates with existing bot configuration:

- **Concurrency**: Respects the "Concurrent" setting for multiple profiles
- **Proxy Support**: Each profile can use a different proxy
- **Platform Selection**: Works with both Windows and Android platforms
- **Consent Handling**: Uses the existing ConsentManager for cookie popups

## Code Architecture

### Main Functions

1. **`execute_high_cpc_mode()`** - Main execution function
   - Location: `advanced_bot.py`, line ~19023
   - Handles all 5 tabs and orchestrates the entire flow

2. **`_fill_checkout_form()`** - Helper for form filling
   - Fills checkout forms with random realistic data
   - Supports multiple field types (name, address, city, state, etc.)

3. **`_perform_random_clicks()`** - Helper for clicking
   - Performs random clicks on visible clickable elements
   - Implements safety checks and error handling

4. **`toggle_high_cpc_inputs()`** - UI toggle function
   - Enables/disables input fields based on checkbox state

### Configuration Keys

```python
{
    'high_cpc_enabled': bool,       # Enable/disable mode
    'high_cpc_url': str,            # High CPC website URL
    'high_cpc_target': str,         # Target domain URL
    'high_cpc_stay_time': int,      # Stay time in seconds
}
```

## Testing

A test suite is provided in `test_high_cpc_mode.py` that validates:

1. Configuration parsing and validation
2. Execution flow decision logic
3. Edge cases (missing URLs, disabled mode, etc.)

Run tests with:
```bash
python3 test_high_cpc_mode.py
```

## Best Practices

1. **URL Format**: Always include protocol (https:// or http://)
2. **Stay Time**: Set appropriate stay time (minimum 30 seconds, recommended 180+)
3. **High CPC Sites**: Use reputable e-commerce or content sites
4. **Concurrency**: Start with lower concurrency (1-5) for testing
5. **Monitoring**: Watch logs to ensure proper execution

## Limitations

1. Shopping interactions depend on website structure
2. Some sites may have bot detection mechanisms
3. Form filling may not work on all checkout forms
4. Cookie popups must match common patterns to be detected

## Error Handling

The feature includes comprehensive error handling:

- Gracefully handles missing page elements
- Continues execution if shopping flow fails
- Logs all actions and errors for debugging
- Ensures proper cleanup of tabs even on errors

## Future Enhancements

Potential improvements for future versions:

1. Configurable number of High CPC tabs (currently fixed at 4)
2. Custom form data instead of random generation
3. More sophisticated shopping flow detection
4. Support for additional e-commerce platforms
5. Configurable click patterns and timing
