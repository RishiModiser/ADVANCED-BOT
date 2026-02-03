# Quick Reference: New RPA Actions

## Overview
8 new actions have been added to the RPA Action Toolbar to enhance automation capabilities.

## New Actions Quick Reference

### 🔄 Refresh Webpage
**Purpose**: Reload the current page  
**Type**: `refresh`  
**Configuration**: None  
**Example**:
```json
{"type": "refresh"}
```
**Note**: Automatically handles consent popups after refresh

---

### 🔀 Close Tab
**Purpose**: Close the current browser tab  
**Type**: `closeTab`  
**Configuration**: None  
**Example**:
```json
{"type": "closeTab"}
```

---

### 🔍 Statement If
**Purpose**: Conditional execution based on element visibility  
**Type**: `if`  
**Configuration**:
- `selector` (required): CSS selector to check
- `condition` (optional): Condition expression

**Example**:
```json
{
  "type": "if",
  "selector": ".cookie-banner",
  "condition": "element.is_visible()"
}
```

---

### 🔁 For Loop Elements
**Purpose**: Iterate over elements matching a selector  
**Type**: `forLoopElements`  
**Configuration**:
- `selector` (required): CSS selector for elements
- `max_items` (optional): Maximum items to process (default: 10)

**Example**:
```json
{
  "type": "forLoopElements",
  "selector": "a.product-link",
  "max_items": 5
}
```

---

### 🔢 For Loop Times
**Purpose**: Execute steps a fixed number of times  
**Type**: `forLoopTimes`  
**Configuration**:
- `iterations` (required): Number of times to loop (default: 5)

**Example**:
```json
{
  "type": "forLoopTimes",
  "iterations": 10
}
```

---

### ♾️ While Loop
**Purpose**: Execute steps while a condition is true  
**Type**: `while`  
**Configuration**:
- `condition` (required): Loop condition
- `max_iterations` (optional): Safety limit (default: 10)

**Example**:
```json
{
  "type": "while",
  "condition": "element.is_visible()",
  "max_iterations": 20
}
```

---

### ⛔ Exit Loop
**Purpose**: Break out of current loop  
**Type**: `break`  
**Configuration**: None  
**Example**:
```json
{"type": "break"}
```

---

### 🚪 Quit Browser
**Purpose**: Close entire browser context and terminate script  
**Type**: `quitBrowser`  
**Configuration**: None  
**Example**:
```json
{"type": "quitBrowser"}
```

---

## Complete Example Script

```json
{
  "name": "Advanced Automation",
  "description": "Uses multiple new actions",
  "steps": [
    {
      "type": "newPage",
      "comment": "Open new tab"
    },
    {
      "type": "navigate",
      "url": "https://example.com"
    },
    {
      "type": "wait",
      "duration": 2000
    },
    {
      "type": "if",
      "selector": ".popup",
      "comment": "Check if popup exists"
    },
    {
      "type": "refresh",
      "comment": "Refresh the page"
    },
    {
      "type": "forLoopTimes",
      "iterations": 3,
      "comment": "Repeat 3 times"
    },
    {
      "type": "scroll",
      "depth": 50
    },
    {
      "type": "forLoopElements",
      "selector": "a",
      "max_items": 5,
      "comment": "Process first 5 links"
    },
    {
      "type": "closeTab",
      "comment": "Close current tab"
    }
  ]
}
```

---

## Tips

1. **Consent Handling**: Enable the "Auto-handle Cookie Banners" checkbox in settings for automatic popup handling
2. **Loop Safety**: All loops have maximum iteration limits to prevent infinite loops
3. **Error Handling**: Scripts continue even if individual steps fail
4. **Testing**: Test scripts with small iteration counts first
5. **Break Statement**: Use `break` action to exit loops early if needed

---

## Using in Visual Builder

1. Open **RPA Script Creator** tab
2. Drag actions from **Action Toolbox** to **Workflow Steps**
3. Click on a step to configure it in **Step Configuration** panel
4. Set required parameters (selectors, iterations, etc.)
5. Click **Start Automation** to execute

---

## Using in JSON Editor

1. Open **RPA Script Creator** tab
2. Switch to **JSON Editor** tab
3. Write or paste your JSON script
4. Script automatically validates
5. Switch back to **Visual Builder** to see steps
6. Click **Start Automation** to execute

---

## Troubleshooting

**Q: Loop doesn't execute nested steps?**  
A: The current implementation logs loop structure. Nested step execution is a future enhancement.

**Q: Consent popups still appearing?**  
A: Ensure "Auto-handle Cookie Banners" checkbox is enabled in Traffic Behaviour settings.

**Q: Script stops at "if" statement?**  
A: The "if" action currently checks conditions but doesn't execute nested steps yet.

**Q: Browser quits unexpectedly?**  
A: Check if you have a `quitBrowser` action in your script - it terminates execution immediately.

---

For detailed documentation, see: `RPA_ENHANCEMENTS_DOCUMENTATION.md`
