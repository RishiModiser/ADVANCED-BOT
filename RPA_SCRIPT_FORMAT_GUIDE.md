# RPA Script Format Compatibility Guide

## Overview
The RPA Script Creator now supports multiple JSON formats and action naming conventions. This allows you to load scripts from different sources without modification.

## Supported JSON Formats

### Format 1: Standard Format (Already Supported)
```json
{
  "name": "My Script",
  "description": "Script description",
  "steps": [
    {
      "type": "navigate",
      "url": "https://example.com",
      "timeout": 30000
    }
  ]
}
```

### Format 2: Array Format with Config Objects (New)
```json
[
  {
    "type": "gotoUrl",
    "config": {
      "url": "https://example.com",
      "timeout": 30000
    }
  }
]
```

### Format 3: Simple Array Format (New)
```json
[
  {
    "type": "navigate",
    "url": "https://example.com",
    "timeout": 30000
  }
]
```

## Action Type Aliases

The following action type names are automatically converted to internal format:

### Navigate/Go to URL
- `gotoUrl` → `navigate`
- `goto` → `navigate`
- `gotoURL` → `navigate`
- `goToUrl` → `navigate`
- `openUrl` → `navigate`

### Wait/Delay
- `waitTime` → `wait`
- `waitFor` → `wait`
- `delay` → `wait`
- `sleep` → `wait`
- `pause` → `wait`

### Scroll Page
- `scrollPage` → `scroll`
- `pageScroll` → `scroll`
- `scrollTo` → `scroll`

### Click Element
- `clickElement` → `click`
- `clickOn` → `click`

### Input Text
- `inputText` → `input`
- `typeText` → `input`
- `enterText` → `input`

### New Page/Tab
- `openPage` → `newPage`
- `createPage` → `newPage`
- `newTab` → `newPage`
- `openTab` → `newPage`

### Close Page
- `close` → `closePage`
- `closeCurrentPage` → `closePage`

## Configuration Property Aliases

### Navigate Action
- `url` or `URL` → `url`
- `timeout` or `timeOut` → `timeout`

### Wait Action
- `timeout` or `timeOut` or `duration` → `duration`
- `timeoutType` or `type` → `mode`
- `timeoutMin` or `min_duration` → `min_duration`
- `timeoutMax` or `max_duration` → `max_duration`

### Scroll Action
- `position: "bottom"` → `depth: 100, position: "Bottom"`
- `position: "top"` → `depth: 0, position: "Top"`
- `type` → `scroll_type`
- `distance` → `depth`

## Usage Examples

### Example 1: Load Script from File
1. Click **Load Script** button
2. Select your JSON file (any supported format)
3. Script is automatically normalized and loaded
4. Actions appear in the workflow builder

### Example 2: Paste JSON Directly
1. Open the **JSON Editor** tab
2. Paste your JSON (any supported format)
3. Script is automatically normalized
4. Actions appear in the workflow builder

### Example 3: Use the Provided Example
The script from the problem statement:
```json
[
  {
    "type": "newPage",
    "config": {}
  },
  {
    "type": "gotoUrl",
    "config": {
      "url": "https://zw.inatboxapk.biz/",
      "timeout": 30000
    }
  },
  {
    "type": "waitTime",
    "config": {
      "timeoutType": "fixedValue",
      "timeout": 30000
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
```

Will be automatically normalized to:
```json
{
  "name": "Loaded Script",
  "description": "Script loaded from JSON",
  "steps": [
    {
      "type": "newPage"
    },
    {
      "type": "navigate",
      "url": "https://zw.inatboxapk.biz/",
      "timeout": 30000
    },
    {
      "type": "wait",
      "duration": 30000,
      "min_duration": 30000,
      "max_duration": 30000,
      "mode": "Fixed"
    },
    {
      "type": "scroll",
      "depth": 100,
      "position": "Bottom",
      "scroll_type": "Smooth"
    }
  ]
}
```

And will appear in the workflow builder as:
1. **New Tab**
2. **Access Website** (https://zw.inatboxapk.biz/)
3. **Time** (30000ms)
4. **Scroll** (to Bottom)

## Benefits

✅ **Universal Compatibility**: Load scripts from any source
✅ **Automatic Normalization**: No manual editing required
✅ **Visual Builder Sync**: Actions automatically appear in workflow
✅ **Execution Ready**: All normalized scripts work with RPA mode
✅ **Backward Compatible**: Existing scripts continue to work

## Technical Details

### Normalization Process
1. **Load JSON**: Parse the JSON file or text
2. **Detect Format**: Identify array vs object format
3. **Normalize Types**: Convert action type names to internal format
4. **Flatten Config**: Extract config objects to step level
5. **Map Properties**: Convert property names to internal format
6. **Sync to Visual**: Update workflow builder with actions

### When Normalization Happens
- When loading a script from file
- When pasting JSON into the editor
- When starting RPA mode execution

### Preserved Properties
All properties in your original JSON are preserved, even if not explicitly mapped. This ensures no data loss during normalization.

## Troubleshooting

### Script doesn't load?
- Verify JSON syntax is valid
- Check that action types are supported
- Ensure required properties are present (e.g., url for navigate)

### Actions don't appear in workflow?
- Check JSON editor for normalized format
- Verify no JSON syntax errors
- Look for error messages in the dialog

### Script won't execute?
- Verify all steps have required properties
- Check that URLs are valid
- Ensure timeout values are reasonable

## Support

For issues or questions, please refer to:
- `test_normalization_standalone.py` - Unit tests for normalization
- `test_rpa_integration.py` - Integration tests
- `QUICK_REFERENCE_NEW_RPA_ACTIONS.md` - Full action reference
